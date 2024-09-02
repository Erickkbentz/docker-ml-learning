import os
import argparse
import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

def main(args):
    
    # Load preprocessed data
    try:
        df = pd.read_csv(args.input_path)
        print(f"Loaded data from {args.input_path}")
    except FileNotFoundError:
        print(f"File not found: {args.input_path}")
        raise

    # Separate features and labels
    X = df.iloc[:, :-1].values
    y = df['label'].values

    # Reshape features to original image dimensions (32x32x3)
    X = X.reshape(-1, 32, 32, 3)

    # Normalize pixel values (ensure it's in the correct range)
    X = X.astype('float32') / 255.0

    # Convert labels to one-hot encoding
    y = to_categorical(y, 10)

    # Manually split dataset
    num_samples = X.shape[0]
    indices = np.arange(num_samples)
    np.random.shuffle(indices)

    split_index = int(num_samples * 0.8)
    train_indices = indices[:split_index]
    test_indices = indices[split_index:]

    x_train, x_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]

    # Define CNN model
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(10, activation='softmax')
    ])

    # Compile model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train model
    print("Starting model training...")
    model.fit(x_train, y_train, epochs=args.epochs, batch_size=args.batch_size, validation_data=(x_test, y_test))

    # Evaluate model
    loss, accuracy = model.evaluate(x_test, y_test)
    print(f"Model accuracy: {accuracy}")

    # Save the model
    save_path = os.path.join(args.output_path, 'cnn_model.h5')
    model.save(save_path)
    print(f"Model saved to {save_path}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train a Sequential model on the dataset.')
    parser.add_argument('--input_path', type=str, required=True, help='Path to the dataset CSV file.')
    parser.add_argument('--output_path', type=str, default=os.path.join(os.getcwd(), "cnn_model.h5"), help='Output file path.')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs.')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size.')

    args = parser.parse_args()
    main(args)