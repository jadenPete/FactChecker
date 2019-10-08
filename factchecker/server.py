#!/usr/bin/env python3

from __init__ import latest_model, text_to_sequences
from flask import Flask, abort, request
import json
import os

app = Flask(__name__)

with open(os.path.join(os.pardir, "selectors.json"), "r") as file:
	selectors = file.read()


@app.route("/predict", methods=["POST"])
def predict():
	text = request.get_json(True)

	if not isinstance(text, str):
		abort(400)
	else:
		return json.dumps(float(model.predict(text_to_sequences(tokenizer, text))[0][0]))


@app.route("/selectors.json")
def selectors_json():
	return selectors.encode()


if __name__ == "__main__":
	tokenizer, model = latest_model()
	app.run(port=8080, threaded=False)
