# Date: 23/06/2023
# Name: Vivian Witting
# Project: Evaluation and comparison of privacy-preserving techniques for
#          distributed medical image processing.
# University of Amsterdam
# This file contains functions to measure the performance of techniques.
# ------------------------------------------------------------------------

import time
import psutil
import requests
import ast
import numpy as np
from flask import Flask, jsonify
from skimage.metrics import structural_similarity as ssim

app = Flask(__name__)

# This function computate the mse and ssim by manually applying the formulas
# and return them to the main function.
def compute_loss(original_data, private_data):
    mse = np.mean((original_data.astype(float) - private_data.astype(float)) ** 2)
    ssims = ssim(original_data.astype(float), private_data.astype(float))
    return float(mse), ssims

# This function measures the performance of HE, based on CPU utilization,
# time, and accuracy.
@app.route('/evaluate_result', methods=['GET'])
def evaluate_result():
    evaluation_results = []

    # Retrieve results of the computation on original data.
    response = requests.get("http://127.0.0.1:5000/plain_results")
    plain_results = response.json()
    start_time = time.time()

    # Retrieve results of the computation on encrypted data.
    response = requests.get("http://127.0.0.1:5000/encrypted_results")
    encrypted_results = response.json()
    cpu_usage_after = psutil.cpu_percent()

    end_time = time.time()

    processing_time = end_time - start_time
    encrypted_results = ast.literal_eval(encrypted_results[0])

    mse, ssims = compute_loss(np.array(plain_results[0]), np.array(encrypted_results))

    evaluation_results.append({
        'processing_time': processing_time,
        'cpu_usage_after': cpu_usage_after,
        'similarity (-1,1)': ssims,
        'mse': mse
    })

    return jsonify(evaluation_results)

# This function measures the performance of the Laplace distribution and
# Gaussian blur, based on CPU utilization, time, and accuracy.
@app.route('/evaluate_data', methods=['GET'])
def evaluate_data():
    # Perform utility and efficiency evaluation for each image
    evaluation_results = []

    response = requests.get("http://127.0.0.1:5000/original_images")
    original_images = response.json()
    base_time = time.time()

    response = requests.get("http://127.0.0.1:5000/processed_images")
    processed_images = response.json()

    cpu_usage_after = psutil.cpu_percent()
    end_time = time.time()

    processing_time = end_time - base_time

    mse, ssims = compute_loss(np.array(original_images), np.array(processed_images))

    evaluation_results.append({
        'processing_time': processing_time,
        'cpu_usage_after': cpu_usage_after,
        'similarity (-1,1)': ssims,
        'mse': mse
    })

    return jsonify(evaluation_results)

# Start the Flask app
if __name__ == '__main__':
    app.run(port=5010)