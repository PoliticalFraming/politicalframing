#!/usr/bin/env python

# usage
# python last_resort.py phrase

import requests
import math
import pickle
import sys
from dateutil import parser
import json

class CapitolWords(object):

  API_KEY = '8e87cf0e8a92499e9d14b67165f7018f'
  RESULTS_PER_PAGE = 1000
  OUTPUT_PATH = "jsons/"

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
        speech[u'document_title'] = speech[u'title']
        del speech[u'title']
        speech[u'slug'] = '' #speech[u'document_title'].lower().replace(" ","-")
        speech[u'crdoc'] = speech[u'origin_url']
        del speech[u'origin_url']
        speech[u'speaker_bioguide'] = speech[u'bioguide_id']
        del speech[u'bioguide_id']
        del speech[u'capitolwords_url']
        del speech[u'order']
        date = parser.parse(speech[u'date']) if speech[u'date'] else None
        speech[u'date'] = date.isoformat('T')+"Z" if date else None
        speech[u'year'] = str(date.year) if date else ''
        speech[u'month'] = str(date.month) if date else ''
        speech[u'day'] = str(date.day) if date else ''
        speech[u'year_month'] = str(date.year) + str(date.month) if date else ''
        speech[u'page_id'] = speech[u'pages']
        speech[u'speaker_firstname'] = speech[u'speaker_first']
        del speech[u'speaker_first']
        speech[u'speaker_lastname'] = speech[u'speaker_last']
        del speech[u'speaker_last']
        if speech.get('speaker_middle'):
          speech[u'speaker_middlename'] = speech[u'speaker_middle']
          del speech[u'speaker_middle']
        if speech[u'chamber']=='House':
          speech[u'speaker_title'] = 'Representative'
        elif speech[u'chamber']=='Senate':
          speech[u'speaker_title'] = 'Senator'

        speeches.append(speech)

        with open(CapitolWords.OUTPUT_PATH + speech[u'id'], 'w') as f:
          json.dump(speech, f)
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