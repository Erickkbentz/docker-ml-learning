import pandas as pd
import argparse

def preprocess_titanic_data():
    # Load the Titanic dataset from a URL
    url = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
    data = pd.read_csv(url)

    # Select relevant features and target
    features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
    target = 'Survived'

    # Handle missing values
    data = data.assign(Age=data['Age'].fillna(data['Age'].median()))
    data = data.assign(Embarked=data['Embarked'].fillna(data['Embarked'].mode()[0]))

    # Convert categorical features to numerical
    data['Sex'] = data['Sex'].map({'male': 0, 'female': 1})
    data['Embarked'] = data['Embarked'].map({'C': 0, 'Q': 1, 'S': 2})

    # Select features and target
    X = data[features]
    y = data[target]

    # Combine features and target into a single DataFrame
    processed_data = pd.concat([X, y], axis=1)

    return processed_data

def main(args):
    # Preprocess the Titanic dataset
    data = preprocess_titanic_data()

    # Save the preprocessed dataset to a CSV file
    data.to_csv(args.output_path, index=False)
    print(f"Data saved to {args.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate and preprocess the Titanic dataset.')
    parser.add_argument('--output_path', type=str, default='titanic_processed.csv', help='Output file path.')

    args = parser.parse_args()
    main(args)