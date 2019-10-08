import numpy as np
import pandas as pd
import uuid
from threading import Thread

from django.db import models
from scipy import stats
from sklearn.preprocessing import Imputer, LabelEncoder

from main.models import Project, Column, Model
from .ml_model_search import ModelSearcher

class AnalysisEngine:

    def __init__(self):
        """
        Creates and saves a new project model to DB.
        """
        self.id = uuid.uuid4()
        self.project = Project(id=self.id)
        self.project.save()


    def infer_target_type(self) -> None:
        """
        Attempts to infer the target columns data type.
        """
        self.target_column = self.df.columns[-1]
        if self.df[self.target_column].dtype == 'object':
            self.output = 'classification'
        else:
            column_arr = self.df[self.target_column]
            column_arr = column_arr.dropna()
            points = 0

            # Check if column only contains ints
            if np.array_equal(column_arr, column_arr.astype(int)):
                points += 0.7

            # Check if column only contains floats
            elif np.array_equal(column_arr, column_arr.astype(float)):
                points += 0.8

            # Check if column is normally distributed
            k2, p = stats.normaltest(column_arr)
            if p >= 0.1:
                points += 0.3

            # Check if number of unique values is low
            unique_values = set(column_arr)
            if len(unique_values) > len(column_arr) * 0.1:
                points += 0.3

            self.output = 'regression' if points > 1.0 else 'classification'


    def save_columns(self):
        """
        Analyzes each column in the data frame, and saves the meta data
        in the DB.
        """
        self.columns = []

        for col in self.df.columns:
            null_count = self.df[col].isna().sum()
            fill_rate = round((len(self.df) - null_count) / len(self.df), 2)

            # Numerical columns
            if self.df[col].dtype in ('int', 'float'):
                new_column = Column(
                    name=col,
                    type='numerical',
                    filled=fill_rate,
                    min=round(self.df[col].min(), 2),
                    mean=round(self.df[col].mean(), 2),
                    median=round(self.df[col].median(), 2),
                    max=round(self.df[col].max(), 2),
                    unique=0,
                    target=(col == self.target_column),
                    project=self.project
                )
                new_column.save()

            # Categorical columns
            else:
                new_column = Column(
                    name=col,
                    type='categorical',
                    filled=fill_rate,
                    min=0,
                    mean=0,
                    median=0,
                    max=0,
                    unique=self.df[col].nunique(),
                    target=(col == self.target_column),
                    project=self.project
                )
                new_column.save()
            self.columns.append(new_column)

        # Mark as complete
        self.project.analytics_complete = True
        self.project.save()


    def run_models(self) -> None:
        """
        Performs model search, and saves the results of each machine learning
        model.
        """
        searcher = ModelSearcher(self.output)
        searcher.fit(self.X, self.y, 1)

        for model_name, scores in searcher.results.items():
            new_model = Model(
                name=model_name,
                accuracy=round(scores['acc'], 3),
                roc=round(scores['roc'], 3),
                f1=round(scores['f1'], 3),
                explained_variance=round(scores['explained_variance'], 3),
                r2=round(scores['r2'], 3),
                mae=round(scores['mae'], 3),
                fit_time=round(scores['fit_time'], 3),
                score_time=round(scores['score_time'], 3),
                model_size=round(scores['model_size'], 3),
                params=scores['params'],
                confusion=scores['confusion'],
                errors=scores['errors'],
                project=self.project
            )
            new_model.save()

        # Save feature importances
        importances = searcher.feature_importances
        for column, importance in zip(self.columns, importances):
            column.importance = round(importance, 3)
            column.save()

        # Mark as complete
        self.project.models_complete = True
        self.project.save()


    def preprocess(self) -> None:
        """
        Imputes missing values from data set, and converts strings to numbers.
        """
        self.X = self.df.drop(self.target_column, axis=1)
        self.y = self.df[self.target_column]

        # Preprocess features
        for col in self.X.columns:
            if self.X[col].dtype in ('int', 'float'):
                self.X[col] = self.X[col].fillna(value=self.X[col].mean())
            else:
                self.X[col] = self.X[col].fillna('None')
                self.X[col] = LabelEncoder().fit_transform(self.X[col])

        # Preprocess targets
        if self.output == 'classification':
            encoder = LabelEncoder()
            self.y = encoder.fit_transform(self.y)
            self.project.columns = list(encoder.classes_)
            self.project.save()
        else:
            self.y = self.y.fillna(value=self.y.mean())


    def run_engine(self) -> None:
        """
        Entry point for analysis and model search.
        """
        self.infer_target_type()
        self.save_columns()
        self.preprocess()
        self.run_models()


    def run(self, file_path: str) -> None:
        """
        Opens CSV file and runs separate thread to start the data processing.

        Args:
            file_path: Path to CSV file.
        """
        self.df = pd.read_csv(file_path)
        Thread(target=self.run_engine).start()
