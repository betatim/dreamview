import csv
import os


def run(label_fname, input_image_dir):
    os.makedirs(input_image_dir + "/class_0", exist_ok=True)
    os.makedirs(input_image_dir + "/class_1", exist_ok=True)

    with open(label_fname) as labels_csv:
        for score, fname in csv.reader(labels_csv):
            fname = fname.split(".")[0] + ".jpeg"
            if float(score) > 0.03:
                os.symlink(input_image_dir + fname,
                           input_image_dir + "/class_1")

            else:
                os.symlink(input_image_dir + fname,
                           input_image_dir + "/class_0")


if __name__ == "__main__":
    import sys
    run(sys.argv[1], sys.argv[2])
