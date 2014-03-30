from __future__ import division

from app import si
import httplib2
from dateutil import parser
from datetime import datetime

from sunburnt import RawString

from app.models.frame import Frame
import re

class Speech(object):
  
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
    self.speaker_first = kwargs.get('speaker_firstname')
    self.speaker_last = kwargs.get('speaker_lastname')
    self.speaker_party = kwargs.get('speaker_party')
    self.speaker_raw = kwargs.get('speaker_raw')
    self.speaker_state = kwargs.get('speaker_state')
    self.speaking = kwargs.get('speaking')
    self.title = kwargs.get('title')
    self.volume = kwargs.get('volume')

  @staticmethod
  def get(rows, start, **kwargs):
    """
    Input
      speech_id
      start_date
      end_date
      phrase
      rows - the number of records to get from solr
      start - where to start getting records in solr (offset)
      frame
      order

    Output
      List of output
    """
    query = {}

    if kwargs.get('speech_id'):
      query['id'] = kwargs['speech_id']
    elif kwargs.get('phrase'):
      query['speaking'] = kwargs['phrase']

    kwargs['start_date'] = parser.parse(kwargs['start_date']) if kwargs.get('start_date') else datetime(1994,1,1)
    kwargs['end_date'] = parser.parse(kwargs['end_date']) if kwargs.get('end_date') else datetime.now()
    query['date__range'] = (kwargs['start_date'], kwargs['end_date'])
    query['speaker_party__range'] = ("*", "*")
    # RawString('[* TO *]')

    # 
    # if the number of docs is less than numFound, then this is the pagination offset

    if kwargs.get('speaker_party'):
      query['speaker_party'] = kwargs['speaker_party']


    if kwargs.get('order'):

      if kwargs.get('order') != "frame":
        response = si.query(**query).paginate(rows=rows, start=start).exclude(speaker_party=None).sort_by(kwargs.get('order')).execute()
      else:
        # IGNORING ROWS and IGNORE START AND DOWNLOADING ALL SPEECHES WHEN ORDERING BY FRAME
        # HOLY SHIT THIS IS TERRIBLE
        # LIKE SERIOUSLY TERRIBLE
        # PLEASE CHANGE THIS.
        # ~ RIP good coding practices ~
        print "ordering by frame"
        numFound = si.query(**query).paginate(rows=0, start=0).exclude(speaker_party=None).execute().result.numFound
        print numFound
        response = si.query(**query).paginate(rows=numFound, start=0).exclude(speaker_party=None).execute()
        frame = Frame.get(Frame.id == kwargs['frame'])
        response.result.docs = Speech.order_by_frame_prevalance(response.result.docs, frame)
    else:
      response = si.query(**query).paginate(rows=rows, start=start).exclude(speaker_party=None).execute()
    
    speeches = response.result.docs
    current_count = response.result.numFound
    current_start = response.result.start

    # TODO: improve this
    if kwargs.get('frame') and kwargs.get('highlight'):
      frame = Frame.get(Frame.id == kwargs['frame'])
      for speech in speeches:
          speech = Speech.highlight_speech(speech, frame)

    speeches_dict = {
      'count': current_count,
      'start': current_start,
      'speeches': speeches
    }

    return speeches_dict

  @staticmethod
  def highlight_speech(speech, frame):
    """
    Input
      speech dict
      frame dict

    Output
      speech object with highlighted 'speaking'
    """
    frame = frame.word_string.split(' ')

    speech['speaking'] = \
      map(lambda sentence: 
        "".join(map(lambda word: "<span class='highlight'>" + word + "</span>" if word in frame else word, 
          re.split(r'(\W+)',sentence))), 
      speech['speaking'])

    return speech

  @staticmethod
  def order_by_frame_prevalance(speeches, frame):
      print ("ORDER BY FRAME PREVALANCE")
      speech_prevalances = [] #array of tuples containing speeches and ther prevalance values
      for speech in speeches:
          speech_words = " ".join(speech['speaking']).lower().split()
          framewords_count = 0
          for word in frame.word_string.split():
              if word in speech_words:
                framewords_count += 1

          frame_prevalance = framewords_count / len(speech_words)

          speech_prevalances.append((speech, frame_prevalance))

      for blah in sorted(speech_prevalances, key=lambda x: x[1], reverse=True):
        print blah[0]['document_title'], blah[1]

      return map(lambda x:x[0] , sorted(speech_prevalances, key=lambda x: x[1], reverse=True))

      # ################################################################
      # # Better Implementaiton Stub - if simple counts don't work well
      # ################################################################
      #for speech in speeches:
      #     frame_words = {} #dict containing word:count_in_speech
      #     for word in frame.word_string.split():
      #         if word in speech.speaking:
      #             frame_words[word] = frame_words.get(word,0) + 1
      #     # do better ordering using frame_words dictionary 
      #     # (maybe something like tf/idf based counts) 
      # ################################################################