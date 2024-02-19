import os
import pandas as pd
from sklearn.cluster import HDBSCAN
import matplotlib.pyplot as plt
import umap


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
umap_coords = umap_coords[hdbscan_labels['labels'] > -1]
hdbscan_labels = hdbscan_labels[hdbscan_labels['labels'] > -1]

# Plot
plt.scatter(umap_coords['x'], umap_coords['y'],c=hdbscan_labels['labels'],cmap='hsv')
# plt.scatter(umap_coords['x'], umap_coords['y'])
plt.xlabel('t-SNE Component 1')
plt.ylabel('t-SNE Component 2')
plt.title('t-SNE Visualization of Grouped Data')
plt.show()
