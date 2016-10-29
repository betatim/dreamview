# Create directories linking to the downloaded tiles
#
# data/train/<class>/
# data/validation/<class>/
import os
import glob

import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold



def run(input, class_map=dict(a=["1"], b=["5"])):
    output_dir = "/Users/thead/git/dreamview/data/"

    X_ = []
    y_ = []
    for new_klass in class_map:
        images = []
        for klass in class_map[new_klass]:
            for img in glob.glob(input + "/%s/*/*/*/aerial.jpeg" % klass):
                if os.stat(img).st_size > 0:
                    images.append(img)

        X_ += images
        y_ += [new_klass] * len(images)

    X = np.array(X_)
    y = np.array(y_)
    print(X.shape, y.shape)


    skf = StratifiedKFold(n_splits=6, shuffle=True, random_state=3)
    #skf = KFold(n_splits=2, shuffle=True, random_state=3)
    for n, (train_index, val_index) in enumerate(skf.split(X, y)):
        print("Split", n)
        X_train, X_val = X[train_index], X[val_index]
        y_train, y_val = y[train_index], y[val_index]

        d = os.path.join(output_dir, "split_%i" % n)
        d_train = os.path.join(d, "train")
        d_val = os.path.join(d, "val")
        os.makedirs(d_train, exist_ok=True)
        os.makedirs(d_val, exist_ok=True)
        for klass in class_map:
            os.makedirs(os.path.join(d_train, klass), exist_ok=True)
            os.makedirs(os.path.join(d_val, klass), exist_ok=True)

        for i, (x, klass) in enumerate(zip(X_train, y_train)):
            os.symlink(x, os.path.join(d_train, klass, "%i.jpeg" % i))
        for i, (x, klass) in enumerate(zip(X_val, y_val)):
            os.symlink(x, os.path.join(d_val, klass, "%i.jpeg" % i))


if __name__ == "__main__":
    import sys
    input_dir = sys.argv[1]

    run(input_dir)
