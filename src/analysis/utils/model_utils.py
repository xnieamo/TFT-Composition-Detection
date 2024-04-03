from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

import os
import pandas as pd
import numpy as np


def plot_coefficients(coefs, unit_presence):

    coefs_df = pd.DataFrame({'unit':unit_presence.columns,'coefs':np.exp(coefs)})
    coefs_df = coefs_df.sort_values(by='coefs', ascending=False)
    coefs_df['coefs'] = coefs_df['coefs'] - 1

    # Get only the item count coeffs
    item_count_coefs = coefs_df[coefs_df['unit'].str.contains('tier|item_count')]


    non_zero_coefs = item_count_coefs[item_count_coefs['coefs'] != 0]
    non_zero_coefs.plot.bar(x='unit', y='coefs', rot=75)

    plt.xticks(ha='right')
    plt.tight_layout()
    plt.show()
    pass


def plot_best_model(mdl, X_test, y_test):

    y_pred = mdl.predict_proba(X_test)
    fpr, tpr, _ = roc_curve(y_test, y_pred[:,1])
    auc_score = auc(fpr, tpr)

    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % auc_score)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    plt.show()

    pass

def load_data(comp_id=-1):
    # Set the working directory
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../../../Data/Processed/compAnalysis.h5')

    # Load h5 from data/processed
    with pd.HDFStore(filename,'r') as store:
        unit_presence = store.get('unit_presence')
        unit_tier = store.get('unit_tier')
        unit_item_count = store.get('unit_item_count')
        placement = store.get('placement')
        umap_labels = store.get('umap_labels')

    #  Keep data where cluster id is 0
    if comp_id < 0:
        clusterIdx = umap_labels['labels'] >= -1
    else:
        clusterIdx = umap_labels['labels'] == comp_id


    unit_presence = unit_presence[clusterIdx]
    unit_tier = unit_tier[clusterIdx].add_suffix('_tier')
    unit_item_count = unit_item_count[clusterIdx].add_suffix('_item_count')
    placement = placement[clusterIdx]

    # Binarize the placement data
    placement = placement['placement']  <= 4

    unit_presence = pd.concat([unit_presence,unit_item_count],axis=1)
    unit_presence = pd.concat([unit_presence,unit_tier],axis=1) 

    return unit_presence, placement