# This file will help get rid of our recent errors with analyzing speeches by
# rolling back to using CapitolWord data for particular topics.

# This file will achieve the above by using our very old "database_views.py" code
# which downloaded speeches within a particular topic. We will combine it with the code
# we recently wrote "update_bioguide_solr.py" which allows searching through all
# congresspeople without a speaker_party defined and attempting to re-resolve their
# party affiliation, state, and other speaker metadata. This data is essential for our
# classifier.

# To begin afresh we will use a new local sort instance.

# cd ~
# wget http://archive.apache.org/dist/lucene/solr/4.6.1/solr-4.6.1.zip
# unzip solr-4.6.1.zip
# cd solr-4.6.1/example/solr/collection1/conf
# vim schema.xml

import requests
import math
import pickle

class CapitolWords(object):

  API_KEY = '8e87cf0e8a92499e9d14b67165f7018f'
  RESULTS_PER_PAGE = 1000

  @staticmethod
  def download_speeches(phrase):
    print "Downloading speeches for topic " + phrase

    page = 0
    speeches = []
    relevance = 0
    data = {}

    filename = phrase + ".pickle"
    # loop through pages of results and add each page to the pickle
    while page == 0 or data.get('results') != None:
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
        pickled_speeches = speeches if not pickled_speeches else pickled_speeches.append(speeches)
        pickle.dump(pickled_speeches,f)
    return

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
  CapitolWords.download_speeches("potato")