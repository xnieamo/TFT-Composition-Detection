
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

## Effect of units, tier, and items on placement
### Approach
Outcomes in a game of TFT is measured by your placement out of 8 players. The top 4 players are considered "winners". Therefore, we will binarize
out placement data for each composition. Then, to analyze the specific effects of units, tier of units, and number of items on units, we fit a 
logistic regression model to the data. We will do the analysis for the largest cluster first, and then repeat it using the whole data set.

### Insights
We can evaluate our model using a ROC curve [[3]][ROC]. The simple interpretation of such a plot is that the closer to the diagonal, the worse the model fit.
We see below that while unit presence does an okay job at predicting outcomes, unit tier and item count seem completely unrelated. This indicates that there
is little difference in the rate of upgrading units and which units get itemized between players. However, **the choice of units** is different enough to provide some insight 
to an optimal game strategy. 

![ROC_pres](/Data/Figures/UnitPresence_ROC.png)![ROC_tier](/Data/Figures/UnitTier_ROC.png)![ROC_item](/Data/Figures/UnitItems_ROC.png)

We plot the coefficients of each unit for our largest cluster to see the impact. Most of the top coefficients belong to strong units generally
acquired toward the end of the game, a confound due placement being determine by how long you survive. However, we also see 4 accessible units with the Crowd-diver
trait in the top 10 coefficients. This indicates that for this particular comp, you want to try playing these units.

![Cluster0](/Data/Figures/Comp0_coeffs.png)

What if we were to fit a model over all the data? Below, we see that two of the strongest predictors are Twitch and Pantheon (orange)! We would have missed 
this comp earlier if we set our `n_neighbors` too low. Additionally, Pentakill units Kayle and Viego (purple) as emerge as high value plays across the entire data.
![Cluster0](/Data/Figures/CompAll_coeffs.png)


## Insight into individual players
### Approach
While identifying trends in the playerbase is important to understand the meta and strategies that are most likely to be successful, it 
is also vital to understand each individual's playstyle. This allows players to review the progress they've made when trying to implement new strategies
and remove bias from evaluating flaws in their game. One way to approach this is to compare the players play rate of champions against the coefficients
from our logistic regression. We normalize the coefficients so that they sum up to 1, representing a theoretical play rate. Additionally, we can also 
calculate the similarity between the coefficient derived play rates and the player's. We'll use a cosine similarity here because we care more about directionality than
a measure of absolute difference.

### Insights
Below is a plot of the rank 1 player's playrate (orange, purple, grey) at the time this data was collected ploted against the coefficient playrates (blue). We notice
that while this player is successfully utilizing units like Kayle and Viego (purple) they may be overindexing on TD Akali and Thresh (grey). Additionally, while the comparison
also suggests leaning more into Twitch and Pantheon, that specific comp requires conditions that may be hard to activate. A more detailed analysis of the compositions
that included other information like augments may help tease this effect out.

![Rank1](/Data/Figures/Rank1_histogram.png)

In the next figure, we are plotting the dot product of player play unit and comp play rates with the population data. Players with more than 1400 LP are represented with larger 
circles. This visualization indicates that top players will lean more towards good units and good comps (not surprising). However, note that playing the best comps is not necessarily required to be at the top of the rankings, as only 2 large circles are above 0.3 on the y-axis.

![DotScatter](/Data/Figures/DotProducts.png)

## Conclusions
The code and write-up in this repo serve as a fairly cursory overview of some analytical techniques that can be used to think about player strategies
in TFT. While the clustering method for identifying team comps is interesting, it is also something that most stat sites already implement in one 
way or another. However, I do believe that analytics sites would benefit from utilizing regression based models of units and specific items instead of 
just presenting averages as that would allow for consideration of confounds, such as relative LP of the lobby. Finally, limitations based on sample size as well as
demand may affect the development of individualized analytics, but such tools will surely help improve skill development of the playerbase. My goal will be to
further develop some of these metrics and eventually launch a site tailored around provide players detailed insights into their playstyles. With luck, I'll be able
to launch a beta product by or slightly after Set 11 release, so stayed tuned for more!

## References
[1] https://umap-learn.readthedocs.io/en/latest/  \
[2] https://pair-code.github.io/understanding-umap/ \
[3] https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc


[UMAP_ref]:https://umap-learn.readthedocs.io/en/latest/
[UMAP_dist_ref]: https://pair-code.github.io/understanding-umap/
[ROC]:https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc
