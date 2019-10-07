#!/usr/bin/env python3

from __init__ import latest_model, text_to_sequences
from flask import Flask, request
import os

app = Flask(__name__)
tokenizer, model = latest_model()

with open(os.path.join(os.pardir, "selectors.json"), "r") as file:
	selectors = file.read()


@app.route("/predict", methods=["POST"])
def predict():
	return model.predict(text_to_sequences(tokenizer, request.json))[0][0]


@app.route("/selectors.json")
def selectors_json():
	return selectors.encode()
