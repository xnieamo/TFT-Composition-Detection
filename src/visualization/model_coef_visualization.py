import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import pearsonr

dirname = os.path.dirname(__file__)
h5_filename = os.path.join(dirname, '../../Data/Processed/model_perf.csv')


model_perf = pd.read_csv(h5_filename)

model_perf.info()

# plot_columns = ['train_acc', 'test_acc']
# ax = model_perf[plot_columns].plot(kind='bar')
# ax.axhline(y=0.5, color='k', linestyle='--')
# plt.ylabel('Acc/AUC')
# plt.xlabel('Composition ID')
# plt.show()

# Scatter plot
# x_vals = model_perf['data_size']
# y_vals = model_perf['test_acc']

# _, p_val = pearsonr(x_vals, y_vals)
# print("Pearson correlation: ", p_val)

# plt.scatter(x_vals, y_vals)
# plt.xscale('log')
# plt.xlabel('Cluster Size')
# plt.ylabel('Test Accuracy')
# plt.show()


file_name = os.path.join(dirname, '../../Data/Processed/model_coeffs.pkl')
with open(file_name, 'rb') as file:
    loaded_data_frames = pd.read_pickle(file)
model_coef = loaded_data_frames[0]
model_coef = model_coef[model_coef['unit'].str.contains('tier|item_count')]
model_coef = model_coef.sort_values(by='coefs', ascending=False)
model_coef['coefs'] = np.exp(model_coef['coefs']) - 1
model_coef.plot(kind='bar',x='unit', y='coefs', rot=75)
plt.xticks(ha='right')
plt.tight_layout()
plt.ylabel('Odds Ratio (Adjusted -1)')
plt.show()