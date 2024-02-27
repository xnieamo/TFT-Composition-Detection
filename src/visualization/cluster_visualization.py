import os
import pandas as pd
from sklearn.cluster import HDBSCAN
import matplotlib.pyplot as plt


# Set the working directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../Data/Processed/umap_hyperparam_sweep.h5')

# Load h5 from data/processed
with pd.HDFStore(filename,'r') as store:
        for key in store.keys():
        
            # Extract param values from the key
            n_neighbors = int(key.split('_')[3])
            min_dist = float(key.split('_')[5])

            if n_neighbors == 50 and min_dist == 0.5:
                umap_coords = store.get(key)

# Fit HDBSCAN to the umap coordinates
hdbscan_obj = HDBSCAN(min_cluster_size=200, min_samples=100).fit(umap_coords)
hdbscan_labels = pd.DataFrame(hdbscan_obj.labels_, columns=['labels'])

# Save umap labels to compAnalysis.h5
savefilename = os.path.join(dirname, '../../Data/Processed/compAnalysis.h5')
with pd.HDFStore(savefilename, 'a', complevel=9, complib='blosc') as store:
    # Remove existing label if it exists
    if 'umap_labels' in store.keys():
        store.remove('umap_labels')

    # Save the new label
    store.put('umap_labels', hdbscan_labels)


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
writefilename = os.path.join(dirname, '../../Data/Processed/compUnits.txt')
with open(writefilename, 'w') as file:
    for label in hdbscan_labels['labels'].unique():
        presence_cluster = unit_presence[hdbscan_labels['labels'] == label].mean().rename('play rate')
        tier_cluster = unit_tier[hdbscan_labels['labels'] == label].mean().rename('tier')

        # Combine the mean vectors
        cluster = pd.concat([presence_cluster, tier_cluster], axis=1)

        # Write the cluster to a file
        file.write(str(label)+", cluster size: "+str(sum(hdbscan_labels['labels'] == label))+'\n')
        file.write(cluster.nlargest(10, 'play rate').to_markdown()+'\n\n')


# Plot
plt.scatter(umap_coords['x'], umap_coords['y'],c=hdbscan_labels['labels'],cmap='hsv')
plt.xlabel('UMAP Component 1')
plt.ylabel('UMAP Component 2')
plt.title('UMAP Visualization of Grouped Data')
plt.show()
