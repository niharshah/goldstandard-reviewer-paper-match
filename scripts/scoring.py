# Scripts to evaluate predicted similarity scores against references.

# For example usage, refer to the Experiments.ipynb notebook where this module is used
# to reproduce results of the paper

from itertools import combinations
import numpy as np


def compute_kendall_tau(preds, refs, vp, vr, k=None):
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
        k: int to indices the use of top k items

    Returns:
        Loss of predictions.

    Note: Absolute values of *predicted* similarities do not matter, only the ordering is used to
    compute the score. Values of similarities in the references are used to weight mistakes.
    """

    max_loss, loss = 0, 0

    for reviewer in vr:
        papers = list(refs[reviewer].keys())
        
        valid_papers = [p for p in papers if p in vp]
        # Skip reviewers with no valid papers
        if not valid_papers:
            continue
        # sort the papers by highest to lowest algorithm scoring
        pred_ranking = sorted(valid_papers, key=lambda p: preds[reviewer][p], reverse=True)
        # get all the pairs for valid papers
        pairs = list(combinations(pred_ranking, 2))
        # Get the pairs where one element is in the top k valid papers
        if k:
            top_k_items = set(pred_ranking[:k])  
            pairs = [pair for pair in pairs if pair[0] in top_k_items or pair[1] in top_k_items]
        
        for p1, p2 in pairs:

            pred_diff = preds[reviewer][p1] - preds[reviewer][p2]
            true_diff = refs[reviewer][p1] - refs[reviewer][p2]

            max_loss += np.abs(true_diff)

            if pred_diff * true_diff == 0:
                loss += np.abs(true_diff) / 2

            if pred_diff * true_diff < 0:
                loss += np.abs(true_diff)

    return loss / max_loss
    
def compute_mrr(preds, refs, vp, vr, k):
    """Compute accuracy of predictions against references (MRR metric)

    Args:
        preds: dict of dicts, where top-level keys corresponds to reviewers
        and inner-level keys correspond to the papers associated with a given
        reviewer in the dataset. Values in the inner dicts should represent similarities
        and must be computed for all (valid_reviewer, valid_paper) pairs from the references.

        refs: ground truth values of reviewer expertise. The structure of the object
        is the same as that of preds.

        vp: papers to use in evaluations
        vr: reviewers to use in evaluations
        k: int to indices the use of top k items

    Returns:
        Loss of predictions.
    """
    means = []
    for reviewer in vr:
        papers = list(refs[reviewer].keys())
        valid_papers = [p for p in papers if p in vp]
        if not valid_papers:
            continue
        
        r_ranks = []
        
        pred_ranking = sorted(valid_papers, key=lambda p: preds[reviewer][p], reverse=True)
        ref_ranking = sorted(valid_papers, key=lambda p: refs[reviewer][p], reverse=True)
        
        for ref in ref_ranking[:k]:
            r_ranks.append(1/(pred_ranking.index(ref)+1))
        means.append(np.mean(r_ranks))

    return np.mean(means)

def compute_precision(preds, refs, vp, vr, k):
    """Compute accuracy of predictions against references (Precision metric)

    Args:
        preds: dict of dicts, where top-level keys corresponds to reviewers
        and inner-level keys correspond to the papers associated with a given
        reviewer in the dataset. Values in the inner dicts should represent similarities
        and must be computed for all (valid_reviewer, valid_paper) pairs from the references.

        refs: ground truth values of reviewer expertise. The structure of the object
        is the same as that of preds.

        vp: papers to use in evaluations
        vr: reviewers to use in evaluations
        k: int to indices the use of top k items

    Returns:
        Loss of predictions.
    """
    preision_score = []
    for reviewer in vr:
        papers = list(refs[reviewer].keys())
        valid_papers = [p for p in papers if p in vp]
        if not valid_papers:
            continue
        
        pred_ranking = sorted(valid_papers, key=lambda p: preds[reviewer][p], reverse=True)
        ref_ranking = sorted(valid_papers, key=lambda p: refs[reviewer][p], reverse=True)

        count = 0
        for i in pred_ranking[:k]:
            if i in ref_ranking[:k]:
                count += 1
        preision_score.append(count/k)

    return np.mean(preision_score)

def compute_ndcg(preds, refs, vp, vr, k):
    """Compute accuracy of predictions against references (NDCG metric)

    Args:
        preds: dict of dicts, where top-level keys corresponds to reviewers
        and inner-level keys correspond to the papers associated with a given
        reviewer in the dataset. Values in the inner dicts should represent similarities
        and must be computed for all (valid_reviewer, valid_paper) pairs from the references.

        refs: ground truth values of reviewer expertise. The structure of the object
        is the same as that of preds.

        vp: papers to use in evaluations
        vr: reviewers to use in evaluations
        k: int to indices the use of top k items

    Returns:
        Loss of predictions.
    """
    def dcg(scores):
        """Compute Discounted Cumulative Gain (DCG)."""
        return sum(rel / np.log2(idx + 2) for idx, rel in enumerate(scores))

    ndcg_scores = []

    for reviewer in vr:
        papers = list(refs[reviewer].keys())
        valid_papers = [p for p in papers if p in vp]
        if not valid_papers:
            continue

        # Predicted ranking (sorted by predicted scores)
        pred_ranking = sorted(valid_papers, key=lambda p: preds[reviewer][p], reverse=True)[:k]
        # Ground truth relevance scores in predicted ranking order
        rel_score = [refs[reviewer][p] for p in pred_ranking]
        # Ideal ranking (sorted by ground truth)
        ideal_ranking = sorted(valid_papers, key=lambda p: refs[reviewer][p], reverse=True)[:k]
        # Ground truth relevance scores in ideal ranking order
        ideal_score = [refs[reviewer][p] for p in ideal_ranking]
        # Compute NDCG
        ndcg = dcg(rel_score) / dcg(ideal_score) if dcg(ideal_score) > 0 else 0
        ndcg_scores.append(ndcg)

    # Return average NDCG across all reviewers
    return np.mean(ndcg_scores) if ndcg_scores else 0

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