import numpy as np
import pandas as pd
import graphviz
import graphviz.backend
from numpy.distutils.system_info import f2py_info
from sklearn import tree
from sklearn.datasets import load_boston, load_iris, load_wine, load_digits, load_breast_cancer, load_diabetes, fetch_mldata
from matplotlib.figure import figaspect
import string
import re
import matplotlib.pyplot as plt
import seaborn as sns
from animl.trees import *
from numbers import Number
import matplotlib.patches as patches
from scipy import stats
from sklearn.neighbors import KernelDensity
import inspect, sys, tempfile

from animl.viz.trees import *

"""
Generate samples into testing/samples dir to compare against future
images as a means of visually checking for errors.

Run with working directory as main animl dir so this code can see animl package
and data paths are set correctly. 
"""

# REGRESSION

def viz_boston(orientation="TD", max_depth=3, random_state=666):
    regr = tree.DecisionTreeRegressor(max_depth=max_depth, random_state=random_state)
    boston = load_boston()

    data = pd.DataFrame(boston.data)
    data.columns = boston.feature_names

    regr = regr.fit(data, boston.target)

    # st = dectreeviz(regr.tree_, data, boston.target)
    st = dtreeviz(regr, data, boston.target, target_name='price',
                  feature_names=data.columns, orientation=orientation,

                  fancy=True)

    return st

def viz_diabetes(orientation="TD", max_depth=3, random_state=666):
    diabetes = load_diabetes()

    regr = tree.DecisionTreeRegressor(max_depth=max_depth, random_state=random_state)
    regr = regr.fit(diabetes.data, diabetes.target)

    st = dtreeviz(regr, diabetes.data, diabetes.target, target_name='disease progression',
                  feature_names=diabetes.feature_names, orientation=orientation,
                  fancy=True)

    return st

def viz_sweets(orientation="TD", max_depth=3, random_state=666):
    sweets = pd.read_csv("testing/data/sweetrs.csv")
    sweets = sweets.sample(n=2000) # just grab 2000 of 17k

    X, y = sweets.drop('rating', axis=1), sweets['rating']

    regr = tree.DecisionTreeRegressor(max_depth=max_depth, random_state=random_state)
    regr = regr.fit(X, y)

    st = dtreeviz(regr, X, y, target_name='rating',
                  feature_names=sweets.columns, orientation=orientation,
                  fancy=True)

    return st

def viz_fires(orientation="TD", max_depth=3, random_state=666):
    fires = pd.read_csv("testing/data/forestfires.csv")
    fires['month'] = fires['month'].astype('category').cat.as_ordered()
    fires['month'] = fires['month'].cat.codes + 1
    fires['day'] = fires['day'].astype('category').cat.as_ordered()
    fires['day'] = fires['day'].cat.codes + 1

    X, y = fires.drop('area', axis=1), fires['area']

    regr = tree.DecisionTreeRegressor(max_depth=max_depth, random_state=random_state)
    regr = regr.fit(X, y)

    st = dtreeviz(regr, X, y, target_name='area',
                  feature_names=fires.columns, orientation=orientation,
                  fancy=True)

    return st


# CLASSIFICATION

def viz_iris(orientation="TD", max_depth=3, random_state=666):
    clf = tree.DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)
    iris = load_iris()

    data = pd.DataFrame(iris.data)
    data.columns = iris.feature_names

    clf = clf.fit(data, iris.target)

    st = dtreeviz(clf, data, iris.target,target_name='variety',
                  feature_names=data.columns, orientation=orientation,
                  class_names=["setosa", "versicolor", "virginica"], # 0,1,2 targets
                  fancy=True)

    return st

def viz_digits(orientation="TD", max_depth=3, random_state=666):
    clf = tree.DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)
    digits = load_digits()

    data = pd.DataFrame(digits.data)
    "8x8 image of integer pixels in the range 0..16."
    data.columns = [f'pixel[{i},{j}]' for i in range(8) for j in range(8)]

    clf = clf.fit(data, digits.target)

    st = dtreeviz(clf, data, digits.target,target_name='number',
                  feature_names=data.columns, orientation=orientation,
                  class_names=[chr(c) for c in range(ord('0'),ord('9')+1)],
                  fancy=True, histtype='bar')
    return st

def viz_wine(orientation="TD", max_depth=3, random_state=666):
    clf = tree.DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)
    wine = load_wine()

    data = pd.DataFrame(wine.data)
    data.columns = wine.feature_names

    clf = clf.fit(data, wine.target)

    st = dtreeviz(clf, data, wine.target,target_name='wine',
                  feature_names=data.columns, orientation=orientation,
                  class_names=list(wine.target_names),
                  fancy=True)
    return st

def viz_breast_cancer(orientation="TD", max_depth=3, random_state=666):
    clf = tree.DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)
    cancer = load_breast_cancer()

    data = pd.DataFrame(cancer.data)
    data.columns = cancer.feature_names

    clf = clf.fit(data, cancer.target)

    st = dtreeviz(clf, data, cancer.target,target_name='cancer',
                  feature_names=data.columns, orientation=orientation,
                  class_names=list(cancer.target_names),
                  fancy=True)
    return st

def viz_knowledge(orientation="TD", max_depth=3, random_state=666):
    # data from https://archive.ics.uci.edu/ml/datasets/User+Knowledge+Modeling
    clf = tree.DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)
    cancer = pd.read_csv("testing/data/knowledge.csv")
    target_names = ['very_low', 'Low', 'Middle', 'High']
    cancer['UNS'] = cancer['UNS'].map({n: i for i, n in enumerate(target_names)})

    X_train, y_train = cancer.drop('UNS', axis=1), cancer['UNS']
    clf = clf.fit(X_train, y_train)

    st = dtreeviz(clf, X_train, y_train, target_name='UNS',
                  feature_names=cancer.columns.values, orientation=orientation,
                  class_names=target_names,
                  fancy=True)
    return st


def save(name, dirname, orientation, max_depth):
    print(f"Process {name} orientation={orientation} max_depth={max_depth}")
    st = f(orientation=orientation, max_depth=max_depth)
    # Gen both pdf/png
    g = graphviz.Source(st, format='pdf') # can't gen svg as it refs files in tmp dir that disappear
    filename = f"{name}-{orientation}-{max_depth}"
    g.render(directory=dirname, filename=filename, view=False, cleanup=True)

    # do it the hard way to set dpi for png
    # g = graphviz.Source(st, format='png')
    # filepath = g.save(filename=f"{filename}.dot", directory=tempfile.gettempdir()) # save dot file
    # # cmd, rendered = graphviz.backend.command('dot', 'png', filepath)
    # cmd = ['dot', '-Gdpi=300', '-Tpng', f'-o{dirname}/{filename}.png', filepath]
    # graphviz.backend.run(cmd, capture_output=True, check=True, quiet=False)
    # That conversion fails to get good image. do this on command line:
    #
    # $ convert -density 300x300 boston-TD-2.pdf foo.png


if __name__ == '__main__':
    all_functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    these_functions = [t for t in all_functions if inspect.getmodule(t[1]) == sys.modules[__name__]]
    viz_funcs = [f[1] for f in these_functions if f[0].startswith('viz_')]

    if len(sys.argv)>1:
        dirname = sys.argv[1]
    else:
        dirname = "."

    print(f"tmp dir is {tempfile.gettempdir()}")
    for f in viz_funcs:
        name = f.__name__[len("viz_"):]
        save(name, dirname, "TD", 2)
        save(name, dirname, "TD", 4)
        save(name, dirname, "LR", 3)