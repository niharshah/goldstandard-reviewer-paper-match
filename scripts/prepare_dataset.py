# Prepare dataset for similarity computation in the OperReview format
# (https://github.com/openreview/openreview-expertise)

# Example usage:
# python prepare_dataset.py --dataset ../data --destination ../evaluation_datasets --OR_name test_20 --hist_len 20 --regime SS

import os
import json
import numpy as np
import pandas as pd

import argparse
import helpers as hlp


def _get_k_recent_papers(participant, data_path, k, regime='SS'):
    """Get the most recent papers from a participant's publication profile.
    Only years are used for ordering and ties are broken uniformly at random.

    Args:
        participant: Semantic Scholar id of the participant
        data_path: Path to the dataset folder
        k: number of papers that should be included in the profile
        regime: whether to use SS or other representations

    Returns:
        A list of length k where each entry represents a paper
    """

    profile_coarse, profile_fine, profile = {}, {}, []

    # Read reviewer representation (contains only paper IDs)
    with open(os.path.join(data_path, 'participants', participant + '.json'), 'r') as handler:
        profile_coarse = json.load(handler)

    # For each of the reviewer's paper, read its representation (contains more paper info)
    for pid in set([pap['paperId'] for pap in profile_coarse['papers']]):
        paper = _get_paper_representation(pid, data_path, regime)

        if paper is not None:
            profile_fine[pid] = paper

    if k is None:
        k = len(profile_fine)

    recent_papers = sorted(profile_fine.keys(),
                           key=lambda x: profile_fine[x]['year'] + np.random.uniform(0, 0.001),
                           reverse=True)[:k]

    return [{'id': tp, 'content': profile_fine[tp]} for tp in recent_papers]


def _get_paper_representation(pid, data_path, regime):
    """ Read representation of the paper.

    Args:
        pid: Semantic Scholar id of the paper
        data_path: Path to the dataset folder
        regime: whether to use SS or other representations

    Returns:
        Dict representing the paper. If some important fields are missing (title, abstract, year, full text),
        return None which means that the paper should be excluded from similarity computation
    """

    # Directory with semantic scholar representations of papers
    ss_dir = os.path.join(data_path, 'papers')

    # Directory with PDFs parsed into txt files
    pdf_dir = os.path.join(data_path, 'txts')

    with open(os.path.join(ss_dir, pid + '.json'), 'r') as handler:
        paper = json.load(handler)

    # We only leave papers with non-empty title, abstract, and year of publications
    if paper['title'] is None or paper['abstract'] is None or paper['year'] is None:
        return None

    if regime == 'SS':
        return paper

    if pid + '.json' not in set(os.listdir(pdf_dir)):
        return None

    with open(os.path.join(pdf_dir, pid + '.json'), 'r') as handler:
        text = json.load(handler)

    paper['text'] = text

    return paper


def prepare_dataset(dst_path, targets, data_path, k=10, regime='SS'):
    """Transform the dataset we release into the OpenReview format required by the similarity computation methods.

    Args:
        dst_path: path to the folder where the dataset will be stored.
        The folder should not exist and will be created

        targets: dict of sets where each set corresponds to a reviewer and
        contains papers the (reviewer, paper) similarities should be computed for.

        regime: whether to use SS or other representations

        data_path: path to the dataset folder

        k: number of papers that should be included in the profile
    """

    if regime not in set(['SS', 'PDF']):
        raise ValueError("Unknown regime is provided")

    if os.path.exists(dst_path):
        print("I reuse the existing dataset. Provide a fresh path if you want to build a new one")
        return dst_path

    archives_path = os.path.join(dst_path, 'archives')
    submissions_path = os.path.join(dst_path, 'submissions.json')

    os.mkdir(dst_path)
    os.mkdir(archives_path)

    papers = {}

    for participant in targets:

        # Prepare a single jsonl with the participant's profile
        profile = _get_k_recent_papers(participant, data_path, k, regime)

        # If a reviewer does not have papers to include in the profile, we remove them. This can happen if a reviewer
        # does not have papers with arXiv links in their SS profiles (when we construct dataset in the `PDF` regime)
        if len(profile) > 0:

            with open(os.path.join(archives_path, '~' + participant + '.jsonl'), 'w', encoding='utf-8') as handler:
                for line in profile:
                    handler.write(json.dumps(line) + '\n')

        # Prepare a single json for all target papers

        for pid in targets[participant]:

            content = _get_paper_representation(pid, data_path, regime)

            if content is None:
                continue

            paper = {"id": pid, "content": content}

            papers[pid] = paper

    with open(submissions_path, 'w', encoding='utf-8') as handler:
        json.dump(papers, handler)


def parse_args(argv=None):
    parse = argparse.ArgumentParser()
    parse.add_argument('--dataset', type=str, help='Path to the dataset main folder')
    parse.add_argument('--destination', type=str, help='Path to the destination folder')
    parse.add_argument('--OR_name', type=str, help='Name of the OR-transformed dataset')
    parse.add_argument('--regime', type=str, default='SS', help='Whether to use SS or other representations')
    parse.add_argument('--hist_len', type=int, help='Number of papers that should be included in the profile')

    return parse.parse_args(argv)


if __name__ == '__main__':
    args = parse_args()

    df = pd.read_csv(os.path.join(args.dataset, 'evaluations.csv'), sep='\t')
    _, targets = hlp.to_dicts(df)

    OR_dataset_path = os.path.join(args.destination, args.OR_name)
    prepare_dataset(OR_dataset_path, targets, args.dataset, args.hist_len, args.regime)