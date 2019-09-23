#!/usr/bin/env python3

from __init__ import source_bias, words_to_sequences, lsources, usources
from keras.callbacks import ModelCheckpoint
from keras.layers import Dense, Embedding, GaussianNoise, GRU
from keras.models import Sequential
from keras.optimizers import Adam
from keras.preprocessing.text import Tokenizer, tokenizer_from_json
import math
import os
import random

os.makedirs("models", exist_ok=True)
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

model.summary()
print()

model.compile(optimizer=Adam(),
              loss="categorical_crossentropy",
              metrics=["accuracy"])


def source_articles(sources):
	return [(s, n) for s in sources for n in os.listdir(os.path.join("input", s))]


# Save after each epoch
articles = source_articles(lsources)
callbacks = [ModelCheckpoint(os.path.join("models",
                                          "model-{epoch:02d}-{loss:.4f}.h5"))]


def input_generator():
	while True:
		random.shuffle(articles)

		for source, name in articles:
			if source in lsources:
				bias = source_bias(source)
			else:
				bias = predictions[name]

			with open(os.path.join("input", source, name), "r") as file:
				yield (words_to_sequences(file.read().splitlines()), bias)


# Train on labeled data
model.fit_generator(input_generator(),
                    steps_per_epoch=len(articles),
                    epochs=5, callbacks=callbacks)


# Add predictions for unlabeled data
unlabeled = source_articles(usources)
articles += unlabeled


def predict_generator():
	for source, name in unlabeled:
		with open(os.path.join("input", source, name), "r") as file:
			yield words_to_sequences(file.read.splitlines())


predictions = model.predict_generator(predict_generator())

# Train on a mix of labeled and unlabeled data
model.fit_generator(input_generator,
                    steps_per_epoch=len(articles),
                    epochs=2, callbacks=callbacks,
                    initial_epoch=5)
