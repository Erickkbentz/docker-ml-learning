from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pandas as pd
import argparse
import os

def load_data(data_path=None):
    if data_path:
        print(f"Loading data from {data_path}")
        data = pd.read_csv(data_path)
        X = data.iloc[:, :-1].values
        y = data.iloc[:, -1].values
    else:
        raise ValueError("Data path not provided")
    return X, y

def main(args):
    # Load the dataset
    X, y = load_data(args.data_path)

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_size, random_state=args.random_state)

    # Define the model
    clf = RandomForestClassifier(random_state=args.random_state, max_features=args.max_features)

    # Define the parameter grid
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_features': ['sqrt', 'log2', 1.0, 0.5],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    # Perform grid search
    grid_search = GridSearchCV(estimator=clf, param_grid=param_grid, cv=5, n_jobs=-1)
    grid_search.fit(X_train, y_train)

    # Get the best model
    best_clf = grid_search.best_estimator_

    # Make predictions on the test set
    y_pred = best_clf.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    cm = confusion_matrix(y_test, y_pred)

    print("Confusion Matrix:")
    print(cm)
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Model accuracy: {accuracy:.2f}")
    print(f"Model precision: {precision:.2f}")
    print(f"Model recall: {recall:.2f}")
    print(f"Model F1 score: {f1:.2f}")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train a RandomForestClassifier on the dataset.')
    parser.add_argument('--data_path', type=str, default=None, help='Path to the dataset CSV file.')
    parser.add_argument('--test_size', type=float, default=0.2, help='Proportion of the dataset to include in the test split.')
    parser.add_argument('--random_state', type=int, default=42, help='Random seed.')
    parser.add_argument('--max_features', type=str, default='sqrt', help='Number of features to consider when looking for the best split.')
    parser.add_argument('--output_path', type=str, default=os.environ.get("MODEL_OUTPUT_PATH", "model"), help='Output file path.')

    args = parser.parse_args()
    main(args)