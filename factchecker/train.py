#!/usr/bin/env python3

from __init__ import latest_model, source_bias, words_to_sequences, lsources, usources
from keras.callbacks import ModelCheckpoint
from keras.layers import Dense, Embedding, GaussianNoise, GRU
from keras.models import Sequential
from keras.optimizers import Adam
from keras.preprocessing.text import Tokenizer, tokenizer_from_json
import math
import numpy
import os
import random


def source_articles(sources):
	return [(s, n) for s in sources for n in os.listdir(os.path.join("input", s))]


def generate_tokenizer():
	tokenizer_path = os.path.join("models", "tokenizer.json")

	# Load the tokenizer
	try:
		with open(tokenizer_path, "r") as file:
			tokenizer = tokenizer_from_json(file.read())
	except FileNotFoundError:
		# Already in lowercase
		tokenizer = Tokenizer(lower=False)

		# Build the tokenizer
		for source in list(lsources) + usources:
			for name in os.listdir(os.path.join("input", source)):
				with open(os.path.join("input", source, name), "r") as file:
					tokenizer.fit_on_texts([file.read().splitlines()])

		# Save the tokenizer
		with open(tokenizer_path, "w") as file:
			file.write(tokenizer.to_json())

	return tokenizer


def generate_model(tokenizer, articles):
	# Given the mean of the squared normal distribution,
	# we can adjust the standard deviation so the norm
	# of Gaussian noise averages to a desired number
	norm = 1
	word_dim = 100

	model = Sequential([
		Embedding(len(tokenizer.word_index) + 1, word_dim, mask_zero=True),
		GaussianNoise(norm / math.sqrt(word_dim)),
		GRU(100),
		Dense(100, activation="relu"),
		Dense(2, activation="softmax")
	])

	model.compile(optimizer=Adam(),
	              loss="categorical_crossentropy",
	              metrics=["accuracy"])

	# Train on labeled data
	model.fit_generator(fit_generator(articles),
	                    steps_per_epoch=len(articles),
	                    epochs=5, callbacks=callbacks)

	return model


def fit_generator(articles, predictions=None):
	while True:
		random.shuffle(articles)

		for source, name in articles:
			if source in lsources:
				bias = source_bias(source)
			else:
				bias = numpy.array([predictions[(source, name)]])

			with open(os.path.join("input", source, name), "r") as file:
				yield (words_to_sequences(tokenizer, file.read().splitlines()), bias)


def predict_generator(articles):
	for source, name in articles:
		with open(os.path.join("input", source, name), "r") as file:
			yield words_to_sequences(tokenizer, file.read().splitlines())


os.makedirs("models", exist_ok=True)

articles = source_articles(lsources)
callbacks = [ModelCheckpoint(os.path.join("models",  # Save after each epoch
                                          "model-{epoch:02d}-{loss:.4f}.h5"))]

# Load the model, or train a new one
try:
	tokenizer, model = latest_model()
except ValueError:
	tokenizer = generate_tokenizer()
	model = generate_model(tokenizer, articles)

model.summary()
print()

# Add unlabeled articles
unlabeled = source_articles(usources)
articles.extend(unlabeled)

# Generate predictions
output = model.predict_generator(predict_generator(unlabeled),
                                 steps=len(unlabeled))

# Retrain
model.fit_generator(fit_generator(articles, dict(zip(unlabeled, output))),
                    steps_per_epoch=len(articles),
                    epochs=7, callbacks=callbacks,
                    initial_epoch=5)
