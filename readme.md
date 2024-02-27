
# TFT Composition Detection

## Introduction

## Data acquisition and preprocessing
TFT match data was collected from all matches with at least 1 Challenger player on client version 14.2.556.3141 on February 
4th, 2024, using the RIOT API with a temporary personal key. Because all match history up until that point was initially
pulled, the raw SQLite data file is about 1 GB in size and therefore not uploaded here. None of the actual analyses require the file and 
work perfectly fine with the .h5 files in `Data/Processed`. The final data set for analysis had **37,032** comps in total, which is pretty 
small relative to the number of comps analyzed by popular data sites. However, we still are able to draw similar conclusions about
gameplay strategies.

For each player/match combination, the units on their final board was turning into a 60-dimnensional binary vector. Each
dimension represented a different unit and was set to 1 if present on the board. There are many ways to approach representing
boards. One example is to use or add information about traits and synergies. However, as we shall see, this simple approach 
works pretty well for composition identification.

## Identifying compositions
### Approach
We'll want to use an unsupervised learning algorithm since we don't have any labels for our data. There are many clustering 
techniques in the wild and I'd wager a fair number of them would be up to the task. However, this is not meant to be an academic excercise 
about clustering techniques, so we pick one based on specific qualities relevant to our dataset. HDBSCAN is a clustering 
technique that doesn't require pre-specifying the number of clusters and also handles variable cluster density and size. This is 
advantageous because we don't know a priori how many compositions are played and we don't know how popular each composition might be.

However, if we run HDBSCAN on our raw dataset, the algorithm will not converge within the default number of iterations. One reason might be that
each entry in our dataset is fairly sparse, given most comps end on 7-9 units. Instead, we'll apply a dimensionality reduction method called UMAP [[1]][UMAP_ref] to project 
our data onto 2 dimensions. 

### Insights
UMAP has two parameters: `n_neighbors` and `min_dist`. `n_neighbors` controls the amount of global structure in our projection and as its value 
increases, the projection more and more reflects the global structure of the original data. Below, we see that at low values
of `n_neighbors`, all the data points are projected into a single cloud, while at high values, smaller clusters emerge. The `min_dist` parameter influences
the distance between points in the project space. You can read more about this here [[2]][UMAP_dist_ref].

![UMAP_figure_here](/Data/Figures/UMAP_paramsweep.png)

The effect of these choice in UMAP become apparent once we run our clustering algorithm on our 2-dimensional data. The figure below on the left has  `n_neighbors=20`
while the figure on the right has  `n_neighbors=50`. `min_dist=0.5` for both. Points are colored by the cluster label assigned via
HDBSCAN. 

![20_0.5](/Data/Figures/Clusters_20_05.png) ![50_0.5](/Data/Figures/Clusters.png)

Visually, it is clear that the higher `n_neighbors` value has resulted a set of smaller clusters, but what does this mean
for our comp identification? 

Below is one of the largest clusters identified at `n_neighbors=20` with 5166 data points, along with average play rate and tier. Players will recognize these
units are core the "Excecutioner" line. However, this line is usually played as reroll, meaning that you try to level units to 
tier 3. So why is the average tier rate mostly under 2?
|                |   play rate |     tier |
|:---------------|------------:|---------:|
| TFT10_Amumu    |    0.883469 | 2.0391   |
| TFT10_Vex      |    0.835656 | 1.96787  |
| TFT10_Twitch   |    0.68254  | 1.5753   |
| TFT10_Pantheon |    0.662602 | 1.58653  |
| TFT10_Samira   |    0.563879 | 1.3734   |
| TFT10_Thresh   |    0.432249 | 0.707704 |
| TFT10_Jinx     |    0.283391 | 0.811653 |
| TFT10_Karthus  |    0.278746 | 0.427604 |
| TFT10_Urgot    |    0.275648 | 0.668215 |
| TFT10_Vi       |    0.266551 | 0.685056 |

If we look at the comps identified at `n_neighbors=50` that share similar units, we see that there are two variations of the line, one with Samira/Urgot (Country reroll) and another with Twitch/Pantheon (Twitch reroll) which often runs the augment Twin Terror, explaining the sudden drop in playrate from Vex to Samira. This granularity is lost at lower values of `n_neighbors`. The big cluster above combines the two comps, and we lose insight
into the key units played. We'll continue to our next analysis with `n_neighbors=50` because it is good enough, but do note that there may be some optimized clustering
parameters not explored.
<table>
<tr><td>

|                 |   play rate |     tier |
|:----------------|------------:|---------:|
| TFT10_Samira    |    0.994143 | 2.72182  |
| TFT10_Urgot     |    0.97511  | 2.45827  |
| TFT10_Thresh    |    0.966325 | 1.59883  |
| TFT10_Vex       |    0.963397 | 2.20059  |
| TFT10_Amumu     |    0.919473 | 2.07906  |
| TFT10_TahmKench |    0.913616 | 1.69693  |
| TFT10_Sett      |    0.651537 | 1.32064  |
| TFT10_Katarina  |    0.265007 | 0.525622 |
| TFT10_Illaoi    |    0.216691 | 0.248902 |
| TFT10_Karthus   |    0.120059 | 0.17716  |
</td><td>

|                        |   play rate |     tier |
|:-----------------------|------------:|---------:|
| TFT10_Amumu            |    0.938712 | 2.1849   |
| TFT10_Twitch           |    0.89294  | 2.07396  |
| TFT10_Pantheon         |    0.878717 | 2.10654  |
| TFT10_Vex              |    0.860357 | 2.04474  |
| TFT10_Samira           |    0.488234 | 1.11559  |
| TFT10_Jinx             |    0.373416 | 1.07111  |
| TFT10_Karthus          |    0.336178 | 0.514869 |
| TFT10_Vi               |    0.329972 | 0.857512 |
| TFT10_Thresh           |    0.31549  | 0.511249 |
| TFT10_Akali_TrueDamage |    0.202741 | 0.313421 |
</td></tr></table>

## Effect of units, upgrades, and items on placement
### Approach


### Insights
        - Logistic regression, ROC
        - Similar performance to a linear SVM
        - Crowd divers best
        - When fit over all data, twitch/pantheon emerges as very strong
## Insight into individual players
WIP: While most of the analysis is done, writing takes time! Check back in a few days
from now (02/26/2024)

## Conclusions

## References
[1] https://umap-learn.readthedocs.io/en/latest/  \
[2] https://pair-code.github.io/understanding-umap/


[UMAP_ref]:https://umap-learn.readthedocs.io/en/latest/
[UMAP_dist_ref]: https://pair-code.github.io/understanding-umap/