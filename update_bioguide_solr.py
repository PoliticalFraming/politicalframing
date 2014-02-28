from __future__ import division

import math
import json
import urllib2
import httplib2
from sunburnt import SolrInterface
from dateutil import parser
from datetime import datetime

from pprint import pprint as pp

import sqlite3
conn = sqlite3.connect(':memory:')


DB_PARAMS = ["localhost","capitolwords","capitolwords","capitolwords"]
BIOGUIDE_LOOKUP_PATH = '/Users/atul/Capitol-Words/api/bioguide_lookup.csv'

def mysql2sqlite():
	import MySQLdb
	conn = sqlite3.connect(':memory:')


# 	cursor = MySQLdb.Connection(*DB_PARAMS, use_unicode=True).cursor()

# 	conn

def main():
	solr_url = "http://politicalframing.com:8983/solr"
	h = httplib2.Http(cache="/var/tmp/solr_cache")
	si = SolrInterface(url = solr_url, http_connection = h)

	# chamber = 'Senate'
	# print commit_solr()
	numFound = si.query(speaking='healthcare', chamber='Senate').exclude(speaker_party="*").sort_by("-score").paginate(rows=0, start=0).execute().result.numFound
	print numFound
	for i in range(0, int(math.ceil(numFound/10000))):
		current_speeches = si.query(speaking='healthcare', chamber='Senate').exclude(speaker_party="*").field_limit(["id", "speaker_raw", "congress", "date"]).sort_by("-score").paginate(rows=10000, start=10000*i).execute().result.docs
		# print current_speeches
		json_documents = []
		for j, speech in enumerate(current_speeches):
			if ((speech['speaker_raw'] != 'recorder') 
				and (speech['speaker_raw'] != 'the presiding officer') 
				and (speech['speaker_raw'] != 'the vice president') 
				and ('the presiding officer' not in speech['speaker_raw'])
				and ('pro tempore' not in speech['speaker_raw'])):
				partial_document = get_speaker_metadata(id=speech['id'], date=speech['date'], congress=speech['congress'], speaker=speech['speaker_raw'], chamber='Senate')

				if partial_document:
					json_documents.append(partial_document)
				else:
					print j

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()
			# import sys
			# sys.exit()

	# print commit_solr()

	# chamber = 'House'
	# print commit_solr()
	numFound = si.query(speaking='healthcare', chamber='House').exclude(speaker_party="*").sort_by("-score").paginate(rows=0, start=0).execute().result.numFound
	print numFound
	for i in range(0, int(math.ceil(numFound/100000))):
		current_speeches = si.query(speaking='healthcare', chamber='House').exclude(speaker_party="*").field_limit(["id", "speaker_raw", "congress", "date"]).sort_by("-score").paginate(rows=100000, start=100000*i).execute().result.docs
		# print current_speeches		
		json_documents = []
		for j, speech in enumerate(current_speeches):	
			if ((speech['speaker_raw'] != 'recorder') 
				and (speech['speaker_raw'] != 'the presiding officer') 
				and (speech['speaker_raw'] != 'the vice president') 
				and ('the presiding officer' not in speech['speaker_raw'])
				and ('pro tempore' not in speech['speaker_raw'])):
				partial_document = get_speaker_metadata(id=speech['id'], date=speech['date'], congress=speech['congress'], speaker=speech['speaker_raw'], chamber='House')

				if partial_document:
					json_documents.append(partial_document)
				else:
					print j

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()
			# import sys
			# sys.exit()
	# print commit_solr()

	# chamber = 'Extensions'
	# print commit_solr()
	numFound = si.query(speaking='healthcare', chamber='Extensions').exclude(speaker_party="*").sort_by("-score").paginate(rows=0, start=0).execute().result.numFound
	print numFound

	for i in range(0, int(math.ceil(numFound/100000))):
		current_speeches = si.query(speaking='healthcare', chamber='Extensions').exclude(speaker_party="*").field_limit(["id", "speaker_raw", "congress", "date"]).sort_by("-score").paginate(rows=100000, start=100000*i).execute().result.docs
		# print current_speeches
		json_documents = []
		for j, speech in enumerate(current_speeches):	
			# print speech['speaker_raw']
			if ((speech['speaker_raw'] != 'recorder') 
				and (speech['speaker_raw'] != 'the presiding officer') 
				and (speech['speaker_raw'] != 'the vice president') 
				and ('the presiding officer' not in speech['speaker_raw'])
				and ('pro tempore' not in speech['speaker_raw'])):
				partial_document = get_speaker_metadata(id=speech['id'], date=speech['date'], congress=speech['congress'], speaker=speech['speaker_raw'], chamber='Extensions')

				if partial_document:
					json_documents.append(partial_document)
				else:
					print j

		if len(json_documents) > 1:
			json_doc_list_string, body = update_solr2(json_documents)
			print len(json_documents)
			print body
			print commit_solr()
			# import sys
			# sys.exit()
	# print commit_solr()

