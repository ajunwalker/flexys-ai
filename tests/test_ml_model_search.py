import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from modules.ml_model_search import ModelSearcher

iris_url = 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv'

def test_classification():
    model_searcher = ModelSearcher('classification')
    df = pd.read_csv(iris_url)
    target_column = 'species'
    X, y = df.drop(target_column, axis=1), df[target_column]
    y = LabelEncoder().fit_transform(y)
    model_searcher.fit(X, y, 1)


def test_regression():
    model_searcher = ModelSearcher('regression')
    df = pd.read_csv(iris_url)
    df['species'] = LabelEncoder().fit_transform(df['species'])
    target_column = 'sepal_length'
    X, y = df.drop(target_column, axis=1), df[target_column]
    model_searcher.fit(X, y, 1)
