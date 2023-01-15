# DeepScore
The DeepScore Repository for the EuBIC 2023 Hackathon

## Scrum

![](scrum.jpg)
(This image was taken from https://www.pm-partners.com.au/the-agile-journey-a-scrum-overview/)

- Monday: Sprint Planning Meeting: We define a Story Map on what we want to do -> Product / Sprint Backlog. 
- We will have a two Daily Stand Ups at 09:00 and 13:00
- Thursday at 16:00 we will collect the results and have a Retrospective
- After that: Everyone can continue as they please

## Data:
- Relevant data will be uploaded here: https://datashare.biochem.mpg.de/s/3U2qb7EonBErttl

# Topics from the initial project proposal.

## 1 Assessing Confidence
- Hacks: Supplement random numbers to an ML-scoring system and investigate the performance
- Hard decoys: Provide harder decoys and investigate the performance
- Data Leakage: Gradually leak training data to a scoring system and investigate the performance

## 2 Interactive Tool
- Frontend that shows raw data and accepts user input to assign confidence scores
- Backend with database or functionality to merge multiple user sessions
 
## 3 Deep-learning Score
- Extract raw data identifications
- Train a model based on the human-supplied confidence scores
- Perform rescoring on existing studies

### Technical Details
The default language should be Python, but open to everything that gets the job done better.
The tools mentioned below are suggestions – there are a lot of great tools out there that I am not aware of, and we should collect and decide what to use at the beginning of the hackathon.
- GitHub to host the code and manage the project board
- AlphaPept https://github.com/MannLabs/alphapept to use an existing search engine that can be
hacked
- AlphaTims https://github.com/MannLabs/alphatims for raw data accession
- AlphaPeptDeep to build ML/DL models https://github.com/MannLabs/alphapeptdeep (This uses
PyTorch) or following the tutorials at https://www.proteomicsml.org
- Organizing & tracking ML tasks with: https://neptune.ai/home
- To collect data for manual curation we could use MongoDB https://www.mongodb.com
- Frontend: https://streamlit.io
I use Visual Studio Code with Anaconda and have a couple of DL/ML environments ready to go.
- The programming language(s) that will be used.
- (If applicable) Any existing software that will be featured.
- (If applicable) Any datasets that will be used and their availability.
