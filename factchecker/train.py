#!/usr/bin/env python3

from __init__ import source_bias, words_to_sequences, sources
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
	for source in sources:
		for name in os.listdir(os.path.join("input", source)):
			with open(os.path.join("input", source, name), "r") as file:
				tokenizer.fit_on_texts([file.read().splitlines()])

	# Save the tokenizer
	with open(tokenizer_path, "w") as file:
		file.write(tokenizer.to_json())


def input_generator():
	# Agregate every article and its source
	articles = [(s, n) for s in sources
	            for n in os.listdir(os.path.join("input", s))]

	# Randomly yield the data forever
	while True:
		random.shuffle(articles)

		for source, name in articles:
			with open(os.path.join("input", source, name), "r") as file:
				yield (words_to_sequences(file.read().splitlines()), source_bias(source))


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

# Save after each epoch
model.fit_generator(input_generator(),
                    steps_per_epoch=tokenizer.document_count,
                    epochs=10, callbacks=[
	ModelCheckpoint(os.path.join("models", "model-{epoch:02d}-{loss:.4f}.h5"))
])
