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
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.utils import shuffle

class ModelSearcher:
    """
    This class acts as an interface for performing bayesian optimization on
    a specified model, or several models.
    """

    def __init__(self) -> None:
        """
        Initializes models and grids for grid search.
        """

        self.available_models = {
            'Support Vector Machine': SGDClassifier,
            'Random Forest'         : RandomForestClassifier,
            'QuadraticSVC'          : SGDClassifier,
        }

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

        param_dict = {'n_jobs': 1}

        # Add early stopping for SGD algorithms
        if 'SVC' in self.current_model or 'SVR' in self.current_model:
            param_dict['early_stopping'] = True

        # Construct parameter dict for model
        for param, value in zip(self.grids[self.current_model], params[0]):
            cast = self.param_types[param['name']]
            param_dict[param['name']] = cast(value)

        model = self.available_models[self.current_model](**param_dict)

        cv = cross_validate(
            estimator=model,
            X=self.X,
            y=self.y,
            scoring=['f1', 'accuracy', 'roc_auc'],
            cv=min(5, len(self.y)),
            return_estimator=True)

        if cv['test_accuracy'].mean() > self.results[self.current_model]['acc']:

            self.results[self.current_model]['acc'] = cv['test_accuracy'].mean()
            self.results[self.current_model]['roc'] = cv['test_roc_auc'].mean()
            self.results[self.current_model]['f1'] = cv['test_f1'].mean()

            if 'early_stopping' in param_dict:
                del param_dict['early_stopping']
            del param_dict['n_jobs']

            self.results[self.current_model]['params'] = str(param_dict)
            self.results[self.current_model]['fit_time'] = cv['fit_time'].mean()
            self.results[self.current_model]['score_time'] = cv['score_time'].mean()

            model_bytes = sys.getsizeof(pickle.dumps(cv['estimator'][0]))
            self.results[self.current_model]['model_size'] = model_bytes // 1000

            preds = cv['estimator'][0].predict(self.X)
            confusion = confusion_matrix(list(self.y), preds, list(set(self.y)))
            confusion = [[val for val in row] for row in confusion]
            self.results[self.current_model]['confusion'] = confusion


        if self.current_model == 'Random Forest':
            feature_importances = []
            for estimator in cv['estimator']:
                feature_importances.append(estimator.feature_importances_)
            self.feature_importances = np.array(feature_importances).mean(axis=0)

        return 1 - cv['test_accuracy'].mean()


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

        self.param_types = {
            'alpha': float,
            'max_depth': int,
            'min_samples_split': int,
            'n_estimators': int,
            'max_iter': int,
            'n_neighbors': int
        }

        self.grids = {
            'Support Vector Machine': [
                {
                    'name'  : 'alpha',
                    'type'  : 'continuous',
                    'domain': (1e-6, 1e-2),
                },
                {
                    'name'  : 'max_iter',
                    'type'  : 'discrete',
                    'domain': (200,),
                }
            ],
            'Random Forest': [
                {
                    'name'  : 'max_depth',
                    'type'  : 'discrete',
                    'domain': (5, max(10, num_features // 40)),
                },
                {
                    'name'  : 'min_samples_split',
                    'type'  : 'discrete',
                    'domain': (2, 8, 32),
                },
                {
                    'name'  : 'n_estimators',
                    'type'  : 'continuous',
                    'domain': (10, max(20, num_features // 20)),
                }
            ],
        }

        for model_name in ('Support Vector Machine', 'Random Forest'):

            self.current_model = model_name
            print(self.current_model)

            opt = BayesianOptimization(
                f=self.perform_cv,
                domain=self.grids[self.current_model])

            opt.run_optimization(max_iter=max_iter)
