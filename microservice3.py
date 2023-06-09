from flask import Flask, jsonify
import numpy as np
import requests


app = Flask(__name__)

@app.route('/third_party', methods=['GET'])
def add_to_first():
    response = requests.get("http://127.0.0.1:5000/original_images")
    input_of_three = response.json()
    response = requests.get("http://127.0.0.1:5010/second_party")
    retrieved = response.json()

    third = retrieved + input_of_three

    return jsonify(third)

if __name__ == "__main__":
    app.run(port=5015)
