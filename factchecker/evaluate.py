#!/usr/bin/env python3

from __init__ import latest_model, source_bias, words_to_sequences
import os
import sys

source = sys.argv[1]
tokenizer, model = latest_model()

os.chdir(os.path.join("input", source))

articles = os.listdir()


def input_generator():
	for name in articles:
		with open(name, "r") as file:
			yield (words_to_sequences(tokenizer, file.read().splitlines()),
			       source_bias(source))


loss, accuracy = model.evaluate_generator(input_generator(),
                                          steps=len(articles))

print(f"\nLoss: {loss :.4f}")
print(f"Accuracy: {accuracy * 100}%")
