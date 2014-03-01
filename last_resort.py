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

class CapitolWords(object):

  API_KEY = '8e87cf0e8a92499e9d14b67165f7018f'
  RESULTS_PER_PAGE = 30

  @staticmethod
  def download_speeches(phrase):
    print "Downloading speeches for topic " + phrase

    page = 0
    speeches = []
    relevance = 0
    data = {}

    while page == 0 or data.get('results') != []:
      current_data = CapitolWords.download_page(phrase, page)
      current_count = CapitolWords.getCount(current_data)
      if CapitolWords.isFirst(page): print "%d speeches found" % current_count
      for speech in current_data[u'results']:
        # save_to_solr(speech)

      page = page+1

    total_count = CapitolWords.getCount(data)

    print "Successfully Downloaded " + str(total_count)  + " speeches for topic '" + phrase + "'"
    return 

  @staticmethod
  def download_page(phrase, page):
    endpoint = 'http://capitolwords.org/api/text.json'
    query_parameters = {
      'apikey': CapitolWords.API_KEY,
      'phrase': phrase,
      'per_page' : CapitolWords.RESULTS_PER_PAGE,
      'page': page
    }
    response = requests.get(endpoint, params = query_parameters)
    if not(response.ok): response.raise_for_status() # Raises stored HTTPError, if one occured.
    data = response.json()
    print "Downloaded page " + str(page) + " of " + str(int(math.ceil(data[u'num_found']/CapitolWords.RESULTS_PER_PAGE)))
    return data

  @staticmethod
  def isFirst(page):
  	if page == 0: return True
  	else: return False

  @staticmethod
  def getCount(data):
  	return data[u'num_found']

if __name__ == "__main__":
  CapitolWords.download_speeches("immigration")