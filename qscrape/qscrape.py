import requests 
import os.path
import json
import sys
import traceback

from bs4 import BeautifulSoup as bs
from collections import OrderedDict

class Q:

	FILENAME = "./q.txt"
	CONCURRENT = 200

	def __init__(self, corpus=FILENAME):
		''' Set up defaults, checks if file already exists and loads it in '''

		self.BASE_URL = "https://qalerts.app"
		self.BASE_POSTS_URL = "https://qalerts.app/?n="

		self.JSON = OrderedDict()
		self.JSON["posts"] = {}

		self.silent = False

		self.MAIN_PAGE_POST_DIV_CLASS = "xtext-accent text-decoration-none font-weight-bold text-custom-green"
		self.SINGLE_POST_DIV_CLASS = "dont-break-out mb-3 text-accent"

		if os.path.isfile(corpus):
			with open(corpus) as f:
				self.JSON = json.load(f, object_pairs_hook=OrderedDict)

	def _get_q_max(self):
		''' Get ceiling of Q posts '''

		q = requests.get(self.BASE_URL)
		soup = bs(q.text, features="html.parser")
		max_posts = soup.find_all("a", {"class": self.MAIN_PAGE_POST_DIV_CLASS})

		return int(max_posts[0].text)


	def _handle_request(self, resp):
		''' Isolated function for actual data munging '''

		try:
			q = resp.body
		except AttributeError:
			q =resp.text
			
		soup = bs(q, features="html.parser")

		try:
			post_number = soup.find_all("a", {"title": "Sequential Post Number"})[0].text
			post_date = soup.find("div", {"class": "ml-2"}).text
			post_text = soup.find("div", {"class": self.SINGLE_POST_DIV_CLASS}).text
			q_entry = {"number": post_number, "date": post_date, "text": post_text}

			if not self.silent:
				print("Retrieving post: " + str(post_number))
				print(q_entry)

			self.JSON["posts"][int(post_number)] = q_entry
			
		except Exception as e:
			''' Some posts are image only - we are concerned with text for now '''
			traceback.print_tb(e.__traceback__)

	def get(self, post_number):
		''' Get single Q drop '''

		q = requests.get(self.BASE_POSTS_URL+str(post_number))
		self._handle_request(q)

	def scrape(self, n=-1):
		''' Scrape QAlert site for new Q posts and save to internal JSON '''

		if (n == -1):
			n = self._get_q_max()

		post_floor = len(self.JSON["posts"])

		if (post_floor == 0):
			post_floor = 1

		post_range = abs(post_floor - n)
		
		for post in range(post_floor, post_floor+post_range):

			self.get(post)

	def save(self, output=FILENAME):
		''' Write Q JSON representation to file '''

		with open(output, 'w+') as f:
			json.dump(self.JSON, f)


if __name__ == "__main__":

	q = Q()
	q.scrape()
	q.save()
