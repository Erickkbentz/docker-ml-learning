import numpy as np
import pandas as pd
from tensorflow.keras.datasets import cifar10

# Load CIFAR-10 dataset
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

# Combine train and test data
data = np.concatenate((x_train, x_test), axis=0)
labels = np.concatenate((y_train, y_test), axis=0)

# Flatten the images and create a DataFrame
data_flattened = data.reshape(data.shape[0], -1)
df = pd.DataFrame(data_flattened)
df['label'] = labels

# Preprocess data (example: normalize pixel values)
df.iloc[:, :-1] = df.iloc[:, :-1] / 255.0

# Save preprocessed data for training script
df.to_csv('/data/training_data.csv', index=False)