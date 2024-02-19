import os
import pandas as pd
from sklearn.cluster import HDBSCAN
import matplotlib.pyplot as plt
import umap

# Set the working directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../Data/Processed/compAnalysis.h5')

# Load h5 from data/processed
with pd.HDFStore(filename,'r') as store:
    unit_presence = store.get('unit_presence')
    # unit_tier = store.get('unit_tier')
    # unit_item_count = store.get('unit_item_count')
    # placement = store.get('placement')

# Print the data
# print(unit_presence.head(5))

# Create a umap plot of the data
umap_obj = umap.UMAP(n_neighbors=100, min_dist=0.3, n_components=2,metric='euclidean').fit_transform(unit_presence)

# Cluster with HBDSCAN
hdbscan_obj = HDBSCAN(min_cluster_size=100, min_samples=10).fit(umap_obj)

# Save the labels and umap coords to a h5 file
with pd.HDFStore('umap_clusters.h5', 'a', complevel=9, complib='blosc') as store:
    store.put('umap_coords', pd.DataFrame(umap_obj, columns=['x','y']))
    store.put('hdbscan_labels', pd.DataFrame(hdbscan_obj.labels_, columns=['labels']))


# Counter for the number of rows assigned to clusters
print(sum(hdbscan_obj.labels_ > -1)/len(hdbscan_obj.labels_))

# Plot the t-SNE
# plt.scatter(umap_obj[:,0], umap_obj[:,1],c=hdbscan_obj.labels_,cmap='Spectral')
# plt.xlabel('t-SNE Component 1')
# plt.ylabel('t-SNE Component 2')
# plt.title('t-SNE Visualization of Grouped Data')
# plt.show()



