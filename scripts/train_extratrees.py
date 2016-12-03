from collections import Counter
import glob
import os
import random

import numpy as np

import matplotlib.pyplot as plt

from skimage import img_as_ubyte
from skimage.color import rgb2grey
from skimage.exposure import equalize_adapthist
from skimage.io import imread
from skimage.io import imsave

from sklearn.dummy import DummyClassifier
from sklearn.metrics import auc
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.utils import shuffle


import warnings
#warnings.filterwarnings('error')

def load_images(input_dir="/tmp/mapswipe/project-1", n_images=2000, seed=1):
    """Loads `n_images` for each class."""
    class_map = {1: "1", 0: "5"}
    output_dir = "/Users/thead/git/dreamview/data/"

    X_ = []
    y_ = []
    for new_klass in class_map:
        images = []
        for klass in class_map[new_klass]:
            for img in glob.glob(input_dir + "/%s/*/*/*/aerial.jpeg" % klass):
                if os.stat(img).st_size > 0:
                    images.append(img)

        images = shuffle(images, random_state=seed+42+new_klass)
        images = images[:n_images]
        X_ += images
        y_ += [new_klass] * len(images)

    # XXX deduce array size from an actual image
    X = np.zeros((2*n_images, 256*256), dtype=np.ubyte)
    y = np.zeros(2*n_images, dtype=np.int)

    for n, (img_path, klass) in enumerate(zip(X_, y_)):
        # the order of these OPs has been chosen on purpose, don't mess
        # without checking what happens
        img = imread(img_path)
        img = equalize_adapthist(img)
        img = rgb2grey(img)
        img = img_as_ubyte(img)

        if not n % 10:
            fname = os.path.split(img_path)[:-1]
            fname = os.path.join(*fname, "aerial-processed.jpeg")
            imsave(fname, img)

        X[n,:] = img.ravel()
        y[n] = klass

    return X, y


def run():
    X, y = load_images()

    X_train, X_val, y_train, y_val = train_test_split(X, y,
                                                      train_size=0.8,
                                                      stratify=y,
                                                      random_state=34)

    print(Counter(y), Counter(y_train), Counter(y_val))
    for n in (10, 20, 50, 100):
        print("n_estimators=", n)
        et = ExtraTreesClassifier(n_estimators=n,
                                  bootstrap=True,
                                  oob_score=True,
                                  n_jobs=5, random_state=2)
        et.fit(X_train, y_train)
        print("OOB score:", et.oob_score_)
        print("Train score:", et.score(X_train, y_train))
        print("Validation score:", et.score(X_val, y_val))

        y_score = et.predict_proba(X_val)[:, 1]

        fpr, tpr, _ = roc_curve(y_val, y_score)

        print("AUC:", auc(fpr, tpr))

        plt.figure()
        lw = 2
        plt.plot(fpr, tpr, color='darkorange',
                 lw=lw, label='ROC curve')
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        print("="*80)

    plt.show()


if __name__ == "__main__":
    run()
