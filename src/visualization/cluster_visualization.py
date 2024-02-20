import os
import pandas as pd
from sklearn.cluster import HDBSCAN
import matplotlib.pyplot as plt


# Set the working directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../Data/Processed/umap_clusters.h5')

# Load h5 from data/processed
with pd.HDFStore(filename,'r') as store:
    umap_coords = store.get('umap_coords')
    hdbscan_labels = store.get('hdbscan_labels')


hdbscan_obj = HDBSCAN(min_cluster_size=200, min_samples=100).fit(umap_coords)
hdbscan_labels = pd.DataFrame(hdbscan_obj.labels_, columns=['labels'])
print(hdbscan_labels['labels'].unique())

# Keep coords where labels are not -1
clusterIdx = hdbscan_labels['labels'] > -1
umap_coords = umap_coords[clusterIdx]
hdbscan_labels = hdbscan_labels[clusterIdx]

# Load original data vectors to compute mean cluster vectors
filename = os.path.join(dirname, '../../Data/Processed/compAnalysis.h5')
with pd.HDFStore(filename,'r') as store:
    unit_presence = store.get('unit_presence')
    unit_tier = store.get('unit_tier')

unit_presence = unit_presence[clusterIdx]
unit_tier = unit_tier[clusterIdx]

# Compute mean cluster vectors by looping through the unique labels and average the corresponding vectors
for label in hdbscan_labels['labels'].unique():
    presence_cluster = unit_presence[hdbscan_labels['labels'] == label].mean()
    tier_cluster = unit_tier[hdbscan_labels['labels'] == label].mean()

    # Combine the mean vectors
    cluster = pd.concat([presence_cluster, tier_cluster], axis=1)

    # Print top 10 values of the mean cluster
    print(str(label)+" cluster size: "+str(sum(hdbscan_labels['labels'] == label)))
    print(cluster.nlargest(10, 0))
    


# Plot
# plt.scatter(umap_coords['x'], umap_coords['y'],c=hdbscan_labels['labels'],cmap='hsv')
# # plt.scatter(umap_coords['x'], umap_coords['y'])
# plt.xlabel('UMAP Component 1')
# plt.ylabel('UMAP Component 2')
# plt.title('UMAP Visualization of Grouped Data')
# plt.show()
