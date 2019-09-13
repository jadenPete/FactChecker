#!/usr/bin/env python3

from keras.callbacks import ModelCheckpoint
from keras.layers import Dense, Embedding, GRU
from keras.models import Sequential
from keras.optimizers import Adam
from keras.preprocessing.text import Tokenizer, tokenizer_from_json
import numpy
import os
import random

# Sources and the left-component of their bias (output)
sources = {
	"thinkprogress": 0.9,
	"huffpost": 0.85,
	"theblaze": 0.1,
	"infowars": 0
}

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
	articles = [(s, n) for s in sources for n in os.listdir(os.path.join("input", s))]

	# Randomly yield the data forever
	while True:
		random.shuffle(articles)

		for source, name in articles:
			with open(os.path.join("input", source, name), "r") as file:
				words = file.read().splitlines()
				bias = sources[source]

				yield (numpy.array(tokenizer.texts_to_sequences([words])),
				       numpy.array([[bias, 1 - bias]]))


model = Sequential([
	Embedding(len(tokenizer.word_index) + 1, 100, mask_zero=True),
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
