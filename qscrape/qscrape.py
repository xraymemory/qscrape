import requests 
import os.path
import json
import sys
import traceback
import markovify 

from bs4 import BeautifulSoup as bs
from collections import OrderedDict

class Q:

    FILENAME = "./q.json"
    CONCURRENT = 200

    def __init__(self, corpus=FILENAME):
        ''' Set up defaults, checks if file already exists and loads it in '''

        self.BASE_URL = "https://qalerts.app"
        self.BASE_POSTS_URL = "https://qalerts.app/?n="

        self.JSON = OrderedDict()
        self.JSON["posts"] = {}
        self.corpus = ''

        self.silent = True

        self.MAIN_PAGE_POST_DIV_CLASS = "xtext-accent text-decoration-none font-weight-bold text-custom-green"
        self.SINGLE_POST_DIV_CLASS = "dont-break-out mb-3 text-accent"

        ''' Look for corpus on disk and load it in'''
        if os.path.isfile(corpus):
            with open(corpus) as f:
                self.JSON = json.load(f, object_pairs_hook=OrderedDict)
                for post in self.JSON["posts"]:
                    self.corpus += self.JSON["posts"][str(post)]['text'] + '\n'

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
            ''' Some posts are image only - we are concerned with text for now .
                Since we are getting the post number from scraping and not from
                any counter, the numbers will still line up.
            '''
            traceback.print_tb(e.__traceback__)


    def get(self, post_number):
        ''' Get single Q drop '''

        q = requests.get(self.BASE_POSTS_URL+str(post_number))
        self._handle_request(q)

    def scrape(self, start=1, end=-1):
        ''' Scrape QAlert site for new Q posts and save to internal JSON '''

        if (start == -1):
            start = len(self.JSON["posts"])

        if (end == -1):
            end = self._get_q_max()
        
        for post in range(start, end):

            self.get(post)

    def save(self, output=FILENAME):
        ''' Write Q JSON representation to file '''

        with open(output, 'w+') as f:
            json.dump(self.JSON, f)

    def drop(self, q_input=''):
        ''' Generate Q drops from markov chain '''

        if q_input == '': q_input = self.corpus

        model = markovify.Text(q_input)
        sentence = model.make_sentence()
 

        ''' Markovify occasionally returns weird results which print as blanks
        so if we see those, we just sample again '''
        if ((sentence is not None) and (sentence != None) and ((sentence is not ' ') and (sentence is not '') and (sentence is not '\n'))):
            return sentence
        else:
            return self.drop()




if __name__ == "__main__":

    def run():

        q = Q()

        if len(q.corpus) <= 1:
            q.scrape(end=50)
            q.save()
        
        print(q.drop())

    run()


