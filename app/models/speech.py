from app import app, db, si
from peewee import *
from dateutil import parser
from datetime import datetime

from app.models.frame import get_frame
from sunburnt import SolrInterface

class Speech(dict):
  def __init__(self, *args, **kwargs):
    self.speech_id = kwargs.get('speech_id')
    self.bills = kwargs.get('bills')
    self.biouguide = kwargs.get('biouguide')
    self.capitolwords_url = kwargs.get('capitolwords_url')
    self.chamber = kwargs.get('chamber')
    self.congress = kwargs.get('congress')
    self.date = kwargs.get('date')
    self.number = kwargs.get('number')
    self.order = kwargs.get('order')
    self.origin_url = kwargs.get('origin_url')
    self.pages = kwargs.get('pages')
    self.session = kwargs.get('session')
    self.speaker_first = kwargs.get('speaker_first')
    self.speaker_last = kwargs.get('speaker_last')
    self.speaker_party = kwargs.get('speaker_party')
    self.speaker_raw = kwargs.get('speaker_raw')
    self.speaker_state = kwargs.get('speaker_state')
    self.speaking = kwargs.get('speaking')
    self.title = kwargs.get('title')
    self.volume = kwargs.get('volume')
    self.__dict__ = self
  @staticmethod
  def get(**kwargs):
    kwargs['speech_id'] = kwargs.get('speech_id') or ''
    kwargs['start_date'] = parser.parse(kwargs['start_date']).date() if kwargs.get('start_date') else datetime(1994,1,1)
    kwargs['end_date'] = parser.parse(kwargs['end_date']).date() if kwargs.get('end_date') else datetime.now()
    si.query(id=kwargs['speech_id'], speaking=kwargs['phrase'], date__range=(kwargs['start_date'], kwargs['end_date']))
  def highlight_speech(speech, frame):
    speech['speaking'] = \
      map(lambda sentence: 
        " ".join(map(lambda word: "<strong>" + word + "</strong>" if word in frame.word_string.split(' ') else word, 
          sentence.split())), 
      eval(speech.get('speaking')))
    return speech