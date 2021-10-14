import pandas as pd
from pathlib import Path
from pickle import load

from sklearn.compose import TransformedTargetRegressor
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import LabelBinarizer, LabelEncoder, Normalizer, PowerTransformer
from sklearn.decomposition import PCA

from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report
from sklearn.tree import DecisionTreeClassifier

from sklearn.pipeline import Pipeline, FeatureUnion
from skopt import BayesSearchCV

from src.augmentation.augmentation import AugmentDocuments
from src.preprocessing.xtract_vectorizer import WindowTransformerList, BoxPositionGetter, BagOfWordInLine
from src.preprocessing.word_transformers import ContainsDigit, IsPrenom, IsNom, IsDate
import numpy as np


if __name__ == "__main__":
    with open('./model/fdp_data_preprocessing_big_augment', 'rb') as f1:
        data = load(f1)

    pipe_feature = data['pipe_feature']
    X_train, y_train, X_test, y_test = data['X_train'], data['y_train'], data['X_test'], data['y_test']

    df = pd.DataFrame(X_train, columns=pipe_feature.get_feature_names())

    pipe_feature_post = Pipeline([
        ('power_transformer', PowerTransformer()),
    ])

    X_train = pipe_feature_post.fit_transform(X_train)
    X_test = pipe_feature_post.transform(X_test)


    # pipe = RandomForestClassifier(n_estimators= 50, verbose=2)
    # pipe.fit(X_train, y_train)
    #
    # model = SelectFromModel(pipe, max_features=100, prefit=True)
    # X_train = model.transform(X_train)
    # X_test = model.transform(X_test)

    pipe = BayesSearchCV(
        HistGradientBoostingClassifier(verbose=0),
        {
            'max_leaf_nodes': (10, 60),
            'learning_rate': (0.1, 1., 'uniform'),
            'max_depth': (1, 100),  # integer valued parameter
        },
        n_jobs=-1,
        n_iter=64,
        cv=3,
        verbose=1,
        scoring='f1_macro'
    )

    pipe.fit(X_train, y_train)

    print("val. score: %s" % pipe.best_score_)

    # pipe = HistGradientBoostingClassifier(verbose=2)
    # pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)

    print(classification_report(y_test, y_pred))

    from pickle import dump
    with open('./model/model_test_pipeline_fdp', 'wb') as f1:
        dump(pipe_feature, f1)
        dump(pipe, f1)

#
# OrderedDict([('learning_rate', 0.1),
#              ('max_depth', 14),
#              ('max_leaf_nodes', 10)])
#
# OrderedDict([('learning_rate', 0.1),
#              ('max_depth', 100),
#              ('max_leaf_nodes', 60)])


