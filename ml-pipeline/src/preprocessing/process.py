import argparse
import numpy as np
from tensorflow.keras.datasets import cifar10
import os

TRAINING_DATA_FILE_NAME = 'training_data.npz'

def main(args):
    output_path = args.output_path
    fraction = args.fraction
    normalize_value = args.normalize_value

    # Load CIFAR-10 dataset
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()

    # Calculate the number of samples to load based on the fraction
    num_train_samples = int(len(x_train) * fraction)
    num_test_samples = int(len(x_test) * fraction)

    # Slice the data arrays to load only the specified fraction
    x_train = x_train[:num_train_samples]
    y_train = y_train[:num_train_samples]
    x_test = x_test[:num_test_samples]
    y_test = y_test[:num_test_samples]

    print("Done loading data")

    # Normalize pixel values to be between 0 and 1
    x_train = x_train / normalize_value
    x_test = x_test / normalize_value

    # Save the data as .npz file
    save_path = os.path.join(output_path, TRAINING_DATA_FILE_NAME)
    np.savez_compressed(save_path, x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
    print(f"Data saved to {save_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output_path',
        type=str,
        help='Path to save preprocessed data'
    )
    parser.add_argument(
        '--fraction',
        type=float,
        default=1.0,
        help='Fraction of the CIFAR-10 data to load (between 0 and 1)'
    )
    parser.add_argument(
        '--normalize_value',
        type=float,
        default=255.0,
        help='Value to normalize pixel values by'
    )
    args = parser.parse_args()

    print('Data preprocessing started...')
    main(args)
    print('Data preprocessing complete.')