# Compute TPMS similarities.

# Example usage:
# python tpms.py --OR_dir ../evaluation_datasets --destination ../predictions --regime title+abstract --OR_name d_20_1 --name tpms_test
# See `parse_args` function below to understand the arguments

# The code of the TPMS algorithm is based on the code accompanying the following publication:
# Xu, Y., Zhao, H., Shi, X., and Shah, N. (2019). On strategyproof conference review. In IJCAI.

from tpms_helpers.sanitize import tokenize, isUIWord

import argparse
import os
import json
import math

from nltk.stem import PorterStemmer
from collections import Counter
from collections import defaultdict


def _wrap_na(text):
    """Substitute None with empty string.

    Args:
        text: Text to be wrapped

    Returns:
        Empty string if text is none and the original text otherwise
    """

    if text is None:
        return ''

    return text


def paper2bow(text):
    """Tokenize and filter given text.

    Args:
        text: string to be processed
    Returns:
        Counter of words in the text
    """
    words = [w.lower() for w in tokenize(text)]
    # Filter out uninformative words.
    words = filter(lambda w: not isUIWord(w), words)
    # Use PortStemmer.
    ps = PorterStemmer()
    words = [ps.stem(w) for w in words]
    return Counter(words)


def get_paper_profiles(file, regime):
    """Get representations for papers' content

    Args:
        file: path to file where papers' representations are stored
        regime: a keyword specifying the amount of information available to the algorithm

    Returns:
        Dictionary in which each entry is a target representation
    """
    if regime not in ['title', 'title+abstract', 'full']:
        raise ValueError("Undefined regime is requested")

    with open(file, 'r') as handler:
        papers = json.load(handler)

    papers_dict = {}
    ps = PorterStemmer()

    for key in papers:
        paper = papers[key]
        texts = []
        loc_counter = {}

        texts.append(_wrap_na(paper['content']['title']))

        if regime == 'title+abstract' or regime == 'full':
            texts.append(_wrap_na(paper['content']['abstract']))

        if regime == 'full':
            if 'text' not in paper['content']:
                raise ValueError(f"Paper {paper} has no textual content")

            for word, item in paper['content']['text'].items():

                stemmed_word = ps.stem(word)

                if stemmed_word in loc_counter:
                    loc_counter[stemmed_word] += item
                else:
                    loc_counter[stemmed_word] = item

        content = paper2bow(' '.join(texts))

        for word in loc_counter:
            if word in content:
                content[word] += loc_counter[word]
            else:
                content[word] = loc_counter[word]

        papers_dict[key] = content

    return papers_dict


def get_reviewer_profiles(directory, regime):
    """Get representations for reviewers' bibliographies

    Args:
        directory: path where reviewers' jsonl representations are stored
        regime: a keyword specifying the amount of information available to the algorithm

    Returns:
        Dictionary in which each entry is a target representation
    """

    if regime not in ['title', 'title+abstract', 'full']:
        raise ValueError("Undefined regime is requested")

    profiles_dict = {}
    ps = PorterStemmer()

    for file in os.listdir(directory):

        key = file.split('.')[0].strip('~')
        texts = []
        loc_counter = {}

        with open(os.path.join(directory, file), 'r') as handler:

            for line in handler:
                paper = json.loads(line)
                texts.append(_wrap_na(paper['content']['title']))

                if regime == 'title+abstract' or regime == 'full':
                    texts.append(_wrap_na(paper['content']['abstract']))

                if regime == 'full':

                    if 'text' not in paper['content']:
                        raise ValueError(f"Paper {paper} has no textual content")

                    for word, item in paper['content']['text'].items():

                        stemmed_word = ps.stem(word)

                        if stemmed_word in loc_counter:
                            loc_counter[stemmed_word] += item
                        else:
                            loc_counter[stemmed_word] = item

        profile = paper2bow(' '.join(texts))

        for word in loc_counter:
            if word in profile:
                profile[word] += loc_counter[word]
            else:
                profile[word] = loc_counter[word]

        profiles_dict[key] = profile

    return profiles_dict


def compute_idf(profiles):
    """Given a set of documents, compute IDF of each word

    Args:
        profiles: a list of dicts of word counters to compute IDF for.
        Each counter represents a document:
        [{d1: {w1: count of w1 in d1, w2: count of w2 in d1}, d2: ...}]

    Returns:
        IDFs of the words in documents
    """

    num_docs = sum([len(x) for x in profiles])
    idf = defaultdict(lambda: 0.0)

    for profile in profiles:
        for loc_key in profile:
            for word in profile[loc_key]:
                idf[word] += 1.0

    for word in idf:
        idf[word] = math.log(num_docs / idf[word])

    return idf


def compute_similarities(revs, paps):
    """Compute TPMS similarities

    Args:
        revs: profiles of reviewers
        paps: profiles of papers

    Returns:
        Dict of similarities between each reviewer and paper
    """

    similarities = {}
    idf_dict = compute_idf([revs, paps])

    for r in revs:

        similarities[r] = dict()

        for p in paps:

            r_profile, p_profile = revs[r], paps[p]

            if len(r_profile) == 0 or len(p_profile) == 0:
                raise ValueError(f"Empty profiles in pair {r, p}")

            r_normalizer, p_normalizer = max(r_profile.values()), max(p_profile.values())
            similarity = 0.0

            r_norm, p_norm = 0.0, 0.0

            for word in r_profile:
                r_tf = 0.5 + 0.5 * r_profile[word] / r_normalizer
                w_idf = idf_dict[word]
                r_norm += (r_tf * w_idf) ** 2

                if word in p_profile:
                    p_tf = 0.5 + 0.5 * p_profile[word] / p_normalizer
                    similarity += r_tf * p_tf * (w_idf ** 2)

            for word in p_profile:
                p_tf = 0.5 + 0.5 * p_profile[word] / p_normalizer
                w_idf = idf_dict[word]
                p_norm += (p_tf * w_idf) ** 2

            r_norm, p_norm = math.sqrt(r_norm), math.sqrt(p_norm)

            similarities[r][p] = similarity / r_norm / p_norm

    return similarities


def handle_dataset(path, regime):
    """Compute similarities for dataset in the OR format.

    Args:
        path: path to the dataset in the OR format
        regime: a keyword specifying the amount of information available to the algorithm

    Returns:
        Dict of dicts where outer level corresponds to reviewers,
        inner level corresponds to papers, and values are (reviewer, paper)
        similarities
    """

    reviewers_dir = os.path.join(path, 'archives')
    papers_file = os.path.join(path, 'submissions.json')

    reviewers = get_reviewer_profiles(reviewers_dir, regime)
    papers = get_paper_profiles(papers_file, regime)

    similarities = compute_similarities(reviewers, papers)

    return similarities


def parse_args(argv=None):

    parse = argparse.ArgumentParser()

    parse.add_argument('--OR_dir', type=str, help='Path to the OR datasets folder')
    parse.add_argument('--OR_name', type=str, help='Name of the OR dataset')
    parse.add_argument('--regime', type=str, default='title',
                       help='The amount of information available to the algorithm')
    parse.add_argument('--destination', type=str, help='Output dir')
    parse.add_argument('--name', type=str, help='Name of the prediction file')

    return parse.parse_args(argv)


if __name__ == '__main__':
    args = parse_args()

    OR_dataset_path = os.path.join(args.OR_dir, args.OR_name)
    predictions = handle_dataset(OR_dataset_path, args.regime)

    with open(os.path.join(args.destination, args.name + '.json'), 'w') as handler:
        json.dump(predictions, handler)