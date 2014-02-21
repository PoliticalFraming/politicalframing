from app import app, api, db
from peewee import *

from app.models.Topic import Topic, get_topic

from flask.ext.restful import Resource, reqparse, fields, marshal_with
from flask_peewee.utils import get_dictionary_from_model

from dateutil import parser as dateparser

topic_fields = {
	'topic_id': fields.String,
	'phrase': fields.String
}

parser = reqparse.RequestParser()

class TopicController(Resource):

	def get(self, topic_id):
		print topic_id
		topic = Topic.get(Topic.topic_id == topic_id)
		return get_dictionary_from_model(topic)

class TopicListController(Resource):

	parser.add_argument('page', type = int, required = False, location = 'values')

	def get(self):
		args = parser.parse_args()
		if not args['page']: args['page'] = 1
		query = Topic.select().order_by(Topic.topic_id)
		count = query.count()
		topics = map(lambda x: get_dictionary_from_model(x), query.paginate(args['page'],20))
		
		return {
			'meta': {'count':count},
			'data': topics
			}
	
	# def post(self):
		# args = parser.parse_args()
		# user = Topic(username = args['username'], password = hash_pass(args['password']), email = args['email'])
		# db.session.add(user)
		# db.session.commit()
		# return "yay life"

api.add_resource(TopicListController, '/api/topics/', endpoint = 'topics')
api.add_resource(TopicController, '/api/topics/<int:topic_id>/', endpoint = 'topic')