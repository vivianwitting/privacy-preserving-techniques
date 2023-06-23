# Date: 23/06/2023
# Name: Vivian Witting
# Project: Evaluation and comparison of privacy-preserving techniques for
#          distributed medical image processing.
# University of Amsterdam
# This file contains functions to apply privacy-preserving techniques.
# ------------------------------------------------------------------------

import os
import json
import pydicom
import numpy as np
from Pyfhel import Pyfhel
from flask import Flask, jsonify

data_ct = "images10"
data_list = data_ct

epsilon = 0.8 # Privacy parameter
sensitivity = 1.0
delta = 10e-4 # Probability of failing to maintain privacy

app = Flask(__name__)

bfv_params = {
    'scheme': 'BFV',    # can also be 'bfv'
    'n': 2**15,         # Polynomial modulus degree, the num. of slots per plaintext,
                        #  of elements to be encoded in a single ciphertext in a
                        #  2 by n/2 rectangular matrix (mind this shape for rotations!)
                        #  Typ. 2^D for D in [10, 16]
    't': 65537,         # Plaintext modulus. Encrypted operations happen modulo t
                        #  Must be prime such that t-1 be divisible by 2^N.
    't_bits': 20,       # Number of bits in t. Used to generate a suitable value
                        #  for t. Overrides t if specified.
    'sec': 128,         # Security parameter. The equivalent length of AES key in bits.
                        #  Sets the ciphertext modulus q, can be one of {128, 192, 256}
                        #  More means more security but also slower computation.
}
app = Flask(__name__)


# Differential privacy
def add_laplace_noise(image):
    shape = image.shape
    noise = np.random.laplace(scale=sensitivity/epsilon, size=shape)
    noisy_data = np.round(image + noise).astype(int)
    return noisy_data

# Differential privacy
def add_gaussian_blur(data):
    # Compute the standard deviation (sigma) based on epsilon and sensitivity
    sigma = (2 * (sensitivity**2) * np.log(1.25/delta)) / (epsilon**2)
    noisy_data = data + np.random.normal(0, sigma, size=data.shape)
    return noisy_data

# Homomorphic encryption
def homomorphic_encryption(pixel_array, bfv_params):

    # Resize the image to fit the target number of slots
    HE = Pyfhel()           # Creating empty Pyfhel object
    HE.contextGen(**bfv_params)  # Generate context for bfv scheme
    HE.keyGen()             # Key Generation: generates a pair of public/secret keys
    HE.relinKeyGen()        # Relinearization key generation

    # Resize the image to fit the target number of slots
    ptxt = HE.encodeInt(pixel_array)
    ctxt = HE.encryptPtxt(ptxt)

    # cc_mull = ctxt * ctxt
    cc_sum = ctxt + ctxt

    d_result = HE.decryptInt(cc_sum)

    return json.dumps(d_result.tolist())

# ---------------- Communicating to other micro service --------------------


# Communicates plain results of the computation (for comparison with HE).
@app.route('/plain_results', methods=['GET'])
def plain_results():
    # Retrieve all DICOM image files in the "images" folder
    image_names = os.listdir(data_list)
    processed_images = []

    for image_name in image_names:
        image_path = os.path.join(data_list, image_name)
        image = pydicom.dcmread(image_path)
        converted_array = image.pixel_array.flatten()[:bfv_params['n']].astype(np.int64)
        # acMul = converted_array * converted_array
        acSum = converted_array + converted_array
        processed_images.append(acSum.tolist())

    return jsonify(processed_images)

# Communicates encrypted data after the homomorphic encryption applied.
@app.route('/encrypted_results', methods=['GET'])
def encrypted_results():
    # Retrieve all DICOM image files in the "images" folder
    image_names = os.listdir(data_list)
    processed_images = []

    for image_name in image_names:
        image_path = os.path.join(data_list, image_name)
        image = pydicom.dcmread(image_path)
        converted_array = image.pixel_array.flatten()[:bfv_params['n']].astype(np.int64)
        cM = homomorphic_encryption(converted_array, bfv_params)
        processed_images.append(cM)

    return jsonify(processed_images)

# Communicates encrypted data after the Laplace or Gaussion noise is applied.
@app.route('/processed_images', methods=['GET'])
def processed_images():
    # Retrieve all DICOM image files in the "images" folder
    image_names = os.listdir(data_list)
    processed_images = []

    for image_name in image_names:
        image_path = os.path.join(data_list, image_name)
        image = pydicom.dcmread(image_path)
        image = image.pixel_array

        # Apply differential privacy to each image using Laplace noise
        # proc_image = add_laplace_noise(image)
        proc_image = add_gaussian_blur(image)

        processed_images.append(proc_image.tolist())

    return jsonify(processed_images)

# Communicates the original plain data.
@app.route('/original_images', methods=['GET'])
def original_images():
    # Retrieve all DICOM image files in the "images" folder
    image_names = os.listdir(data_list)
    original_images = []

    for image_name in image_names:
        image_path = os.path.join(data_list, image_name)
        image = pydicom.dcmread(image_path)

        original_images.append(image.pixel_array.tolist())

    return jsonify(original_images)


# Start the Flask app
if __name__ == '__main__':
    app.run(port=5000)
