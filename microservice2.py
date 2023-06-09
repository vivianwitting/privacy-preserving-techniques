import time
import psutil
import requests
import os
import pydicom
import ast
import sys
import numpy as np
from flask import Flask, jsonify
from skimage.metrics import structural_similarity as ssim

app = Flask(__name__)

def compute_loss(original_data, private_data):
    mse = np.mean((original_data.astype(float) - private_data.astype(float)) ** 2)
    ssims = ssim(original_data.astype(float), private_data.astype(float))
    return mse, ssims

@app.route('/evaluate_result', methods=['GET'])
def evaluate_result():
    cpu_usage_before = psutil.cpu_percent()
    evaluation_results = []

    response = requests.get("http://127.0.0.1:5000/plain_results")
    plain_results = response.json()
    start_time = time.time()

    response = requests.get("http://127.0.0.1:5000/encrypted_results")
    encrypted_results = response.json()
    cpu_usage_after = psutil.cpu_percent()

    end_time = time.time()

    processing_time = end_time - start_time
    encrypted_results = ast.literal_eval(encrypted_results[0])

    # mse, ssims = compute_loss(np.array(plain_results[0]), np.array(encrypted_results))

    evaluation_results.append({
        'processing_time': processing_time,
        'cpu_usage_after': cpu_usage_after,
        # 'similarity (-1,1)': ssims,
        'size of original': sys.getsizeof(plain_results),
        'size of decrypt': sys.getsizeof(encrypted_results)
        # 'mse': mse
    })

    return jsonify(evaluation_results)

@app.route('/second_party', methods=['GET'])
def add_to_first():
    response = requests.get("http://127.0.0.1:5000/original_images")
    input_of_two = response.json()
    response = requests.get("http://127.0.0.1:5000/processed_images")
    retrieved = response.json()

    second = retrieved + input_of_two

    return jsonify(second)

@app.route('/get_secure_sum', methods=['GET'])
def get_smc():
    response = requests.get("http://127.0.0.1:5000/secure_sum")
    retrieved = response.json()

    return jsonify(retrieved)


@app.route('/evaluate_data', methods=['GET'])
def evaluate_data():
    # Perform utility and efficiency evaluation for each image
    evaluation_results = []

    response = requests.get("http://127.0.0.1:5000/original_images")
    original_images = response.json()
    base_time = time.time()
    cpu_usage_before = psutil.cpu_percent()

    response = requests.get("http://127.0.0.1:5000/processed_images")
    processed_images = response.json()

    cpu_usage_after = psutil.cpu_percent()
    end_time = time.time()

    processing_time = end_time - base_time

    # mse, ssims = compute_loss(np.array(original_images), np.array(processed_images))

    evaluation_results.append({
        'processing_time': processing_time,
        'cpu_usage_after': cpu_usage_after,
        # 'similarity (-1,1)': ssims,
        # 'size of original': sys.getsizeof(original_images),
        # 'size of processed': sys.getsizeof(processed_images),
        # 'mse': mse
    })

    return jsonify(evaluation_results)

@app.route('/original_images', methods=['GET'])
def original_images():
    data_folder = "images2"
    # Retrieve all DICOM image files in the "images" folder
    image_names = os.listdir(data_folder)
    original_images = []

    for image_name in image_names:
        image_path = os.path.join(data_folder, image_name)
        image = pydicom.dcmread(image_path)

        original_images.append(image.pixel_array.tolist())

    return jsonify(original_images)

# Start the Flask app
if __name__ == '__main__':
    app.run(port=5010)

#     # Perform further computations on the result or use it as needed

#     return "Processing complete"
