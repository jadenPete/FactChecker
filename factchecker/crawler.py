#!/usr/bin/env python3

from __init__ import text_to_words
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
import os
import pytz
import re
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12371.41.0) " +
                         "AppleWebKit/537.36 (KHTML, like Gecko) " +
                         "Chrome/77.0.3865.56 Safari/537.36"}

namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def parse_url(url, content_type):
	for i in range(4):
		try:
			data = urlopen(Request(url, headers=headers)).read()
		except HTTPError:
			if i == 3:
				raise
			else:
				time.sleep(4)
		else:
			break

	if content_type == "html":
		return BeautifulSoup(data, "html5lib")
	elif content_type == "xml":
		return ET.fromstring(data)


def parse_sitemap(source, sitemap=None):
	if sitemap is None:
		sitemap_url, entry_tag, re_attr = source.sm_index, "sitemap", "sm_format"
	else:
		sitemap_url, entry_tag, re_attr = sitemap, "url", "article_format"

	for entry in parse_url(sitemap_url, "xml").findall(namespace + entry_tag):
		url = entry.find(namespace + "loc").text

		if not hasattr(source, re_attr) or re.match(getattr(source, re_attr)):
			if sitemap is None:
				for url in parse_sitemap(source, url):
					yield url
			else:
				yield url

				if hasattr(source, "delay"):
					time.sleep(source.delay)


def get_urls(source):
	if hasattr(source, "get_urls"):
		return source.get_urls()
	else:
		return parse_sitemap(source, getattr(source, "sitemap", None))


class CNN:
	sitemap = "https://www.cnn.com/sitemaps/cnn/news.xml"
	article_format = r"^https://www\.cnn\.com/\d{4}/\d{2}/\d{2}/politics/"
	selector = ".pg-headline, .el__storyelement__header, .zn-body__paragraph"


class HuffPost:
	selector = ".headline, .content-list-component > p"

	@staticmethod
	def get_urls():
		date = datetime.now(pytz.timezone("US/Eastern"))

		while True:
			url = f"https://www.huffpost.com/archive/{date.strftime('%Y-%m-%d')}"

			for article in parse_url(url, "html").find_all(class_="card__details"):
				if article.find(class_="card__label__text").text == "POLITICS":
					yield article.find(class_="card__link")["href"]

			date -= timedelta(days=1)


class InfoWars:
	sm_index = "https://www.infowars.com/sitemap.xml"
	sm_format = r"^https://www\.infowars\.com/sitemap-pt-post-\d{4}-\d{2}.xml$"
	selector = ".entry-title, .entry-subtitle, article > p"
	delay = 3


class TheBlaze:
	selector = """.headline, .widget__subheadline-text,
	              .body-description > p:not(.shortcode-media),
	              .body-description > h3"""

	@staticmethod
	def get_urls():
		article_format = re.compile(r"^https://www\.theblaze\.com/news/")

		for i in range(0, 1001, 10):
			url = "https://www.google.com/search?q=site:theblaze.com/news/*" + \
			      f"&tbs=sbd:1&tbm=nws&start={i}"

			for article in parse_url(url, "html").find_all("a", href=article_format):
				yield article["href"]


class ThinkProgress:
	sm_index = "https://thinkprogress.org/sitemap.xml"
	selector = ".post__title, .post__dek, .post__content > p"


hash_ = hashlib.md5()
path = os.path.join("input", sys.argv[1])

os.makedirs(path, exist_ok=True)
os.chdir(path)

source = {"cnn": CNN,
          "huffpost": HuffPost,
          "infowars": InfoWars,
          "theblaze": TheBlaze,
          "thinkprogress": ThinkProgress}[sys.argv[1]]

for i, url in zip(range(250), get_urls(source)):
	print(f"Downloading article {i} - {url}")

	soup = parse_url(url, "html")
	words = ""

	for element in soup(["script", "style"]):
		element.decompose()

	for text in soup.select(source.selector):
		for word in text_to_words(text.get_text()):
			words += word + "\n"

	hash_.update(words.encode())

	with open(f"{hash_.hexdigest()}.txt", "w") as file:
		file.write(words)
