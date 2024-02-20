import os
import umap
import time
import pandas as pd

# Set the working directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../Data/Processed/compAnalysis.h5')

# Load h5 from data/processed
with pd.HDFStore(filename,'r') as store:
    unit_presence = store.get('unit_presence')

# UMAP Hyperparameters
n_neighbors_vec = [5,20,50,100,200]
min_dist_vec = [0.3,0.5,0.9]

# Make a list to hold all the dataframes and hyperparam for each iteration
umap_dfs = []
params = []

# Iterate through the hyperparameters, print a timer for each iteration
for n_neighbors in n_neighbors_vec:
    for min_dist in min_dist_vec:
        # Track time
        start_time = time.time()

        # Fit UMAP to the data
        umap_obj = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, n_components=2,metric='euclidean').fit_transform(unit_presence)
        umap_dfs.append(pd.DataFrame(umap_obj, columns=['x','y']))
        params.append([n_neighbors, min_dist])

        # Print runtime
        print("--- %s seconds ---" % (time.time() - start_time))


# Save the umap dataframes to a h5 file and label them with the hyperparameters
savefilename = os.path.join(dirname, '../../Data/Processed/umap_hyperparam_sweep.h5')
with pd.HDFStore(savefilename, 'a', complevel=9, complib='blosc') as store:
    for i, df in enumerate(umap_dfs):
        store.put('umap_coords_nneigh_'+str(params[i][0])+'_mindist_'+str(params[i][1]*10), df)





