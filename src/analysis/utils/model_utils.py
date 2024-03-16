from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

import os
import pandas as pd

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

def load_data():
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
    clusterIdx = umap_labels['labels'] >= -1
    unit_presence = unit_presence[clusterIdx]
    unit_tier = unit_tier[clusterIdx]
    unit_item_count = unit_item_count[clusterIdx]
    placement = placement[clusterIdx]

    # Binarize the placement data
    placement = placement['placement']  <= 4

    unit_presence = pd.concat([unit_presence,unit_item_count],axis=1)
    unit_presence = pd.concat([unit_presence,unit_tier],axis=1) 

    return unit_presence, placement