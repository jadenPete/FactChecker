#!/usr/bin/env python3

from __init__ import text_to_words
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
import itertools
import os
import pytz
import re
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12371.65.0) " +
                         "AppleWebKit/537.36 (KHTML, like Gecko) " +
                         "Chrome/77.0.3865.93 Safari/537.36"}

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

	entries = parse_url(sitemap_url, "xml").findall(namespace + entry_tag)

	if getattr(source, "sm_reverse", False):
		entries.reverse()

	for entry in entries:
		url = entry.find(namespace + "loc").text

		if not hasattr(source, re_attr) or re.match(getattr(source, re_attr), url):
			if sitemap is None:
				for article_url in parse_sitemap(source, url):
					yield article_url
			else:
				yield url

				if hasattr(source, "delay"):
					time.sleep(source.delay)


def parse_google_news(source):
	article_format = re.compile(rf"^{re.escape(source.article_prefix)}")

	for i in range(0, 1001, 10):
		url = f"https://www.google.com/search?q=site:{source.article_prefix}*" + \
		      f"&tbs=sbd:1&tbm=nws&start={i}"

		for article in parse_url(url, "html").find_all("a", href=article_format):
			yield article["href"]


def get_urls(source):
	if hasattr(source, "get_urls"):
		return source.get_urls()
	elif hasattr(source, "article_prefix"):
		return parse_google_news(source)

	return parse_sitemap(source, getattr(source, "sitemap", None))


class AP:
	selector = ".headline, .Article > p"

	@staticmethod
	def get_urls():
		url = "https://apnews.com/apf-politics"

		for article in parse_url(url, "html").find_all(class_="FeedCard"):
			yield "https://apnews.com/" + article.find("a")["href"]


class CNN:
	sm_index = "https://www.cnn.com/sitemaps/cnn/index.xml"
	sm_format = r"^https://www\.cnn\.com/sitemaps/article-\d{4}-\d{2}\.xml$"
	article_format = r"^https://www\.cnn\.com/\d{4}/\d{2}/\d{2}/politics/"
	selector = ".pg-headline, .el__storyelement__header," + \
	           ".zn-body__paragraph:not(.zn-body__footer)"


class FoxNews:
	sm_index = "https://www.foxnews.com/sitemap.xml"
	sm_format = r"^https://www\.foxnews\.com/sitemap\.xml\?type=articles&from=\d+$"
	sm_reverse = True
	article_format = r"^https://www\.foxnews\.com/politics/"
	selector = ".headline, .caption, .article-body > p"


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


class NBCNews:
	sm_index = "https://www.nbcnews.com/sitemap/nbcnews/sitemap-index"
	sm_format = r"^https://www\.nbcnews\.com/sitemap/nbcnews/sitemap-\d{4}-\d{2}-article\.xml$"
	article_format = r"^https://www\.nbcnews\.com/politics/"
	selector = "[class^=headline], .articleDek, [class^=bodyContent] > p"


class NPR:
	selector = ".storytitle, .caption, #storytext > p:not(.contributors-text)"

	@staticmethod
	def get_urls():
		for i in itertools.count(1, 24):
			if i == 1:
				url = "https://www.npr.org/sections/politics/"
			else:
				url = f"https://www.npr.org/get/1014/render/partial/next?start={i}"

			for article in parse_url(url, "html").find_all(class_="title"):
				article_url = article.find("a")["href"]

				if re.match(r"$https://www\.npr\.org/\d{4}/\d{2}/\d{2}/\d+/", article_url):
					yield article_url


class TheBlaze:
	article_prefix = "https://www.theblaze.com/news/"
	selector = """.headline, .widget__subheadline-text,
	              .body-description > p:not(.shortcode-media),
	              .body-description > h3"""


class TheEconomist:
	sm_index = "https://www.economist.com/sitemap.xml"
	sm_format = r"^https://www\.economist\.com/sitemap-\d{4}-Q[1-4]\.xml$"
	article_format = r"^https://www\.economist\.com/united-states/\d{4}/\d{2}/\d{2}/"
	selector = ".flytitle-and-title__title, .blog-post__description, .blog-post__text > p"
	delay = 5


class ThinkProgress:
	sm_index = "https://thinkprogress.org/sitemap.xml"
	selector = ".post__title, .post__dek, .post__content > p"


class WashingtonPost:
	article_prefix = "https://www.washingtonpost.com/politics/"
	selector = ".topper-headline, .pb-caption, article > p"


path = os.path.join("input", sys.argv[1])

os.makedirs(path, exist_ok=True)
os.chdir(path)

source = {"ap": AP,
          "cnn": CNN,
          "foxnews": FoxNews,
          "huffpost": HuffPost,
          "infowars": InfoWars,
          "nbcnews": NBCNews,
          "npr": NPR,
          "theblaze": TheBlaze,
          "theeconomist": TheEconomist,
          "thinkprogress": ThinkProgress,
          "washingtonpost": WashingtonPost}[sys.argv[1]]

count = 0

for url in get_urls(source):
	print(f"Downloading {count:03}: {url}", end="", flush=True)

	soup = parse_url(url, "html")
	words = ""

	for element in soup(["script", "style"]):
		element.decompose()

	for text in soup.select(source.selector):
		for word in text_to_words(text.get_text()):
			words += word + "\n"

	if len(words) > 0:
		name = f"{hashlib.md5(words.encode()).hexdigest()}.txt"
		count += 1

		with open(name, "w") as file:
			file.write(words)

		print(f" -> {name}\n")

		if count == 250:
			break
	else:
		print("\n")
