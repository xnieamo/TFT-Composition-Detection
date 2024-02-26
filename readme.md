# TODO LIST
- [ ] Roll calculator
- [x] JSON importer
    - [x] Automatic JSON downloader
- [ ] Champ DPS calculator
    - [ ] DPS time line 


- Challenger player list from 2/4/2024
    - 4631 matches on most recent patch with at least 1 challenger player
        - Needed to filter out approx 100 set 3 games


SECTIONS
Introduction
Data acquisition and preprocessing
Identifying comps
    - Approach
    - Comparison to tactics.tools
    - insights
        - low global structure leaves merges similar comps (excecutioner's) and 
          you lose fine grain information (vex vs samira carry)
        - not enough distance focuses too much on single clusters of comps -> this
          happens because we used binary vectors so strong overlapping units result in 100% appearance
Upgrades and items effects on placement
    - Approach
        - Use heartsteal as example bc most data and most diverse distribution of champs
        - fit logistic regression to identify factors that are most important -> cluster 0
        - binarize outcomes to top4 and bot4
    - insights
        - Logistic regression, ROC
        - Similar performance to a linear SVM
        - Crowd divers best
        - When fit over all data, twitch/pantheon emerges as very strong
Individual player advice
    - Approach

    - Insights

Conclusions
