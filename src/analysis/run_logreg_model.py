from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import classification_report, roc_curve, roc_auc_score
from sklearn import svm
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

# Set the working directory
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../../Data/Processed/compAnalysis.h5')

# Load h5 from data/processed
with pd.HDFStore(filename,'r') as store:
    unit_presence = store.get('unit_presence')
    unit_tier = store.get('unit_tier')
    unit_item_count = store.get('unit_item_count')
    placement = store.get('placement')
    umap_labels = store.get('umap_labels')
    puuids = store.get('puuid')

# Get a count of occurrences of the unique puuid
puuid_counts = puuids['puuid'].value_counts()
print(puuid_counts.unique())

#  Keep data where cluster id is 0
clusterIdx = umap_labels['labels'] > -1
unit_presence = unit_presence[clusterIdx]
unit_tier = unit_tier[clusterIdx]
unit_item_count = unit_item_count[clusterIdx]
placement = placement[clusterIdx]

# Print average placement for each unique cluster label -> THIS SHOULD BE A REGRESSION FIT AS WELL
mean_placement = placement.groupby(umap_labels['labels']).mean().sort_values(by='placement')
print((4.5-mean_placement).clip(0,4.5))


# Binarize the placement data
placement = placement['placement']  <= 4


# Create a logistic regression models for each variable
lambda_ = 1
logreg = LogisticRegression(C=lambda_,class_weight='balanced')

# Fit the model
logreg.fit(unit_presence, placement)
# logreg.fit(unit_tier, placement)
# logreg.fit(unit_item_count, placement)


# Print top 5 units with the highest coefficients
i = logreg.coef_.argsort()[:,:][0]
i_f = np.flip(i)
coefs = logreg.coef_[0]
print(np.exp(coefs[i]))
print(unit_presence.columns[i])

# Put the coefficients in a dataframe
coefs_df = pd.DataFrame({'unit':unit_presence.columns[i_f],'coefs':np.exp(coefs[i_f])/np.max(np.exp(coefs[i_f]))})

# Plot relative coeff values with columns as x-axis
fig = plt.figure()
ax = fig.add_subplot(111)
plt.bar(np.arange(len(unit_presence.columns)),np.exp(coefs[i_f])/np.max(np.exp(coefs[i_f])))
plt.xticks(rotation=75)
ax.set_xticks(np.arange(len(unit_presence.columns)))
ax.set_xticklabels(unit_presence.columns[i_f])
# plt.show()

# Save coefficients to a h5 file
with pd.HDFStore(filename, 'a', complevel=9, complib='blosc') as store:
    # Remove existing label if it exists
    if 'logreg_coefs' in store.keys():
        store.remove('logreg_coefs')
    # Save the new label
    store.put('logreg_coefs', coefs_df)


# Plot ROC curve
# y_pred = logreg.predict(unit_presence)
# fpr, tpr,_ = roc_curve(placement, y_pred)
# auc = roc_auc_score(placement, y_pred)
# plt.plot(fpr, tpr, label="auc="+str(auc))
# plt.legend(loc=4)
# plt.show()

# Fit a SVM model
# clf = svm.SVC(kernel='linear')
# clf.fit(unit_presence, placement)


# i = clf.coef_.argsort()[:,1:10][0]
# print(clf.coef_[0][i])
# print(unit_presence.columns[i])


# # plot auc
# y_pred = clf.predict(unit_presence)
# fpr, tpr,_ = roc_curve(placement, y_pred)
# auc = roc_auc_score(placement, y_pred)
# plt.plot(fpr, tpr, label="auc="+str(auc))
# plt.legend(loc=4)
# plt.show()

