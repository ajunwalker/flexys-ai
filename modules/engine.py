import pandas as pd
import uuid
from threading import Thread

from django.db import models
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


    def save_columns(self):
        """
        Analyzes each column in the data frame, and saves the meta data
        in the DB.
        """
        target_column = self.df.columns[-1]
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
                    target=(col == target_column),
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
                    target=(col == target_column),
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
        searcher = ModelSearcher()
        searcher.fit(self.X, self.y, 1)

        for model_name, scores in searcher.results.items():
            new_model = Model(
                name=model_name,
                accuracy=round(scores['acc'], 3),
                roc=round(scores['roc'], 3),
                f1=round(scores['f1'], 3),
                fit_time=round(scores['fit_time'], 3),
                score_time=round(scores['score_time'], 3),
                model_size=round(scores['model_size'], 3),
                params=scores['params'],
                confusion=scores['confusion'],
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
        self.target_column = self.df.columns[-1]
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
        encoder = LabelEncoder()
        self.y = encoder.fit_transform(self.y)
        self.project.columns = list(encoder.classes_)
        self.project.save()


    def run_engine(self):
        """
        Entry point for analysis and model search.
        """
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
