import os
import joblib
import argparse
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, request, jsonify

app = Flask(__name__)

def load_trained_model(model_path):
    return load_model(model_path)


@app.route('/predict', methods=['POST'])
def predict():
    img_file = request.files['file']
    
    # Load the image and preprocess it
    img = image.load_img(img_file, target_size=(32, 32))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array.astype('float32') / 255.0

    # Make a prediction
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)

    # Return the prediction as a JSON response
    return jsonify({'predicted_class': int(predicted_class[0])})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serve the trained model.')
    parser.add_argument('--model_path', type=str, default=os.path.join(os.getcwd(), "cnn_mode.h5"), help='Path to the trained model.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on.')
    
    args = parser.parse_args()

    print(f"Loading model from {args.model_path}")
    model = load_trained_model(args.model_path)

    app.run(host='0.0.0.0', port=args.port)
    print(f"Server running on port {args.port}")
