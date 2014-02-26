"""

Test file to figure out what the fuck is going on with the bioguide.

Insights thus far: The bioguide_import command takes in the congress number as an argument.
By default, it only downloads the 113th congress.

This data is fed into the NYT API for more detailed data regarding the role of each congress person. 
From the 113th congress, the NYT API shows how many other congress's an individual has been part of.

This is why you see a gradually decreasing trend in the resolution of parties from older speeches.

^ THIS IS A VERY, VERY SIMPLE FIX.

Now the question arrises, why are only 31,120 out of 89,478 speeches "bioguided" in the 113th congress.

It would be nice to find the number of "recorder" however the database is unfortunately not indexed on this field.

Running a query on "congress:113 AND -speaker_party:*" yielded, obviously, 89,478 - 31,120.

Browsing speeches manually, some congresspeople I notice without their bioguide imported are:
ms. pelosi
mr. pascrell
mr. blumenauer
mr. levin
mr. camp

NOTE: we need to somehow create a field that represents recorder or speaker pro tempore etc. and index it


This repo has a YAML file we might be able to use
https://github.com/unitedstates/congress-legislators

It seems the original parser has been improved (or maybe just migrated)
https://github.com/unitedstates/congressional-record/blob/master/congressionalrecord/fdsys/cr_parser.py

"""

import httplib2
from sunburnt import SolrInterface
from dateutil import parser
from datetime import datetime

solr_url = "http://politicalframing.com:8983/solr" # "http://localhost:8983/solr/"
h = httplib2.Http(cache="/var/tmp/solr_cache")
si = SolrInterface(url = solr_url, http_connection = h)

def get_speeches(rows, start, dabool, **kwargs):
  query = {}
  neg_query = {}

  if kwargs.get('speech_id'): query['id'] = kwargs['speech_id']
  if kwargs.get('phrase'): query['speaking'] = kwargs['phrase']
  if kwargs.get('congress'): query['congress'] = kwargs['congress']

  kwargs['start_date'] = parser.parse(kwargs['start_date']) if kwargs.get('start_date') else datetime(1994,1,1)
  kwargs['end_date'] = parser.parse(kwargs['end_date']) if kwargs.get('end_date') else datetime.now()
  query['date__range'] = (kwargs['start_date'], kwargs['end_date'])
  

  # Has the congress person been parsed?
  ###################################################
  if dabool == True:
    query['speaker_party__any'] = True
  # negation 
  # http://politicalframing.com:8983/solr/collection1/select?q=congress=113+AND+-speaker_party=*&start=0&rows=100&wt=json&indent=true
  ###################################################

  response = si.query(**query).paginate(rows=rows, start=start).exclude(neg_query).execute()

  
  speeches = response.result.docs
  current_count = response.result.numFound
  current_start = response.result.start

  speeches_dict = {
    'count': current_count,
    'start': current_start,
    'speeches': speeches
  }

  return speeches_dict

# Congress 113-103, first column all speeches, second column speeches with speaker_party
print "Congress 112: %d \t %d" % (get_speeches(0,0, False, congress=113)['count'], get_speeches(0,0, True, congress=113)['count'])
print "Congress 111: %d \t %d" % (get_speeches(0,0, False, congress=112)['count'], get_speeches(0,0, True, congress=112)['count'])
print "Congress 110: %d \t %d" % (get_speeches(0,0, False, congress=111)['count'], get_speeches(0,0, True, congress=111)['count'])
print "Congress 109: %d \t %d" % (get_speeches(0,0, False, congress=110)['count'], get_speeches(0,0, True, congress=110)['count'])
print "Congress 108: %d \t %d" % (get_speeches(0,0, False, congress=109)['count'], get_speeches(0,0, True, congress=109)['count'])
print "Congress 107: %d \t %d" % (get_speeches(0,0, False, congress=108)['count'], get_speeches(0,0, True, congress=108)['count'])
print "Congress 106: %d \t %d" % (get_speeches(0,0, False, congress=107)['count'], get_speeches(0,0, True, congress=107)['count'])
print "Congress 105: %d \t %d" % (get_speeches(0,0, False, congress=106)['count'], get_speeches(0,0, True, congress=106)['count'])
print "Congress 104: %d \t %d" % (get_speeches(0,0, False, congress=105)['count'], get_speeches(0,0, True, congress=105)['count'])
print "Congress 103: %d \t %d" % (get_speeches(0,0, False, congress=104)['count'], get_speeches(0,0, True, congress=104)['count'])
print "Congress 102: %d \t %d" % (get_speeches(0,0, False, congress=103)['count'], get_speeches(0,0, True, congress=103)['count'])

