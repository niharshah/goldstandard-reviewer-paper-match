# Predictions of the trivial algorithm (constant for each paper-reviewer pair)

# Example usage:
# python trivial_algorithm.py --OR_dir ../evaluation_datasets --destination ../predictions --OR_name d_20_1 --name test_constant

import argparse
import json
import os


def create_dummy_prediction(revs, paps):
    """Create dummy similarities: predict the same score for each paper-reviewer pair.

    Args:
        revs: path to a folder with reviewers' profiles
        paps: dict with papers' profiles

    Returns:
        predicted similarities
    """

    revs = [x.split('.')[0].strip('~') for x in os.listdir(revs)]
    res = {}

    for reviewer in revs:

        res[reviewer] = {paper: 1 for paper in paps}

    return res


def parse_args(argv=None):

    parse = argparse.ArgumentParser()
    parse.add_argument('--OR_dir', type=str, help='Path to the OR datasets folder')
    parse.add_argument('--OR_name', type=str, help='Name of the OR dataset')
    parse.add_argument('--destination', type=str, help='Output dir')
    parse.add_argument('--name', type=str, help='Name of the prediction file')

    return parse.parse_args(argv)


if __name__ == '__main__':

    args = parse_args()

    reviewers = os.path.join(args.OR_dir, args.OR_name, 'archives')

    with open(os.path.join(args.OR_dir, args.OR_name, 'submissions.json'), 'r') as handler:
        papers = json.load(handler)

    predictions = create_dummy_prediction(reviewers, papers)

    with open(os.path.join(args.destination, args.name + '_' + args.OR_name + '_ta' + '.json'), 'w') as handler:
        json.dump(predictions, handler)