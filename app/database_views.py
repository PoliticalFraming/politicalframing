import requests
from requests import HTTPError
import json
import sqlite3
from flask import jsonify, g
from math import ceil
import sys

from peewee import *
from app.models.Topic import Topic
from app.models.Frame import Frame
from app.models.Speech import Speech

from app.models.SpeechTopic import SpeechTopic
from app import app

CAPITOL_WORDS_API_KEY = '8e87cf0e8a92499e9d14b67165f7018f'
RESULTS_PER_PAGE = 30

@app.route('/download_speeches/<phrase>')
def download_speeches_for_topic(phrase):
  print "Downloading speeches for topic " + phrase

  #logic to download speeches from the API and put them in the database
  page_number = 0 #api starts at page 0
  speeches = []
  relevance = 0
  data = {}

  try:
    while page_number == 0 or data.get('results') != []:
      data = download_page(phrase, page_number)
      if page_number == 0: print str(data[u'num_found']) + " speeches found"

      for speech in data[u'results']:
        try:
          #put speech in db
          s = insert_speech_into_database(speech)
          #connect speech to topic
          relevance += 1
          connect_speech_to_topic(s, phrase, relevance)
        except:
          print "ERROR: Failed to Insert Speech " + speech['id']
          print "Unexpected error:", sys.exc_info()
          pass
  except HTTPError as e:
    error_msg = "CapitolWordsAPI Returned a HTTPError: {0}".format(e)

    print error_msg
    return error_msg
  except Exception:
    print "Failed to Download Speeches: Reason Unknown"
    return "Failed to Download Speeches: Reason Unknown"

    # Debug Line
    # if page_number == 1: return

    # print "Downloaded page " + str(page_number) + " of " + str(int(ceil(data[u'num_found']/RESULTS_PER_PAGE)))

    page_number += 1
  
  print "Successfully Downloaded " + str(data[u'num_found'])  +" speeches for topic '" + phrase +"'"
  return "Successfully Downloaded " + str(data[u'num_found'])  +" speeches for topic '" + phrase +"'"

def download_page(topic, page):
  endpoint = 'http://capitolwords.org/api/text.json'
  query_parameters = {
    'apikey': CAPITOL_WORDS_API_KEY,
    'phrase': topic,
    'per_page' : RESULTS_PER_PAGE,
    'page': page
  }
  response = requests.get(endpoint, params = query_parameters)
  
  if not(response.ok):
    response.raise_for_status() #Raises stored HTTPError, if one occured.

  data = response.json()
  print "Downloaded page " + str(page) + " of " + str(int(ceil(data[u'num_found']/RESULTS_PER_PAGE)))
  return data

def connect_speech_to_topic(speech, phrase, relevance):
  '''Takes in a Speech object (instance of a peewee model) and a string phrase'''
  SpeechTopic.get_or_create(speech=speech, topic=Topic.get_or_create(phrase=phrase), relevance=relevance)


def insert_speech_into_database(speech):
  try:
    speech_already_in_db = Speech.get(Speech.speech_id == speech['id'])
    if (speech_already_in_db):
      print "speech already in database - not inserting " + speech['id']
    return speech_already_in_db
  except DoesNotExist:
    print "inserting speech into database " + speech['id']
    return Speech.create(
          speech_id = speech.get('id'),
          bills = '',#speech.get('bills'),
          biouguide = speech.get('bioguide'),
          capitolwords_url = speech.get('capitolwords_url'),
          chamber = speech.get('chamber'),
          congress = speech.get('congress'),
          date = speech.get('date'),
          number = speech.get('number'),
          order = speech.get('order'),
          origin_url = speech.get('origin_url'),
          pages = speech.get('pages'),
          session = speech.get('session'),
          speaker_first = speech.get('speaker_first'),
          speaker_last = speech.get('speaker_last'),
          speaker_party = speech.get('speaker_party'),
          speaker_raw = speech.get('speaker_raw'),
          speaker_state = speech.get('speaker_state'),
          speaking = speech.get('speaking'),
          title = speech.get('title'),
          volume = speech.get('volume')
      )


def insert_dummy_speech_into_db():

  speech = {
    "speaker_state": "FL",
    "speaker_first": "Lincoln",
    "congress": 111,
    "title": "PROVIDING FOR CONSIDERATION OF MOTIONS TO SUSPEND THE RULES",
    "origin_url": "http://origin.www.gpo.gov/fdsys/pkg/CREC-2009-03-19/html/CREC-2009-03-19-pt1-PgH3645-2.htm",
    "number": 48,
    "order": 40,
    "volume": 155,
    "chamber": "House",
    "session": 1,
    "speech_id": "CREC-2009-03-19-pt1-PgH3645-2.chunk40",
    "speaking": [
      "Mr. Speaker, no more blaming Bush. Mr. Dodd said that it's the Obama administration that asked them to authorize these bonuses.",
      "I yield 2 minutes to the distinguished gentlewoman from North Carolina, Dr. Foxx."],
    "capitolwords_url": "http://capitolwords.org/date/2009/03/19/H3645-2_providing-for-consideration-of-motions-to-suspend-/",
    "speaker_party": "R",
    "date": "2009-03-19",
    "bills": None,
    "bioguide_id": "D000299",
    "pages": "H3645-H3653",
    "speaker_last": "Diaz-Balart",
    "speaker_raw": "mr. lincoln diaz-balart of florida"
  }

  s=Speech.create(
    speech_id = speech.get('speech_id'),
    bills = speech.get('bills'),
    biouguide = speech.get('bioguide'),
    capitolwords_url = speech.get('capitolwords_url'),
    chamber = speech.get('chamber'),
    congress = speech.get('congress'),
    date = speech.get('date'),
    number = speech.get('number'),
    order = speech.get('order'),
    origin_url = speech.get('origin_url'),
    pages = speech.get('pages'),
    session = speech.get('session'),
    speaker_first = speech.get('speaker_first'),
    speaker_last = speech.get('speaker_last'),
    speaker_party = speech.get('speaker_party'),
    speaker_raw = speech.get('speaker_raw'),
    speaker_state = speech.get('speaker_state'),
    # speaking = speech.get('speaking'),
    title = speech.get('title'),
    volume = speech.get('volume')
    )

  SpeechTopic.create(speech=s, 
      topic=Topic.get_or_create(phrase='gay'))
