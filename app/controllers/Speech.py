from app import app, api, db
from peewee import *

from app.models.Speech import Speech, get_speeches_in_date_order
from app.models.Topic import Topic, get_topic
from app.models.SpeechTopic import SpeechTopic

from flask.ext.restful import Resource, reqparse, fields, marshal_with
from flask_peewee.utils import get_dictionary_from_model

from dateutil import parser as dateparser

speech_fields = {
    'speech_id': fields.String,
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

    def get(self, speech_id):
        print speech_id
        speech = Speech.get(Speech.speech_id == speech_id)
        return get_dictionary_from_model(speech)

class SpeechListController(Resource):

    parser.add_argument('topic', type = int, required = True, location = 'values')
    parser.add_argument('page', type = int, required = False, location = 'values')
    parser.add_argument('start_date', type = str, required = False, location = 'values')
    parser.add_argument('end_date', type = str, required = False, location = 'values')
    parser.add_argument('states', type = str, required = False, location = 'values')

    def get(self):
        args = parser.parse_args()
        if not args['page']: args['page'] = 1
        if args['start_date']: args['start_date'] = dateparser.parse(args['start_date']).date()
        if args['end_date']: args['end_date'] = dateparser.parse(args['end_date']).date()

        query = Speech.select() \
            .join(SpeechTopic).where(SpeechTopic.topic==args['topic']) \
            .order_by(Speech.speech_id)
        if args['states']:
            query = query.where(Speech.speaker_state << args['states'].split(','))

        if args['start_date'] != None or args['end_date'] != None:
            if args['start_date'] == None: query=query.where(Speech.date <= args['end_date'])
            elif args['end_date'] == None: query=query.where(Speech.date >= args['start_date'])
            else: query=query.where(Speech.date >= args['start_date']).where(Speech.date <= args['end_date'])

        count = query.count()

        speeches = map(lambda x: get_dictionary_from_model(x), query.paginate(args['page'],20))

        return {
            'meta': {'count':count},
            'data': speeches
            }
    

    # def post(self):
        # args = parser.parse_args()
        # user = Speech(username = args['username'], password = hash_pass(args['password']), email = args['email'])
        # db.session.add(user)
        # db.session.commit()
        # return "yay life"

api.add_resource(SpeechListController, '/api/speeches/', endpoint = 'speeches')
api.add_resource(SpeechController, '/api/speeches/<string:speech_id>/', endpoint = 'speech')