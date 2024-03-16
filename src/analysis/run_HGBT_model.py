from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from utils.model_utils import plot_best_model, load_data

def main():

    # Load the data
    unit_presence, placement = load_data()

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(unit_presence, placement, test_size=0.2, random_state=42)

    # Define hyperparameters grid
    param_grid = {
        'learning_rate': [0.2],
        'max_leaf_nodes': [30],
        'min_samples_leaf': [256],
        'max_iter': [250],
        'l2_regularization': [0.5],
    }

    # Create CV folds
    cv = KFold(n_splits=10, random_state=42, shuffle=True)

    # Create the model
    model = HistGradientBoostingClassifier(random_state=42,early_stopping=True)

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

    pass




if __name__ == "__main__":  
    main()