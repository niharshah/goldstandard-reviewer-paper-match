# Scripts to evaluate predicted similarity scores against references.

# For example usage, refer to the Experiments.ipynb notebook where this module is used
# to reproduce results of the paper

from itertools import combinations
import numpy as np


def compute_main_metric(preds, refs, vp, vr):
    """Compute accuracy of predictions against references (weighted kendall's tau metric)

    Args:
        preds: dict of dicts, where top-level keys corresponds to reviewers
        and inner-level keys correspond to the papers associated with a given
        reviewer in the dataset. Values in the inner dicts should represent similarities
        and must be computed for all (valid_reviewer, valid_paper) pairs from the references.

        refs: ground truth values of reviewer expertise. The structure of the object
        is the same as that of preds.

        vp: papers to use in evaluations
        vr: reviewers to use in evaluations

    Returns:
        Loss of predictions.

    Note: Absolute values of *predicted* similarities do not matter, only the ordering is used to
    compute the score. Values of similarities in the references are used to weight mistakes.
    """

    max_loss, loss = 0, 0

    for reviewer in vr:

        papers = list(refs[reviewer].keys())

        for p1, p2 in combinations(papers, 2):

            if p1 not in vp or p2 not in vp:
                continue

            pred_diff = preds[reviewer][p1] - preds[reviewer][p2]
            true_diff = refs[reviewer][p1] - refs[reviewer][p2]

            max_loss += np.abs(true_diff)

            if pred_diff * true_diff == 0:
                loss += np.abs(true_diff) / 2

            if pred_diff * true_diff < 0:
                loss += np.abs(true_diff)

    return loss / max_loss


def compute_resolution(preds, refs, vp, vr, regime='easy'):
    """Compute resolution ability of the algorithms for easy/hard pairs of papers.

    Args:
        preds: dict of dicts, where top-level keys corresponds to reviewers
        and inner-level keys correspond to the papers associated with a given
        reviewer in the dataset. Values in the inner dicts should represent similarities
        and must be computed for all (valid_reviewer, valid_paper) pairs from the references.

        refs: ground truth values of reviewer expertise. The structure of the object
        is the same as that of predictions.

        vp: papers to use in evaluations
        vr: reviewers to use in evaluations

        regime: whether to score resolution for hard cases (two papers with score 4+)
        or easy papers (one paper with score 4+, one paper with score 2-)

    Returns:
        Dictionary capturing the loss of predictions.

    Note: Absolute values of *predicted* similarities do not matter, only the ordering is used to
    compute the score. Each mistake costs 1 (we do not weigh by delta between similarities).
    """

    if regime not in {'easy', 'hard'}:
        raise ValueError("Wrong value of the argument ('regime')")

    num_pairs = 0
    num_correct = 0

    for reviewer in vr:

        papers = list(refs[reviewer].keys())

        for p1, p2 in combinations(papers, 2):

            if p1 not in vp or p2 not in vp:
                continue

            s1 = refs[reviewer][p1]
            s2 = refs[reviewer][p2]

            # We only look at pairs of papers that are not tied in terms of the expertise
            if s1 == s2:
                continue

            # Hard-coded parameters to define HARD pairs
            if regime == 'hard' and min(s1, s2) < 4:
                continue

            # Hard-coded parameters to define EASY pairs
            if regime == 'easy' and (max(s1, s2) < 4 or min(s1, s2) > 2):
                continue

            num_pairs += 1
            pred_diff = preds[reviewer][p1] - preds[reviewer][p2]
            true_diff = s1 - s2

            # An algorithm is correct if the ordering of predicted similarities agrees
            # with the ordering of the ground-truth expertise
            if pred_diff * true_diff > 0:
                num_correct += 1

    return {'score': num_correct / num_pairs, 'correct': num_correct, 'total': num_pairs}


if __name__ == '__main__':

    print("This module contains functions for computing the losses of the predicted similarities")