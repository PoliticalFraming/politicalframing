from app import app, api, db
from peewee import *

from app.models.frame import Frame

from flask.ext.restful import Resource, reqparse, fields, marshal_with
from flask_peewee.utils import get_dictionary_from_model

from dateutil import parser as dateparser

frame_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'description': fields.String,
	'generation': fields.Integer,
	'seed_word': fields.String,
	'word_count': fields.Integer,
	'word_string': fields.String
}

frame_marshall = { 
	'meta': fields.Raw,
	'data': fields.Nested(frame_fields)
}

parser = reqparse.RequestParser()

class FrameController(Resource):

	@marshal_with(frame_marshall)
	def get(self, id):
		frame = Frame.get(Frame.id == id)
		return { 'meta': null, 'data': get_dictionary_from_model(frame) }

	@marshal_with(frame_marshall)
	def put(self, id, word_string):
		frame = Frame.get(frame.id == id)
		frame.word_string = word_string
		return { 'meta': null, 'data': get_dictionary_from_model(frame) }

class FrameListController(Resource):

	parser.add_argument('page', type = int, required = False, location = 'values')

	@marshal_with(frame_marshall)
	def get(self):
		args = parser.parse_args()
		if not args['page']: args['page'] = 1
		query = Frame.select().order_by(Frame.id)
		count=query.count()
		frames = map(lambda x: get_dictionary_from_model(x), query.paginate(args['page'],20))
		
		return { 'meta': {'count':count}, 'data': frames }

	@marshal_with(frame_marshall)
	def post(self, name, description, generation, seed_word, word_count, word_string):
		frame = Frame(name=name,
		 description=description, 
		 generation=generation, 
		 seed_word=seed_word, 
		 word_count=word_count, 
		 word_string=word_string)
		return { 'meta': null, 'data': get_dictionary_from_model(frame) }

api.add_resource(FrameListController, '/api/frames/', endpoint = 'frames')
api.add_resource(FrameController, '/api/frames/<int:id>/', endpoint = 'frame')