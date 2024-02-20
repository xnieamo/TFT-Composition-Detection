import os
import pandas as pd
import matplotlib.pyplot as plt

# Set the working directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../Data/Processed/umap_hyperparam_sweep.h5')

# Create a list to store the dataframes
umap_coords = []
params = []

# Load h5 from data/processed
with pd.HDFStore(filename,'r') as store:
    for key in store.keys():
        
        # Extract param values from the key
        n_neighbors = int(key.split('_')[3])
        min_dist = float(key.split('_')[5])
        params.append([n_neighbors, min_dist])

        # Load the dataframes
        umap_coords.append(store.get(key))

# Reorganize the dataframes and params to match the plotting order. We need to
# sort by min_dist and then n_neighbors.
params = sorted(enumerate(params), key=lambda x: (x[1][1],x[1][0]))
umap_coords = [umap_coords[i[0]] for i in params]
params = [i[1] for i in params]

# Plot each dataframe on a separate subplot. Each column is a different
# n_neighbors and each row is a different min_dist.
fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(15,10))
for i, ax in enumerate(axes.flat):
    ax.scatter(umap_coords[i]['x'], umap_coords[i]['y'])
    ax.set_title('n_neighbors: '+str(params[i][0])+' min_dist: '+str(params[i][1]))
    ax.set_xlabel('UMAP Component 1')
    ax.set_ylabel('UMAP Component 2')
plt.tight_layout()
plt.show()