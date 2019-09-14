from keras.models import load_model
from keras.preprocessing.text import tokenizer_from_json
import numpy
import os
import re

# Sources and the left-component of their bias (output)
sources = {
	"thinkprogress": 0.9,
	"huffpost": 0.85,
	"theblaze": 0.1,
	"infowars": 0
}

word_regex = re.compile(r"(?:[A-Z]\.)+|(?:[a-zA-Z]+(?:'[a-zA-Z])?-?)+")


def latest_model():
	# Load the latest saved tokenizer and model
	with open(os.path.join("models", "tokenizer.json"), "r") as file:
		tokenizer = tokenizer_from_json(file.read())

	name = max(f for f in os.listdir("models") if f.endswith(".h5"))
	model = load_model(os.path.join("models", name))

	return tokenizer, model


def source_bias(source):
	return numpy.array([(sources[source], 1 - sources[source])])


def words_to_sequences(tokenizer, words):
	sequences = tokenizer.texts_to_sequences([words])
	sequences[0] += [0] * (100 - len(sequences[0]))

	return numpy.array(sequences)


def text_to_sequences(tokenizer, text):
	text = text.replace("’", "'")
	words = [w.lower() for w in word_regex.findall(text)]

	return words_to_sequences(words)
