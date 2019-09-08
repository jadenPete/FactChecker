#!/usr/bin/env python3

from filter import get_words
from keras.models import load_model
from keras.preprocessing.text import tokenizer_from_json
import numpy
import os

os.chdir("models")

# Load the latest saved tokenizer and model
with open("tokenizer.json", "r") as file:
	tokenizer = tokenizer_from_json(file.read())

print("   * Tokenizer loaded")
model = load_model(max(f for f in os.listdir() if f.endswith(".h5")))
print("   * Model loaded\n")

while True:
	words = tokenizer.texts_to_sequences([get_words(input("> "))])
	words[0] += [0] * (100 - len(words[0]))

	left, right = model.predict(numpy.array(words))[0]
	print(f"    {left * 100}% Liberal\n    {right * 100}% Conservative")
