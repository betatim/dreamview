import os
import shutil


def run(label_fname, input_image_dir):
    os.makedirs(input_image_dir + "/class_0", exist_ok=True)
    os.makedirs(input_image_dir + "/class_1", exist_ok=True)

    with open(label_fname) as labels:
        for label_line in labels:
            score, fname = label_line.split(" ", maxsplit=1)

            # clean filename of extra white space and leading path
            fname = fname.strip()
            fname = fname[6:]
            fname = fname.split(".")[0] + ".jpeg"

            if float(score) > 0.0:
                shutil.copy(input_image_dir + fname,
                            input_image_dir + "/class_1/" + fname)

            else:
                shutil.copy(input_image_dir + fname,
                            input_image_dir + "/class_0/" + fname)


if __name__ == "__main__":
    import sys
    label_fname = sys.argv[1]
    image_dir = sys.argv[2]
    run(label_fname, image_dir)
