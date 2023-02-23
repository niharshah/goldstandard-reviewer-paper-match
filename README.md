# README

This repository accompanies the paper "*A Gold Standard Dataset for the Reviewer Assignment Problem*" by Stelmakh, Wieting, Neubig, and Shah. The structure of the directory is as follows (more details on each point below):

1. `data` folder contains the dataset we release in this work
2. `notebooks` folder contains jupyter notebooks that explore the dataset and replicate the results of the paper
3. `evaluation_datasets` folder contains the dataset preprocessed into the OpenReview format that similarity computation algorithms can directly work with
4. `predictions` folder contains similaritites predicted by different similarity-computation algorithms
5. `scripts` folder contains various scripts, including the evaluation code and implementation of the TPMS algorithm
6. `configs_for_OR_models` folder contains config files used to run the Open Review algorithns (ELMo, Specter, Specter+MFR)

We now provide more details on each of the released folders.

## Data

The dataset folder contains six items:

*1. evaluations.csv*

This tab-separated file contains evaluations reported by participants. Each row in the data frame corresponds to a participant who is represented by their Semantic Scholar ID (`ParticipantID`).

Evaluations reported by the participants are represented in 20 columns. The first 10 columns (`PaperX` where X ranges from 1 to 10) contain Semantic Scholar IDs of papers that a participant evaluated their expertise in. Missing values in these columns indicate that the participant reported expertise for less than 10 papers.

The second 10 columns (`ExpertiseX` where X ranges from 1 to 10) represent expertise in reviewing the corresponding papers (e.g., `Expertise1` is expertise in reviewing `Paper1`). The values of expertise are from 1 to 5 with larger values representing higher expertise. Again, if a participant reported expertise in less than 10 papers, the values of expertise corresponding to missing papers will be missing.

**2. research_areas.json**

This json file contains research areas of papers reported by participants as classified by the Semantic Scholar tool.

**3. participants folder (profiles of participants)**

For each participant, this folder contains a json file, representing the Semantic Scholar profile of the participant crawled on May 1, 2022.

**4. papers (profiles of all papers)**

For each paper (reported by participants or from reviewers' profiles), this folder contains a json file, representing the Semantic Scholar profile of the paper crawled on May 1, 2022.

Note: For papers reported by participants, we edit semantic scholar profiles by adding links to publicly available PDFs whenever they were missing in the SS profile.

**5. pdfs**

PDF files for each paper (reported by participants or from reviewers' profiles) that has PDF publicly available.

**6. txts**

Parsed PDF file. For each file, there is:
- .txt file that is obtained by parsing the pdf with the `xpdf` tool
- .json file that contains counts of workds in the txt file with some sanitization applied (txt -> json conversion is done using the approach of Laurent Charlin https://bitbucket.org/lcharlin/tpms/src/master/)
