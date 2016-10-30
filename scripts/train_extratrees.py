from collections import Counter
import glob
import os
import random

import numpy as np

from skimage.io import imread

from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.utils import shuffle


def load_images(input_dir="/tmp/mapswipe/project-1", n_images=2000, seed=1):
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

        X_ += images
        y_ += [new_klass] * len(images)

    X_, y_ = shuffle(X_, y_, random_state=seed, n_samples=n_images)

    # XXX deduce array size from an actual image
    X = np.zeros((n_images, 256*256), dtype=np.float)
    y = np.zeros(n_images, dtype=np.int)

    for n, (img_path, klass) in enumerate(zip(X_, y_)):
        img = imread(img_path, as_grey=True)
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
    et = ExtraTreesClassifier(n_estimators=300,
                              bootstrap=True,
                              oob_score=True,
                              n_jobs=4, random_state=2)
    et.fit(X_train, y_train)
    print("OOB score:", et.oob_score_)
    print("Validation score:", et.score(X_val, y_val))


if __name__ == "__main__":
    run()
