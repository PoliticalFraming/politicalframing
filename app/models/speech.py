from __future__ import division

from app import si
import app
import httplib2
from dateutil import parser
from datetime import datetime

from sunburnt import RawString
from sunburnt.search import SolrSearch

from app.models.frame import Frame
import re
import operator
from math import exp, log
import json

# import ipdb as pdb
# import ipdb

# from celery.contrib import rdb

class Speech(object):

  def __init__(self, *args, **kwargs):
    self.id = kwargs.get('id')
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
    self.frame_freq = kwargs.get('$frameFreq')
    self.norm = kwargs.get('$norm')
    self.score = kwargs.get('$score')
    self.term_vectors = kwargs.get('term_vectors')

  def belongs_to(self, subgroup):
    """True if speech is by someone in this subgroup"""
    if subgroup.party and subgroup.states:
      return (self.speaker_party.upper() == subgroup.party.upper()) and (self.speaker_state in subgroup.states)
    elif subgroup.party:
      return (self.speaker_party.upper() == subgroup.party.upper())
    elif subgroup.states:
      return (self.speaker_state in subgroup.states)
    else:
      raise "Subgroup has no party or state."

  @staticmethod
  def build_sunburnt_query(**kwargs):
    """
    Input
      id
      start_date
      end_date
      phrase
      rows - the number of records to get from solr
      start - where to start getting records in solr (offset)
      frame
      order
      states - list of 2 letter state abbreviations

    Output
      List of output
    """

    compulsory_params = {}
    optional_params = {}

    if kwargs.get('id'):
      compulsory_params['id'] = kwargs['id']
      solr_query = si.Q(**compulsory_params)
    elif kwargs.get('ids') and kwargs.get('phrase'):
      solr_query = si.Q()
      solr_query &= reduce(operator.or_, [si.Q(id=_id) for _id in kwargs['ids']])
    elif kwargs.get('phrase'):
      compulsory_params['speaking'] = kwargs['phrase']

      kwargs['start_date'] = parser.parse(kwargs['start_date']) if kwargs.get('start_date') else datetime(1994,1,1)
      kwargs['end_date'] = parser.parse(kwargs['end_date']) if kwargs.get('end_date') else datetime.now()

      #If states exist, add to kwargs and then to optional parameters
      if kwargs.get('states'):
        kwargs['states'] = kwargs.get('states').split(',')
        optional_params['speaker_state'] = si.query()
        # for state in kwargs['states']:
        #   optional_params['speaker_state'] |= si.Q(speaker_state=state)
        optional_params['speaker_state'] = reduce(operator.or_, [si.Q(speaker_state=state) for state in kwargs['states']])

      if kwargs.get('speaker_party'):
        compulsory_params['speaker_party'] = kwargs['speaker_party']

      compulsory_params['date__range'] = (kwargs['start_date'], kwargs['end_date'])
      compulsory_params['speaker_party__range'] = ("*", "*")

      solr_query = si.Q(**compulsory_params)
      if optional_params.get('speaker_state'):
        solr_query &= optional_params['speaker_state']
    else:
      print "ERRROR!"
      print kwargs

    solr_query = si.query(solr_query)
    solr_query = solr_query.exclude(speaker_party=None)

    return solr_query

  @staticmethod
  def get(rows, start, **kwargs):
    """
    Input
      id
      start_date
      end_date
      phrase
      rows - the number of records to get from solr
      start - where to start getting records in solr (offset)
      frame
      order
      states - list of 2 letter state abbreviations

    Output
      List of output
    """

    solr_query = Speech.build_sunburnt_query(**kwargs).paginate(rows=rows, start=start)

    if kwargs.get('order') and kwargs.get('order') not in ["frame", "tfidf", "idf", "termFreq"]:
      solr_query = solr_query.sort_by(kwargs.get('order'))

    # solr_query = solr_query.terms('speaking').terms(tf=True)
    params = solr_query.params()
    dict_params = dict(params)

    dict_params['norm'] = 'norm(speaking)'
    dict_params['tf'] = 'tf(speaking, %s)' % kwargs.get('phrase')
    dict_params['idf'] = 'idf(speaking, %s)' % kwargs.get('phrase')
    dict_params['tfidf'] = 'mul($tf, $idf)'
    dict_params['termFreq'] = 'termfreq(speaking, %s)' % kwargs.get('phrase')
    dict_params['fl'] = "*, score, $norm, $termFreq, $tf, $idf, $tfidf"
    dict_params['q'] += " AND {!frange l=8}$tfidf"
    if kwargs.get('order') == None or kwargs.get('order') == "tfidf":
      dict_params["sort"] = "$tfidf desc"

    if kwargs.get('frame') and kwargs.get('order') == "frame" and kwargs.get('analysis_id'):

      from app.models.analysis import Analysis

      frame_words = Frame.get(Frame.id == kwargs['frame']).word_string
      # analysis_obj = Analysis.get(Analysis.id == kwargs['analysis_id'])
      # key = "%s - %s" % (kwargs.get('start_date'), kwargs.get('end_date'))
      # vocabulary_proba = json.loads(analysis_obj.speech_windows)[key]
      # frame_vocabulary_proba =  { word: (abs(exp(vocabulary_proba.get(word)[0]) - exp(vocabulary_proba.get(word)[1]))) if vocabulary_proba.get(word) != None else 0 for word in frame_words.split() }
      # dict_params['frameFreq'] = "mul(sum(" + ", ".join(map(lambda word: "mul(termfreq(speaking,\"%s\"), %f)" % (word, frame_vocabulary_proba[word]), frame_words.split())) + "), $norm)"

      dict_params['frameFreq'] = "mul(sum(" + ", ".join(map(lambda word: "mul(termfreq(speaking,\"%s\"), %f)" % (word, 1), frame_words.split())) + "), $norm)"

      if dict_params.get('fl'):
        dict_params['fl'] += ", $frameFreq"
      else:
        dict_params['fl'] = '$frameFreq'

      dict_params["sort"] = "$frameFreq desc"

    params = zip(dict_params.keys(), dict_params.values())

    # print params

    result = si.schema.parse_response(si.conn.select(params))
    q = SolrSearch(si)
    response = q.transform_result(result, q.result_constructor)

    speeches = response.result.docs
    highlighting = response.highlighting
    term_vectors = response.term_vectors

    current_count = response.result.numFound
    current_start = response.result.start

    # TODO: improve this
    if kwargs.get('frame') and kwargs.get('highlight'):
      frame = Frame.get(Frame.id == kwargs['frame'])
      # pdb.set_trace()
      for speech in speeches:
          speech = Speech.highlight_speech(speech, frame)

    speeches_dict = {
      'count': current_count,
      'start': current_start,
      'speeches': speeches,
      'term_vectors': term_vectors,
      'highlighting': highlighting
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
    frame = frame.word_string.replace("\n", " ").split(' ')

    speech['speaking'] = \
      map(lambda sentence:
        "".join(map(lambda word: "<span class='highlight'>" + word + "</span>" if word in frame else word,
          re.split(r'(\W+)',sentence))),
      speech['speaking'])

    return speech

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