def abbr(longname):
    ''' return the abbreviation for a state'''
    states = {
        'alabama':'al',
        'alaska':'ak',
        'american samoa':'as',
        'arizona':'az',
        'arkansas':'ar',
        'california':'ca',
        'colorado':'co',
        'connecticut':'ct',
        'delaware':'de',
        'district of columbia':'dc',
        'florida':'fl',
        'guam':'gu',
        'georgia':'ga',
        'hawaii':'hi',
        'idaho':'id',
        'illinois':'il',
        'indiana':'in',
        'iowa':'ia',
        'kansas':'ks',
        'kentucky':'ky',
        'louisiana':'la',
        'maine':'me',
        'maryland':'md',
        'massachusetts':'ma',
        'michigan':'mi',
        'minnesota':'mn',
        'mississippi':'ms',
        'missouri':'mo',
        'montana':'mt',
        'nebraska':'ne',
        'nevada':'nv',
        'new hampshire':'nh',
        'new jersey':'nj',
        'new mexico':'nm',
        'new york':'ny',
        'north carolina':'nc',
        'north dakota':'nd',
        'northern mariana islands':'mp',
        'ohio':'oh',
        'oklahoma':'ok',
        'oregon':'or',
        'pennsylvania':'pa',
        'puerto rico':'pr',
        'rhode island':'ri',
        'south carolina':'sc',
        'south dakota':'sd',
        'tennessee':'tn',
        'texas':'tx',
        'utah':'ut',
        'vermont':'vt',
        'virgin islands':'vi',
        'virginia':'va',
        'washington':'wa',
        'west virginia':'wv',
        'wisconsin':'wi',
        'wyoming':'wy',
    }

    if longname.lower() in states.keys():
        return states[longname]
    else:
    	print longname
        return None

def get_speaker_metadata(id, date, congress, speaker, chamber):
	pieces = speaker.split(' of ')
	lastname = pieces[0].lower()
	if lastname.startswith('mr.') or lastname.startswith('ms.') or lastname.startswith('mrs.'):
		i = lastname.find('.')
		lastname = lastname[i+1:].strip()
	if len(pieces) > 1:
		state = pieces[1]
	else:
		state = None
	# get the chamber info
	chamber = chamber.lower()
	if chamber == 'senate':
		position = 'senator'
	else:
		position = 'representative'

	day = date.day
	month = date.month
	year = date.year
	date = '%d-%d-%d' % (year, month, day)

	if chamber == 'extensions':
		chamber = 'house'
	
	data = db_bioguide_lookup(lastname, congress, chamber, date, state)

	if not data or len(data) > 1:
		data = fallback_bioguide_lookup(speaker, congress, position)
		if not data:
			print "-------------------------------------"
			msg = 'No data or too many responses for %s, %s, %s, %s\n' % (lastname, year, position, state)
			print msg
			return None
		
	match = data[0]

	partial_document = {
		"id": id,
		"speaker_state": { "set": match['state'] },
		"speaker_party": { "set": match['party'] },
		"speaker_bioguide": { "set": match['bioguide'] },
		"speaker_firstname": { "set": match['firstname'] },
		"speaker_middlename": { "set": match.get('middlename', '') },
		"speaker_lastname": { "set": match['lastname'] },
		"speaker_title": { "set": match['title'] },
		"speaker_district": { "set": match['district'] },
		"chamber": { "set": chamber }
	}

	return partial_document

def db_bioguide_lookup(lastname, congress, chamber, date, state=None):
	import MySQLdb
	cursor = MySQLdb.Connection(*DB_PARAMS, use_unicode=True).cursor()

	query = """SELECT 
						bioguide_id AS bioguide,
						first       AS firstname,
						middle      AS middlename,
						last        AS lastname,
						party       AS party,
						title       AS title,
						state       AS state,
						district    AS district
				FROM bioguide_legislatorrole
				WHERE
						LOWER(last)    = %s
					AND congress       = %s
					AND LOWER(chamber) = %s
					AND begin_date    <= %s
					AND end_date      >= %s
			"""
	args = [lastname.lower(),
			congress,
			chamber.lower(),
			date,
			date, ]
	if state and abbr(state):
		query += " AND state = %s"
		args.append(abbr(state).upper())

	# cursor.execute(query, args)
	fields = ['bioguide', 'firstname', 'middlename', 'lastname', 'party', 'title', 'state', 'district', ]
	cursor.execute(query, args)
	return [dict(zip(fields, x)) for x in cursor.fetchall()]

def fallback_bioguide_lookup(name, congress, position):
	"""Some lawmakers are routinely referred to in a way that
	means they won't be found using db_bioguide_lookup.  These
	lawmakers should be placed in a pipe-delimited file
	in BIOGUIDE_LOOKUP_PATH, e.g.:
	J000126|eddie bernice johnson|2009|representative|texas
	D000299|lincoln diaz-balart|2009|representative|florida
	"""
	import csv
	import MySQLdb
	cursor = MySQLdb.Connection(*DB_PARAMS, use_unicode=True).cursor()

	with open(BIOGUIDE_LOOKUP_PATH, 'r') as fh:
		for row in csv.reader(fh, delimiter='|'):
			if '|'.join(row[1:]) == '|'.join([name, congress, position, ]):
				cursor.execute("""SELECT bioguide_id, party, state, first, last
										FROM bioguide_legislator
										WHERE bioguide_id = %s 
											  AND congress = %s
										LIMIT 1""", [row[0], congress, ])
				fields = ['bioguide', 'party', 'state', 'firstname', 'lastname', ]
				return [dict(zip(fields, x)) for x in cursor.fetchall()]

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