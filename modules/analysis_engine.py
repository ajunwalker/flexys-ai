import pandas as pd
import uuid
from threading import Thread

from sklearn.preprocessing import Imputer, LabelEncoder

from main.models import Project, Column, Model
from .ml_model_search import ModelSearcher


def save_columns(df, project):

    target_column = df.columns[-1]
    columns = []

    for col in df.columns:

        null_count = df[col].isna().sum()
        fill_rate = round((len(df) - null_count) / len(df), 2)

        if df[col].dtype in ('int', 'float'):

            new_column = Column(
                name=col,
                type='numerical',
                filled=fill_rate,
                min=round(df[col].min(), 2),
                mean=round(df[col].mean(), 2),
                median=round(df[col].median(), 2),
                max=round(df[col].max(), 2),
                unique=0,
                target=(col == target_column),
                project=project
            )
            new_column.save()
            columns.append(new_column)

        else:
            new_column = Column(
                name=col,
                type='categorical',
                filled=fill_rate,
                min=0,
                mean=0,
                median=0,
                max=0,
                unique=df[col].nunique(),
                target=(col == target_column),
                project=project
            )
            new_column.save()
            columns.append(new_column)

    project.analytics_complete = True
    project.save()

    return columns


def run_models(X, y, project):

    searcher = ModelSearcher()
    searcher.fit(X, y, 1)

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
            project=project
        )
        new_model.save()

    return searcher.feature_importances


def preprocess(df):

    target_column = df.columns[-1]
    X, y = df.drop(target_column, axis=1), df[target_column]

    for col in X.columns:
        if X[col].dtype in ('int', 'float'):
            X[col] = X[col].fillna(value=X[col].mean())
        else:
            X[col] = X[col].fillna('None')
            X[col] = LabelEncoder().fit_transform(X[col])

    return X, y


def run_engine(new_project, df):
    columns = save_columns(df, new_project)
    X, y = preprocess(df)
    encoder = LabelEncoder()
    y = encoder.fit_transform(y)
    new_project.columns = list(encoder.classes_)
    new_project.save()

    importances = run_models(X, y, new_project)

    for column, importance in zip(columns, importances):
        column.importance = round(importance, 3)
        column.save()

    new_project.models_complete = True
    new_project.save()


def run(new_project, file_path):

    # Open CSV
    df = pd.read_csv(file_path)
    thread = Thread(target=run_engine, args=(new_project, df))
    thread.start()


def create_project():

    # Create new project
    id = uuid.uuid4()
    new_project = Project(id=id)
    new_project.save()

    return new_project
