import os
import argparse
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

def main(args):
    
    # Load preprocessed data
    try:
        data = np.load(args.input_path)
        x_train = data['x_train']
        y_train = data['y_train']
        x_test = data['x_test']
        y_test = data['y_test']
        print(f"Loaded data from {args.input_path}")
    except FileNotFoundError:
        print(f"File not found: {args.input_path}")
        raise

    # Convert labels to one-hot encoding
    y_train = to_categorical(y_train, 10)
    y_test = to_categorical(y_test, 10)

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
    print("Starting training script...")
    parser = argparse.ArgumentParser(description='Train a Sequential model on the dataset.')
    parser.add_argument('--input_path', type=str, required=True, help='Path to the dataset NPZ file.')
    parser.add_argument('--output_path', type=str, default=os.path.join(os.getcwd(), "cnn_model.h5"), help='Output file path.')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs.')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size.')

    args = parser.parse_args()
    main(args)