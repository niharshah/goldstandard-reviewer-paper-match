# Example usage: python evaluation_script.py --dataset ./data/evaluations.csv --prediction_dir ./predictions --algo tpms

import os
import json
import numpy as np
import pandas as pd

import argparse
import scripts.helpers as hlp
from scripts.scoring import compute_main_metric


def score_performance(pred_file, references, valid_papers, valid_reviewers, bootstraps):
    """Compute the main metric for predicted similarity together with bootstrapped values for confidence intervals

    :param pred_file: Name of the file where predicted similarities are stored (file must be in the PRED_PATH dir)
    :param references: Ground truth values of expertise
    :param valid_papers: Papers to include in evaluation
    :param valid_reviewers: Reviewers to include in evaluation
    :param bootstraps: Subsampled reviewer pools for bootstrap computations
    :return: Score of the predictions + data to compute confidence intervals (if `bootstraps` is not None)
    """

    with open(pred_file, 'r') as handler:
        predictions = json.load(handler)

    score = compute_main_metric(predictions, references, valid_papers, valid_reviewers)
    variations = [compute_main_metric(predictions, references, valid_papers, vr) for vr in bootstraps]

    return score, variations

def parse_args(argv=None):
    parse = argparse.ArgumentParser()
    parse.add_argument('--dataset', type=str, help='Path to the dataset csv file')
    parse.add_argument('--prediction_dir', type=str, help='Directory where predictions are stored')
    parse.add_argument('--algo', type=str, help='Name of the algorithm under evaluation')

    return parse.parse_args(argv)


if __name__ == '__main__':

    args = parse_args()

    df = pd.read_csv(args.dataset, sep='\t')
    references, _ = hlp.to_dicts(df)

    all_reviewers = list(references.keys())

    all_papers = set()
    for rev in references:
        all_papers = all_papers.union(references[rev].keys())

    # Prepare reviewer pools for computing Confidence Intervals (n=1,000 iterations)
    bootstraps = [np.random.choice(all_reviewers, len(all_reviewers), replace=True) for x in range(1000)]

    # Check that prediction files are available
    available_predictions = set(os.listdir(args.prediction_dir))

    for iteration in range(1, 11):
        f_name = f"{args.algo}_d_20_{iteration}_ta.json"
        if f_name not in available_predictions:
            raise ValueError(f"Predicted similarities are missing: {f_name}")

    results = {'pointwise': [], 'variations': []}

    for iteration in range(1, 11):
        f_name = f"{args.algo}_d_20_{iteration}_ta.json"
        f_path = os.path.join(args.prediction_dir, f_name)
        tmp = score_performance(f_path, references, all_papers, all_reviewers, bootstraps)

        results['pointwise'].append(tmp[0])
        results['variations'].append(tmp[1])

    # Get pointwise estimate of performance
    point = round(np.mean(results['pointwise']), 2)

    # Get 95% confidence interval
    boot = np.matrix(results['variations']).mean(axis=0).tolist()[0]
    ci = f"[{round(np.percentile(boot, 2.5), 2)}; {round(np.percentile(boot, 97.5), 2)}]"

    print(f"Pointwise estimate of performance: {point}")
    print(f"95% confidence interval: {ci}")