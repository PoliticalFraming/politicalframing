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

	numFound = si.query(chamber='Senate').exclude(speaker_raw="*").sort_by("speaker_raw").paginate(rows=0, start=0).execute().result.numFound
	print "-----------------------"
	print "Number of Speeches about Topic X in Senate without a Speaker Raw Indexed " + str(numFound)
	for i in range(0, int(math.ceil(numFound/100000))):
		current_speeches = si.query(chamber='Senate').exclude(speaker_raw="*").sort_by("speaker_raw").field_limit(["id", "speaker_raw"]).paginate(rows=100000, start=100000*i).execute().result.docs
		json_documents = []
		for j, speech in enumerate(current_speeches):
			partial_document = get_speaker_metadata(id=speech['id'], speaker=speech['speaker_raw'], chamber='Senate')

			if partial_document:
				print speech['speaker_raw'] + " queued to be ingested"
				json_documents.append(partial_document)

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()

	numFound = si.query(chamber='senate').exclude(speaker_raw="*").sort_by("speaker_raw").paginate(rows=0, start=0).execute().result.numFound
	print "-----------------------"
	print "Number of Speeches about Topic X in senate without a Speaker Raw Indexed " + str(numFound)
	for i in range(0, int(math.ceil(numFound/100000))):
		current_speeches = si.query(chamber='senate').exclude(speaker_raw="*").sort_by("speaker_raw").field_limit(["id", "speaker_raw"]).paginate(rows=100000, start=100000*i).execute().result.docs
		json_documents = []
		for j, speech in enumerate(current_speeches):
			partial_document = get_speaker_metadata(id=speech['id'], speaker=speech['speaker_raw'], chamber='Senate')

			if partial_document:
				print speech['speaker_raw'] + " queued to be ingested"
				json_documents.append(partial_document)

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()

	# chamber = 'House'
	numFound = si.query(chamber='House').exclude(speaker_raw="*").sort_by("speaker_raw").paginate(rows=0, start=0).execute().result.numFound
	print "-----------------------"
	print "Number of Speeches about Topic X in House without a Speaker Raw Indexed " + str(numFound)
	for i in range(0, int(math.ceil(numFound/100000))):
		current_speeches = si.query(chamber='House').exclude(speaker_raw="*").sort_by("speaker_raw").field_limit(["id", "speaker_raw"]).paginate(rows=100000, start=100000*i).execute().result.docs
		json_documents = []
		for j, speech in enumerate(current_speeches):
			partial_document = get_speaker_metadata(id=speech['id'], speaker=speech['speaker_raw'], chamber='House')

			if partial_document:
				print speech['speaker_raw'] + " queued to be ingested"
				json_documents.append(partial_document)

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()

	numFound = si.query(chamber='house').exclude(speaker_raw="*").sort_by("speaker_raw").paginate(rows=0, start=0).execute().result.numFound
	print "-----------------------"
	print "Number of Speeches about Topic X in house without a Speaker Raw Indexed " + str(numFound)
	for i in range(0, int(math.ceil(numFound/100000))):
		current_speeches = si.query(chamber='house').exclude(speaker_raw="*").sort_by("speaker_raw").field_limit(["id", "speaker_raw"]).paginate(rows=100000, start=100000*i).execute().result.docs
		json_documents = []
		for j, speech in enumerate(current_speeches):
			partial_document = get_speaker_metadata(id=speech['id'], speaker=speech['speaker_raw'], chamber='House')

			if partial_document:
				print speech['speaker_raw'] + " queued to be ingested"
				json_documents.append(partial_document)

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()

	# chamber = 'Extensions'
	numFound = si.query(chamber='Extensions').exclude(speaker_raw="*").sort_by("speaker_raw").paginate(rows=0, start=0).execute().result.numFound
	print "-----------------------"
	print "Number of Speeches about Topic X in Extensions without a Speaker Raw Indexed " + str(numFound)
	for i in range(0, int(math.ceil(numFound/100000))):
		current_speeches = si.query(chamber='Extensions').exclude(speaker_raw="*").sort_by("speaker_raw").field_limit(["id", "speaker_raw"]).paginate(rows=100000, start=100000*i).execute().result.docs
		json_documents = []
		for j, speech in enumerate(current_speeches):
			partial_document = get_speaker_metadata(id=speech['id'], speaker=speech['speaker_raw'], chamber='Extensions')

			if partial_document:
				print speech['speaker_raw'] + " queued to be ingested"
				json_documents.append(partial_document)

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()

def get_speaker_metadata(id, speaker, chamber):
	partial_document = {
		"id": id,
		"speaker_raw": { "set": speaker },
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