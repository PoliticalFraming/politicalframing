#!/usr/bin/env python

# usage
# python last_resort.py phrase

import requests
import math
import pickle
import sys

class CapitolWords(object):

  API_KEY = '8e87cf0e8a92499e9d14b67165f7018f'
  RESULTS_PER_PAGE = 1000

  @staticmethod
  def download_speeches(phrase):
    print "Downloading speeches for topic " + phrase

    page = 0
    speeches = []
    relevance = 0
    current_data = {}

    filename = phrase + ".pickle"
    # loop through pages of results and add each page to the pickle
    while page == 0 or current_data.get('results') != []:
      speeches = []
      current_data = CapitolWords.download_page(phrase, page)
      current_count = CapitolWords.getCount(current_data)
      if CapitolWords.isFirst(page): print "%d speeches found" % current_count
      for speech in current_data[u'results']:
        speeches.append(speech)
      page = page+1

      # add this page of speeches to pickle speeches to pickle
      pickled_speeches = None
      try:
        with open(filename, 'r') as f:
          pickled_speeches = pickle.load(f)
      except:
        print "creating new file"

      with open(filename, 'w') as f:
        if pickled_speeches == None:
          pickled_speeches = speeches
        else:
          pickled_speeches += speeches
        pickle.dump(pickled_speeches,f)

  @staticmethod
  def download_page(phrase, page):
    endpoint = 'http://capitolwords.org/api/text.json'
    query_parameters = {
      'apikey': CapitolWords.API_KEY,
      'phrase': phrase,
      'per_page': CapitolWords.RESULTS_PER_PAGE,
      'page': page
    }
    response = requests.get(endpoint, params = query_parameters)
    if not(response.ok): response.raise_for_status() # Raises stored HTTPError, if one occured.
    data = response.json()
    print "Downloaded page " + str(page) + " of " + str(int(math.ceil(data[u'num_found']/CapitolWords.RESULTS_PER_PAGE)) + 1)
    return data

  @staticmethod
  def isFirst(page):
    if page == 0: return True
    else: return False

  @staticmethod
  def getCount(data):
    return data[u'num_found']

if __name__ == "__main__":
  CapitolWords.download_speeches(sys.argv[1])