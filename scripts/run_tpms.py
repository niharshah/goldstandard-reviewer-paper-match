# A script to run the TPMS algorithm on all datasets in the target directory.

# Example usage:
# python run_tpms.py --OR_dir ../evaluation_datasets --pred_dir ../predictions
# This will evaluate the TPMS algorithm on all datasets in the ../evaluation_datasets
# directory and store the predicted similarities in the ../predictions directory
#
# The script evaluates TPMS in all regimes supported by the dataset. Note that
# -- datasets of the form "d_{x}_{y}" support 'title' and 'title+abstract' regimes
# -- datasets of the form "d_full_{x}_{y}" support all regimes: 'title', 'title+abstract', 'full text'
# The scripts looks for the 'full' substring in the dataset folder name to choose the regimes

import argparse
import os

tpms_call = "python tpms.py --OR_dir %s --destination %s --regime %s --OR_name %s --name %s"

def parse_args(argv=None):
    parse = argparse.ArgumentParser()

    parse.add_argument('--OR_dir', type=str, help='Path to the OR datasets folder')
    parse.add_argument('--pred_dir', type=str, help='Output dir for predictions')

    return parse.parse_args(argv)


def predict(args):
    """ Run TPMS algorithm

    :param args:
        - args.OR_dir: path to the folder where datasets in the OR format are stored
        - args.pred_dir: path to the folder where predictions will be stored

    Note: Predictions will not be overwritten. If the args.pred_dir directory already contains predictions
    for some of the datasets, they won't be changed with new predictions
    """

    already_predicted = set(os.listdir(args.pred_dir))

    # Go through all datasets in the target directory
    for OR_name in os.listdir(args.OR_dir):

        # Skip system files
        if OR_name.startswith('.'):
            continue

        if 'full' in OR_name:
            # 'full' in the dataset names guarantees that all papers have PDFs available so we can run
            # TPMS in the full text regime
            r1 = ['title', 'title+abstract', 'full']
            r2 = ['t', 'ta', 'f']
        else:
            # Otherwise, we only run TPMS in the title and title+abstract regime
            r1 = ['title', 'title+abstract']
            r2 = ['t', 'ta']

        for regime, rgm in zip(r1, r2):

            # Name of the prediction file
            name = f"tpms_{OR_name}_{rgm}"

            if name + '.json' not in already_predicted:
                os.system(tpms_call % (args.OR_dir, args.pred_dir, regime, OR_name, name))


if __name__ == '__main__':
    args = parse_args()
    predict(args)