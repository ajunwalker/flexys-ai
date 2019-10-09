# System imports
from collections import defaultdict
import pickle
import sys

# Third party imports
import numpy as np
from GPyOpt.methods import BayesianOptimization
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import SGDClassifier, SGDRegressor
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

# Local imports
from .configs import classifier_config, regressor_config, param_types

class ModelSearcher:
    """
    This class acts as an interface for performing bayesian optimization on
    a specified model, or several models.
    """

    def __init__(self, output_type: str) -> None:
        """
        Initializes models and grids for grid search.

        Args:
            output_type: classification or regression.
        """

        self.available_classifiers = {
            'Support Vector Machine': SGDClassifier,
            'Random Forest'         : RandomForestClassifier,
        }

        self.available_regressors = {
            'Support Vector Machine': SGDRegressor,
            'Random Forest'         : RandomForestRegressor,
        }

        if output_type == 'classification':
            self.available_models = self.available_classifiers
            self.grids = classifier_config
            self.scoring = ['f1_micro', 'accuracy']
        else:
            self.available_models = self.available_regressors
            self.grids = regressor_config
            self.scoring = ['explained_variance', 'r2',
                            'neg_mean_absolute_error']

        self.output_type = output_type
        self.param_types = param_types
        self.results = defaultdict(lambda: defaultdict(int))
        self.feature_importances = []
        self.tried = {}


    def perform_cv(self, params: list):
        """
        Fits model with paramaters selected by bayesian optimization.

        Args:
            param: Parameters for model.
        """

        if str(params) in self.tried:
            return self.tried[str(params)]

        param_dict = {}

        # Add early stopping for SGD algorithms
        if self.current_model == 'Support Vector Machine':
            features = StandardScaler().fit_transform(self.X)
            param_dict['early_stopping'] = True
        else:
            features = self.X

        # Construct parameter dict for model
        for param, value in zip(self.grids[self.current_model], params[0]):
            cast = self.param_types[param['name']]
            param_dict[param['name']] = cast(value)

        model = self.available_models[self.current_model](**param_dict)

        cv = cross_validate(
            estimator=model,
            X=features,
            y=self.y,
            scoring=self.scoring,
            cv=min(5, len(self.y)),
            return_estimator=True)

        curr_model = self.current_model
        improvement = False

        if self.output_type == 'classification':
            mean_score = cv['test_accuracy'].mean()
            if mean_score > self.results[curr_model]['acc']:
                improvement = True
                self.results[curr_model]['acc'] = cv['test_accuracy'].mean()
                #self.results[curr_model]['roc'] = cv['test_roc_auc'].mean()
                self.results[curr_model]['f1'] = cv['test_f1_micro'].mean()

                # Save confusion matrix
                preds = cv['estimator'][0].predict(features)
                confusion = confusion_matrix(list(self.y), preds, list(set(self.y)))
                confusion = [[val for val in row] for row in confusion]
                self.results[curr_model]['confusion'] = confusion

        else:
            mean_score = cv['test_neg_mean_absolute_error'].mean()
            if (self.results[curr_model]["params"] == 0) or \
               (abs(mean_score) < self.results[curr_model]['mae']):
                improvement = True
                exp_var = 'explained_variance'
                mae = 'neg_mean_absolute_error'
                self.results[curr_model][exp_var] = cv['test_' + exp_var].mean()
                self.results[curr_model]['r2'] = cv['test_r2'].mean()
                self.results[curr_model]['mae'] = abs(cv['test_' + mae].mean())

                # Save error pairs
                preds = cv['estimator'][0].predict(features)
                errors = []
                for i in range(min(1000, len(self.y))):
                    errors.append([self.y[i], preds[i]])
                self.results[curr_model]['errors'] = errors

        if improvement is True:
            if 'early_stopping' in param_dict:
                del param_dict['early_stopping']
            if 'n_jobs' in param_dict:
                del param_dict['n_jobs']

            self.results[curr_model]['params'] = str(param_dict)
            self.results[curr_model]['fit_time'] = cv['fit_time'].mean()
            self.results[curr_model]['score_time'] = cv['score_time'].mean()

            model_bytes = sys.getsizeof(pickle.dumps(cv['estimator'][0]))
            self.results[curr_model]['model_size'] = model_bytes // 1000


        if self.current_model == 'Random Forest':
            feature_importances = []
            for estimator in cv['estimator']:
                feature_importances.append(estimator.feature_importances_)
            mean_importances = np.array(feature_importances).mean(axis=0)
            self.feature_importances = mean_importances

        if self.output_type == 'classification':
            return 1 - cv['test_accuracy'].mean()
        else:
            return 1 - cv['test_neg_mean_absolute_error'].mean()


    def fit(self, X: list, y: list, n_jobs: int, max_iter: int = 50) -> None:
        """
        Perform bayesian optimization on hyperparameter space.

        Args:
            x : Array containing training input data.
            y : Array containing data labels.
            n_jobs: Number of threads to run the algorithms.
            max_iter : Number of iterations to perform bayesian optimization.
        """

        self.X, self.y = shuffle(X, y)
        self.n_jobs = n_jobs

        num_features = X.shape[1]

        for model_name in self.available_models:

            self.current_model = model_name
            print(self.current_model)

            opt = BayesianOptimization(
                f=self.perform_cv,
                domain=self.grids[self.current_model])

            opt.run_optimization(max_iter=max_iter)
