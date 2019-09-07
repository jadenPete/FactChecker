#!/usr/bin/env python3

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
import itertools
import os
import pytz
import re
import sys
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


class HuffPost:
	headers = {"User-Agent": """Mozilla/5.0 (X11; CrOS x86_64 12371.41.0)
	                            AppleWebKit/537.36 (KHTML, like Gecko)
	                            Chrome/77.0.3865.56 Safari/537.36"""}

	@classmethod
	def get_urls(cls):
		date = datetime.now(pytz.timezone("US/Eastern"))

		while True:
			url = f"https://www.huffpost.com/archive/{date.strftime('%Y-%m-%d')}"
			soup = BeautifulSoup(urlopen(Request(url, headers=cls.headers)), "html5lib")

			for article in soup.find_all(class_="card__details"):
				if article.find(class_="card__label__text").text == "POLITICS":
					yield article.find(class_="card__link")["href"]

			date -= timedelta(days=1)

	@staticmethod
	def get_text(soup):
		return " ".join(e.get_text() for e in soup.find_all(class_=[
			"headline", "entry__text"
		]))


class TheBlaze:
	@staticmethod
	def get_urls():
		for i in itertools.count():
			sitemap = urlopen(f"https://www.theblaze.com/feeds/sitemaps/sitemap_{i}.ggl").read()

			for element in ET.fromstring(sitemap):
				yield element.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text

	@staticmethod
	def get_text(soup):
		return " ".join(e.get_text() for e in soup.find_all(class_=[
			"headline", "widget__subheadline-text", "body-description"
		]))


hash_ = hashlib.md5()
path = os.path.join("input", sys.argv[1])

os.makedirs(path, exist_ok=True)
os.chdir(path)

source = {"huffpost": HuffPost,
          "theblaze": TheBlaze}[sys.argv[1]]

for i, url in enumerate(source.get_urls()):
	request = Request(url, headers=getattr(source, "headers", {}))
	soup = BeautifulSoup(urlopen(request), "html5lib")

	for element in soup(["script", "style"]):
		element.decompose()

	text = source.get_text(soup).replace("’", "'")
	words = re.findall(r"(?:[A-Z]\.)+|(?:[a-zA-Z]+(?:'[a-zA-Z])?-?)+", text)
	cleaned = "".join(w.lower() + "\n" for w in words)

	hash_.update(cleaned.encode())

	with open(f"{hash_.hexdigest()}.txt", "w") as file:
		file.write(cleaned)

	print(f"Downloaded article {i} - {url}")

	if i == 249:
		break
