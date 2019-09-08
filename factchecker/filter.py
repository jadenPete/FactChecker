import re


def get_words(text):
	text = text.replace("’", "'")
	words = re.findall(r"(?:[A-Z]\.)+|(?:[a-zA-Z]+(?:'[a-zA-Z])?-?)+", text)

	return [w.lower() for w in words]
