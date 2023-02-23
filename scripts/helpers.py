# Auxiliary functions to streamline the similarity computation.

import pandas as pd


def to_dicts(df):
    """Process the released dataframe in .csv format into a dict of dicts that is used in the
    evaluation and prediction stages.

    Args:
        df: released dataset in csv format.

    Returns:
        refs: reference similarities.
         {reviewer1: {paper1: expertise1, paper2: expertise2, ...}, ...}

        targets: Dict of sets. Each key in this dict corresponds to a reviewer and each
        set is a set of papers for which the reviewer evaluated their expertise.
         {reviewer1: {paper1, paper2, paper3, ... }, ...}
    """
    refs, targets = {}, {}

    for idx, row in df.iterrows():
        key = str(row['ParticipantID'])

        refs[key] = {row[f'Paper{x}']: row[f'Expertise{x}'] for x in range(1, 11)
                     if not pd.isna(row[f'Paper{x}'])}

        targets[key] = set([row[f'Paper{x}'] for x in range(1, 11)
                            if not pd.isna(row[f'Paper{x}'])])

    return refs, targets


if __name__ == '__main__':
    print("This module contains some helper functions to streamline the analysis")
