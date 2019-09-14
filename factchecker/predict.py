#!/usr/bin/env python3

from __init__ import latest_model, text_to_sequences

tokenizer, model = latest_model()

while True:
	left, right = model.predict(text_to_sequences(tokenizer, input("> ")))

	print(f"    {left * 100}% Liberal")
	print(f"    {right * 100}% Conservative")
