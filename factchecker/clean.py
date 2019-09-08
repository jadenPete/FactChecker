#!/usr/bin/env python3

import os

os.chdir(os.path.join("input", "huffpost"))

words = ["download", "real", "life", "real", "news", "real",
         "voices", "help", "us", "tell", "more", "of",
         "the", "stories", "that", "matter", "from", "voices",
         "that", "too", "often", "remain", "unheard", "join",
         "huffpost", "plus"]

for name in os.listdir():
	with open(name, "r") as file:
		article = file.read().splitlines()

	if article[-len(words):] == words:
		print(os.path.join("huffpost", name))

		with open(name, "w") as file:
			file.writelines(word + "\n" for word in article[:-len(words)])

os.chdir(os.path.join(os.pardir, "theblaze"))

for name in os.listdir():
	with open(name, "r") as file:
		old = file.read()
		new = old.replace("www\nyoutube\ncom\n", "")

	if new != old:
		print(os.path.join("theblaze", name))

		with open(name, "w") as file:
			file.write(new)
