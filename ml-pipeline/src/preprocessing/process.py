import pandas as pd

# Load raw data
data = pd.read_csv('/data/raw_data.csv')

# Preprocess data (example: fill missing values)
data.fillna(0, inplace=True)

# Save preprocessed data
data.to_csv('/data/preprocessed_data.csv', index=False)