from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from utils.model_utils import plot_best_model, load_data



unit_presence, placement = load_data(0)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(unit_presence, placement, test_size=0.2, random_state=42)

# Define hyperparameters grid, best found: {'C': 0.1, 'max_iter': 250, 'penalty': 'l1', 'solver': 'saga'}
param_grid = {
    'C': [0.1],
    'penalty': ['l1'], 
    'solver': ['saga'], 
    'max_iter': [250]
}

# Create CV folds
cv = KFold(n_splits=10, random_state=42, shuffle=True)

# Create the model
lambda_ = 1
model = LogisticRegression(class_weight='balanced')

# Create the grid search
grid_search = GridSearchCV(model, param_grid, cv=cv, scoring='accuracy', n_jobs=-1, verbose=3)
grid_search.fit(X_train, y_train)

# Print the best parameters
print("Best parameters found: ", grid_search.best_params_)
print("Best score found: ", grid_search.best_score_)

# Print run time
print("Run time: ", grid_search.cv_results_['mean_fit_time'].sum())

# Run best model on test data
best_model = grid_search.best_estimator_
plot_best_model(best_model, X_test, y_test)


# Print top 5 units with the highest coefficients
i = best_model.coef_[0:59]



# # Put the coefficients in a dataframe
# coefs_df = pd.DataFrame({'unit':unit_presence.columns[i_f],'coefs':np.exp(coefs[i_f])/np.max(np.exp(coefs[i_f]))})

# # Plot relative coeff values with columns as x-axis
# fig = plt.figure()
# ax = fig.add_subplot(111)
# # plt.bar(np.arange(len(unit_presence.columns)),np.exp(coefs[i_f])/np.max(np.exp(coefs[i_f])))
# barlist =plt.bar(np.arange(len(unit_presence.columns)),coefs[i_f])
# # [barlist[i].set_color('#ff7f0e') for i in [1,2]]
# # [barlist[i].set_color('#9467bd') for i in [13,14]]
# # [barlist[i].set_color('#7f7f7f') for i in [59]]
# plt.xticks(rotation=75)
# ax.set_xticks(np.arange(len(unit_presence.columns)))
# ax.set_xticklabels(unit_presence.columns[i_f])
# plt.ylabel('Coefficients')
# plt.title('Effect of unit presence on placement')
# plt.show()

# # Save coefficients to a h5 file
# # with pd.HDFStore(filename, 'a', complevel=9, complib='blosc') as store:
# #     # Remove existing label if it exists
# #     if 'logreg_coefs' in store.keys():
# #         store.remove('logreg_coefs')
# #     # Save the new label
# #     store.put('logreg_coefs', coefs_df)

