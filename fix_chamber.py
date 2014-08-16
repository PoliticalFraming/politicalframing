from __future__ import division

import math
import json
import urllib2
import httplib2
from sunburnt import SolrInterface
from dateutil import parser
from datetime import datetime

from pprint import pprint as pp

# import sqlite3
# conn = sqlite3.connect(':memory:')

DB_PARAMS = ["localhost","capitolwords","capitolwords","capitolwords"]
BIOGUIDE_LOOKUP_PATH = '/Users/atul/Capitol-Words/api/bioguide_lookup.csv'

def main():
	solr_url = "http://politicalframing.com:8983/solr/collection1"
	h = httplib2.Http(cache="/var/tmp/solr_cache")
	si = SolrInterface(url = solr_url, http_connection = h)

	# chamber = 'Senate'
	# print commit_solr()

	numFound = si.query(chamber='senate').paginate(rows=0, start=0).execute().result.numFound
	print "-----------------------"
	print "Number of Speeches about Topic X in senate " + str(numFound)
	for i in range(0, int(math.ceil(numFound/10000))):
		current_speeches = si.query(chamber='senate').field_limit(["id"]).paginate(rows=10000, start=10000*i).execute().result.docs
		json_documents = []
		for j, speech in enumerate(current_speeches):
			partial_document = get_speaker_metadata(id=speech['id'], chamber='Senate')

			if partial_document:
				print speech['id'] + " queued to be ingested"
				json_documents.append(partial_document)

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()

	numFound = si.query(chamber='house').paginate(rows=0, start=0).execute().result.numFound
	print "-----------------------"
	print "Number of Speeches about Topic X in house " + str(numFound)
	for i in range(0, int(math.ceil(numFound/10000))):
		current_speeches = si.query(chamber='house').field_limit(["id"]).paginate(rows=10000, start=10000*i).execute().result.docs
		json_documents = []
		for j, speech in enumerate(current_speeches):
			partial_document = get_speaker_metadata(id=speech['id'], chamber='House')

			if partial_document:
				print speech['id'] + " queued to be ingested"
				json_documents.append(partial_document)

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()


def get_speaker_metadata(id, chamber):
	partial_document = {
		"id": id,
		"chamber": { "set": chamber }
	}

	return partial_document

def update_solr(partial_document):
	req = urllib2.Request('http://politicalframing.com:8983/solr/update')
	req.add_header('Content-Type', 'application/json')
	json_doc = partial_document
	response = urllib2.urlopen(req, json_doc)
	body = response.read()
	return json_doc, body

def update_solr2(json_documents):
	req = urllib2.Request('http://politicalframing.com:8983/solr/update')
	req.add_header('Content-Type', 'application/json')

	json_doc_list_string = json.dumps(json_documents)
	response = urllib2.urlopen(req, json_doc_list_string)
	body = response.read()
	return json_doc_list_string, body

def commit_solr():
	req = urllib2.Request('http://politicalframing.com:8983/solr/update?commit=true')
	response = urllib2.urlopen(req)
	body = response.read()
	return body

if __name__ == "__main__":
	main()