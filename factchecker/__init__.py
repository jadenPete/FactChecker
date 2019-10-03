from keras import backend as K
from keras.models import load_model
from keras.preprocessing.text import tokenizer_from_json
import numpy
import os
import re

# Sources and the right-component of their bias (output)
lsources = {
	"thinkprogress": 0.75 / 7,
	"huffpost":         1 / 7,
	"ap":            3.25 / 7,
	"theeconomist":  3.75 / 7,
	"theblaze":         6 / 7,
	"infowars":      6.75 / 7
}

usources = [
	"cnn", "foxnews"  # "washingtonpost"
]

word_regex = re.compile(r"(?:[A-Z]\.)+|(?:[a-zA-Z]+(?:'[a-zA-Z])?-?)+")


def accuracy(y_true, y_pred):
	# What percentage of scores are < a section off
	return K.mean(K.less(K.abs(K.update_sub(y_true, y_pred)), 1 / 7))


def source_bias(source):
	return numpy.array([lsources[source]])


def latest_model():
	# Load the latest saved tokenizer and model
	with open(os.path.join("models", "tokenizer.json"), "r") as file:
		tokenizer = tokenizer_from_json(file.read())

	name = max(f for f in os.listdir("models") if f.endswith(".h5"))
	model = load_model(os.path.join("models", name), custom_objects={
		"accuracy": accuracy
	})

	return tokenizer, model


def words_to_sequences(tokenizer, words):
	sequences = tokenizer.texts_to_sequences([words])
	sequences[0] += [0] * (100 - len(sequences[0]))

	return numpy.array(sequences)


def text_to_words(text):
	return [w.lower() for w in word_regex.findall(text.replace("’", "'"))]


def text_to_sequences(tokenizer, text):
	return words_to_sequences(tokenizer, text_to_words(text))
