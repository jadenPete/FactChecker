#!/usr/bin/env python3

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from filter import get_words
import hashlib
import itertools
import os
import pytz
import re
import sys
import time
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

headers = {"User-Agent": """Mozilla/5.0 (X11; CrOS x86_64 12371.41.0)
	                        AppleWebKit/537.36 (KHTML, like Gecko)
	                        Chrome/77.0.3865.56 Safari/537.36"""}


def dl_page(url):
	return urlopen(Request(url, headers=headers)).read()


class HuffPost:
	selector = ".headline, .entry__text"

	@classmethod
	def get_urls(cls):
		date = datetime.now(pytz.timezone("US/Eastern"))

		while True:
			url = f"https://www.huffpost.com/archive/{date.strftime('%Y-%m-%d')}"
			soup = BeautifulSoup(dl_page(url), "html5lib")

			for article in soup.find_all(class_="card__details"):
				if article.find(class_="card__label__text").text == "POLITICS":
					yield article.find(class_="card__link")["href"]

			date -= timedelta(days=1)


class InfoWars:
	selector = ".entry-title, .entry-subtitle, article"

	@classmethod
	def get_urls(cls):
		sitemap = ET.fromstring(dl_page("https://www.infowars.com/sitemap.xml"))
		namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

		for sm_entry in sitemap.findall(namespace + "sitemap"):
			sm_url = sm_entry.find(namespace + "loc").text

			if re.match(r"^https://www\.infowars\.com/sitemap-pt-post-[0-9]{4}-[0-9]{2}.xml$", sm_url):
				for entry in ET.fromstring(dl_page(sm_url)).findall(namespace + "url"):
					yield entry.find(namespace + "loc").text

					# According to https://www.infowars.com/robots.txt
					time.sleep(3)


class TheBlaze:
	selector = ".headline, .widget__subheadline-text, .body-description"

	@staticmethod
	def get_urls():
		for i in itertools.count():
			url = f"https://www.theblaze.com/feeds/sitemaps/sitemap_{i}.ggl"

			for element in ET.fromstring(dl_page(url)):
				yield element.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text


hash_ = hashlib.md5()
path = os.path.join("input", sys.argv[1])

os.makedirs(path, exist_ok=True)
os.chdir(path)

source = {"huffpost": HuffPost,
          "infowars": InfoWars,
          "theblaze": TheBlaze}[sys.argv[1]]

for i, url in enumerate(source.get_urls()):
	soup = BeautifulSoup(dl_page(url), "html5lib")

	for element in soup(["script", "style"]):
		element.decompose()

	text = " ".join(e.get_text() for e in soup.select(source.selector))
	words = "".join(w + "\n" for w in get_words(text))

	hash_.update(words.encode())

	with open(f"{hash_.hexdigest()}.txt", "w") as file:
		file.write(words)

	print(f"Downloaded article {i} - {url}")

	if i == 249:
		break
