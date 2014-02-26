from app import si
import httplib2
from dateutil import parser
from datetime import datetime

from sunburnt import RawString

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
      rows
      start
      frame

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
    response = si.query(**query).paginate(rows=rows, start=start).exclude(speaker_party=None).execute()
    speeches = response.result.docs
    current_count = response.result.numFound
    current_start = response.result.start

    # TODO: improve this
    if kwargs.get('frame') and kwargs.get('higlight'):
        for speech in speeches:
            speech = highlight_speech(speech['speaking'], frame)

    speeches_dict = {
      'count': current_count,
      'start': current_start,
      'speeches': speeches
    }

    return speeches_dict

  def highlight_speech(self, frame):
    """
    Input
      speech object
      frame object

    Output
      speech object with highlighted 'speaking'
    """
    frame = frame['word_string'].split(' ')

    self.speaking = \
      map(lambda sentence: 
        " ".join(map(lambda word: "<strong>" + word + "</strong>" if word in frame else word, 
          sentence.split())), 
      self.speaking)

    return self
