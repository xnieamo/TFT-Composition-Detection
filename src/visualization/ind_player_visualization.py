import sqlite3
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Set the working directory
dirname = os.path.dirname(__file__)
db_filename = os.path.join(dirname, '../../Data/Raw/TFT.db')
h5_filename = os.path.join(dirname, '../../Data/Processed/compAnalysis.h5')


# Get challenger puuids and lp from the database
db = sqlite3.connect(db_filename)
cur = db.cursor()
cur.execute('''
    SELECT puuid, lp
    FROM players
    WHERE lp > 0
    ORDER BY lp DESC
''')
challenger_data = cur.fetchall()
db.close()

# Load the data from the h5 file
with pd.HDFStore(h5_filename,'r') as store:
    unit_presence = store.get('unit_presence')
    placement = store.get('placement')
    umap_labels = store.get('umap_labels')
    puuids = store.get('puuid')
    log_coeffs = store.get('logreg_coefs')

# Filter players with 50+ games and challenger
puuid_counts = puuids['puuid'].value_counts()
puuids_lp = [x for x in challenger_data if x[0] in puuid_counts and puuid_counts[x[0]] > 50]
puuids_lp_df = pd.DataFrame(puuids_lp, columns=['puuid','lp'])

# Print average placement for each unique cluster label
mean_placement = placement.groupby(umap_labels['labels']).mean().sort_values(by='placement')
rel_placement = (4.5-mean_placement).clip(0,4.5)

# 
log_coeffs_only = log_coeffs['coefs'].to_frame()
norm_log_coeffs = log_coeffs_only / np.linalg.norm(log_coeffs_only)

# Compute comp and champ play rate for each player in puuids_lp
comp_dot_products = []
champ_dot_products = []
for puuid in puuids_lp_df['puuid']:

    idx = puuids.index[puuids['puuid'] == puuid].tolist()

    # Compute comp play rate as a dataframe
    comp_play_rate = umap_labels.loc[umap_labels.index.isin(idx)]
    comp_play_rate = comp_play_rate['labels'].value_counts(normalize=True).rename('play rate')

    # Make comp play match rel_placement
    comp_play_rate = comp_play_rate.reindex(rel_placement.index, fill_value=0)
    
    # Compute dot product on normalized vectors with label > -1'
    c_idx = comp_play_rate > -1
    comp_play_rate = comp_play_rate[c_idx].to_frame()
    norm_comp_play_rate = comp_play_rate / np.linalg.norm(comp_play_rate)
    norm_rel_placement = rel_placement[c_idx] / np.linalg.norm(rel_placement[c_idx])
    dot_product = np.dot(norm_comp_play_rate.T, norm_rel_placement)
    comp_dot_products.append(dot_product[0][0])

    # Compute champ play rate
    champ_play_rate = unit_presence.loc[unit_presence.index.isin(idx)].mean().rename('play rate')

    # Reorder champ play rate to match the order of the logreg_coeffs in df
    champ_play_rate = champ_play_rate.reindex(log_coeffs['unit'])

    # Compute the dot product of the player's champ play rate and the logreg coefficients with normalized vectors
    champ_play_rate = champ_play_rate.to_frame()
    norm_champ_play_rate = champ_play_rate / np.linalg.norm(champ_play_rate)

    dot_product = np.dot(norm_champ_play_rate.T, norm_log_coeffs)   
    champ_dot_products.append(dot_product[0][0])

    # Keep play rate of top 10 players
    this_lp = puuids_lp_df.loc[puuids_lp_df['puuid'] == puuid]['lp']
    if this_lp.values[0] == puuids_lp_df['lp'].nlargest(10).values[0]:
        plot_play_rate = norm_champ_play_rate


# print(norm_champ_play_rate.head(5))
# print(norm_log_coeffs.head(5))


# Plot a double histogram of the champ pla rate and the log coefficients
x = np.arange(norm_champ_play_rate.shape[0])
fig = plt.figure()
ax = fig.add_subplot(111)
plt.bar(x,norm_log_coeffs['coefs'],alpha=0.75)
barlist = plt.bar(x,plot_play_rate['play rate'],alpha=0.75)
[barlist[i].set_color('#9467bd') for i in [12,14]]
[barlist[i].set_color('#7f7f7f') for i in [-14,-15]]
plt.xlabel('Dot Product')
plt.ylabel('Frequency')
plt.title('Rank 1 Play Rate Histogram')
plt.xticks(rotation=75)
ax.set_xticks(x)
ax.set_xticklabels(norm_champ_play_rate.index)
plt.show()

# Plot scatter plot of dot prodcuts with lp as size
plt.scatter(champ_dot_products, comp_dot_products, s=[100 if x > 1400 else 10 for x in puuids_lp_df['lp']], alpha=0.5)
plt.xlabel('Champ')
plt.ylabel('Comp')
plt.title('Dot Products of Champ and Comp Play Rate')
plt.show()
