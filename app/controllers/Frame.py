from app import app, api, db
from peewee import *

from app.models.Frame import Frame

from flask.ext.restful import Resource, reqparse, fields, marshal_with
from flask_peewee.utils import get_dictionary_from_model

from dateutil import parser as dateparser

frame_fields = {
    'frame_id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'generation': fields.Integer,
    'seed_word': fields.String,
    'word_count': fields.Integer,
    'word_string': fields.String
}

parser = reqparse.RequestParser()

class FrameController(Resource):

    def get(self, frame_id):
        print frame_id
        frame = Frame.get(Frame.frame_id == frame_id)
        return get_dictionary_from_model(frame)

class FrameListController(Resource):

	parser.add_argument('page', type = int, required = False, location = 'values')

	def get(self):
		args = parser.parse_args()
		if not args['page']: args['page'] = 1
		query = Frame.select().order_by(Frame.frame_id).paginate(args['page'],20)
		frames = map(lambda x: get_dictionary_from_model(x), query)
		return frames

    # def post(self):
        # args = parser.parse_args()
        # user = Topic(username = args['username'], password = hash_pass(args['password']), email = args['email'])
        # db.session.add(user)
        # db.session.commit()
        # return "yay life"

api.add_resource(FrameListController, '/api/frames/', endpoint = 'frames')
api.add_resource(FrameController, '/api/frames/<int:frame_id>/', endpoint = 'frame')