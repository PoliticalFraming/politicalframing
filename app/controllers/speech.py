from __future__ import division

from app import app, api, db
from peewee import *
from app.models.speech import Speech
from flask.ext.restful import Resource, reqparse, fields, marshal_with
from dateutil import parser as dateparser
import json
import math

speech_fields = {
    'id': fields.String,
    'bills': fields.String,
    'biouguide': fields.String,
    'capitolwords_url': fields.String,
    'chamber': fields.String,
    'congress': fields.Integer,
    'date': fields.DateTime,
    'number': fields.Integer,
    'order': fields.Integer,
    'origin_url': fields.String,
    'pages': fields.String,
    'session': fields.Integer,
    'speaker_first': fields.String,
    'speaker_last': fields.String,
    'speaker_party': fields.String,
    'speaker_raw': fields.String,
    'speaker_state': fields.String,
    'speaking': fields.String,
    'title': fields.String,
    'volume': fields.Integer
}

parser = reqparse.RequestParser()

class SpeechController(Resource):
  def get(self, id):
    speech = Speech.get(Speech.id == id)

class SpeechListController(Resource):
  parser.add_argument('phrase', type = str, required = True, location = 'values')
  parser.add_argument('frame', type = int, required = False, location = 'values')
  parser.add_argument('start_date', type = str, required = False, location = 'values')
  parser.add_argument('end_date', type = str, required = False, location = 'values')
  parser.add_argument('page', type = int, required = False, location = 'values')
  parser.add_argument('order', type = str, required = False, location = 'values')
  parser.add_argument('states', type = str, required = False, location = 'values')

  def get(self):
    args = parser.parse_args()
    if not args['page']: args['page'] = 1
    else: args['page'] = int(args['page'])

    rows = 10

    speeches_dict = Speech.get(
      phrase = args.get('phrase'), 
      frame = args.get('frame'), 
      start_date = args.get('start_date'), 
      end_date = args.get('end_date'),
      rows = rows,
      start = rows * (args['page'] - 1)
    )

    count = speeches_dict['count']
    pages = math.ceil(count/rows)
    start = speeches_dict['start']

    return {
      'meta': {
        'count': count,
        'start': start,
        'pages': pages,
        'page': args['page']
      },
      'data': speeches_dict['speeches']
    }

api.add_resource(SpeechListController, '/api/speeches/', endpoint = 'speeches')
api.add_resource(SpeechController, '/api/speeches/<string:id>/', endpoint = 'speech')