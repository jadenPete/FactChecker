#!/usr/bin/env python3

from __init__ import latest_model, text_to_sequences, words_to_sequences
import os
import sys


def print_score(left):
	print(f"    {left * 100 :8.4f}% Liberal")
	print(f"    {(1 - left) * 100 :8.4f}% Conservative")


tokenizer, model = latest_model()

if len(sys.argv) > 1:
	os.chdir(os.path.join("input", sys.argv[1]))

	articles = sys.argv[2:] if len(sys.argv) > 2 else os.listdir()
	left = 0

	for name in articles:
		with open(name, "r") as file:
			seqs = words_to_sequences(tokenizer, file.read().splitlines())
			left += model.predict(seqs)[0][0]

	print_score(left / len(articles))

else:
	while True:
		print_score(model.predict(text_to_sequences(tokenizer, input("> ")))[0])
