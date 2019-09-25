#!/usr/bin/env python3

from __init__ import latest_model, text_to_sequences, words_to_sequences
import os
import sys


def print_score(right):
	print(f"{(1 - right) * 100 :11.4f}% Liberal")
	print(f"{right * 100 :11.4f}% Conservative")


tokenizer, model = latest_model()

if len(sys.argv) > 1:
	os.chdir(os.path.join("input", sys.argv[1]))

	articles = sys.argv[2:] if len(sys.argv) > 2 else os.listdir()
	right = 0

	for name in articles:
		with open(name, "r") as file:
			seqs = words_to_sequences(tokenizer, file.read().splitlines())
			right += model.predict(seqs)[0][0]

	print_score(right / len(articles))

else:
	while True:
		print_score(model.predict(text_to_sequences(tokenizer, input("> ")))[0][0])
