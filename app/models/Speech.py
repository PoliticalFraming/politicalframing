from app import app, db
from peewee import *
from dateutil import parser

from app.models.frame import get_frame

class Speech(db.Model):
    speech_id = CharField(null=False, db_column='id', primary_key=True, unique=True)
    bills = TextField(null=True)
    biouguide = CharField(null=True)
    capitolwords_url = TextField(null=True)
    chamber = CharField(null=True)
    congress = IntegerField(null=True)
    date = DateField(null=True)
    number = IntegerField(null=True)
    order = IntegerField(null=True)
    origin_url = TextField(null=True)
    pages = CharField(null=True)
    session = IntegerField(null=True)
    speaker_first = CharField(null=True)
    speaker_last = CharField(null=True)
    speaker_party = CharField(null=True)
    speaker_raw = CharField(null=True)
    speaker_state = CharField(null=True)
    speaking = TextField(null=True)
    title = TextField(null=True)
    volume = IntegerField(null=True)

    class Meta:
        db_table = 'speeches'

from app.models.speechtopic import SpeechTopic
from datetime import date, datetime

def get_speeches_in_date_order(topic=None, states=None, start_date=None, end_date=None):
    query = Speech.select()
    if topic!=None:
        query=query.join(SpeechTopic).where(SpeechTopic.topic==topic)
    if states!=None:
        query=query.where(Speech.speaker_state<<states)
    if end_date != None or start_date !=None:
        if start_date==None:
            end_date=parser.parse(end_date).date()
            query=query.where(Speech.date<=end_date)
        elif end_date==None:
            start_date=parser.parse(start_date).date()
            query=query.where(Speech.date>=start_date)
        else: #both start_date and end_date are given
            end_date=parser.parse(end_date).date()
            start_date=parser.parse(start_date).date()
            query=query.where(Speech.date>=start_date).where(Speech.date<=end_date)
    return query.order_by(Speech.date)

def highlight_speech(speech, frame_id):
  ''' Takes a speech and modifies the speech.speaking variable to be
  a list containing a single string with frame words bolded. '''

  frame = get_frame(frame_id).word_string.split(' ')

  speech['speaking'] = \
    map(lambda sentence: 
      " ".join(map(lambda word: "<strong>" + word + "</strong>" if word in frame else word, 
        sentence.split())), 
    eval(speech.get('speaking')))

  return speech

# Speeches.get_speeches(topic_id, states, start_date, end_date, frame_id)
