from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from utils.model_utils import load_data, plot_coefficients
from sklearn.metrics import roc_curve, auc

import pandas as pd

model_coeffs = {}
model_perf = pd.DataFrame(columns=['comp_id','train_acc','test_acc','auc','data_size'])

for i in range(0,16):
    if i != 3:
        continue

    print("Running model for comp: ", i)

    unit_presence, placement = load_data(-1)

    # Print duplicate rows
    print("Duplicate rows: ", unit_presence.duplicated().sum())

    # Print dataset size
    print("Dataset size: ", unit_presence.shape)

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(unit_presence, placement, test_size=0.2, random_state=42)


    # Train logistic regression model
    model = LogisticRegression(max_iter=5000, penalty='l1', solver='saga', C=0.1)
    model.fit(X_train, y_train)

    # Print train accuracy
    print("Train accuracy: ", model.score(X_train, y_train))

    # Print test accuracy
    print("Test accuracy: ", model.score(X_test, y_test))

    # Print AUC
    y_pred = model.predict_proba(X_test)
    fpr, tpr, _ = roc_curve(y_test, y_pred[:,1])
    auc_score = auc(fpr, tpr)
    print("AUC: ", auc_score)

    # Create data from from coefficients
    model_coeffs[i] = pd.DataFrame({'unit':unit_presence.columns,'coefs':model.coef_[0]})

    # Add model performance to model_perf
    model_perf.loc[i,'comp_id'] = i
    model_perf.loc[i,'train_acc']  = model.score(X_train, y_train)
    model_perf.loc[i,'test_acc'] = model.score(X_test, y_test)
    model_perf.loc[i,'auc'] = auc_score
    model_perf.loc[i,'data_size'] = unit_presence.shape[0]

    # Print space
    print("\n")



    # plot_coefficients(model.coef_[0], unit_presence)
print(model_perf.head())
# file_name = 'model_coeffs.pkl'
# with open(file_name, 'wb') as f:
#     pd.to_pickle(model_coeffs, f)

# model_perf.to_csv('model_perf.csv', index=False)