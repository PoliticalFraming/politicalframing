from app import app, api, db
from peewee import *

from app.models.frame import Frame
from app.models.analysis import Analysis

from flask.ext.restful import Resource, reqparse, fields, marshal_with, marshal
from flask_peewee.utils import get_dictionary_from_model
import datetime
from dateutil import parser as dateparser
import json

topic_plot_fields = {
	'subgroup_a_counts': fields.List(fields.Integer),
	'subgroup_b_counts': fields.List(fields.Integer),
	'start_dates': fields.List(fields.Raw),
	'end_dates':  fields.List(fields.Raw),
	'ylabel': fields.String,
	'title': fields.String
}

frame_plot_fields = {
	'ratios': fields.List(fields.Raw), #fields.Float
	'start_dates': fields.List(fields.Raw),
	'end_dates': fields.List(fields.Raw),
	'ylabel': fields.String,
	'title': fields.String
}

wordcount_plot_fields = {
    'title': fields.String,
    'ylabel': fields.String,
    'start_dates': fields.List(fields.Raw),
    'end_dates': fields.List(fields.Raw),
    'subgroup_a_counts': fields.List(fields.Raw),
    'subgroup_b_counts': fields.List(fields.Raw)
}

analysis_fields = {
	'id': fields.Integer,
	'frame': fields.Integer,
	'phrase': fields.String,
	'start_date': fields.Raw, #DateTime
	'end_date': fields.Raw, #DateTime
	'topic_plot': fields.Nested(topic_plot_fields),
	'frame_plot': fields.Nested(frame_plot_fields),
	'wordcount_plot': fields.Nested(wordcount_plot_fields)
}

analysis_marshall = {
	'meta': fields.Raw,
	'data': fields.Nested(analysis_fields)
}

class AnalysisListController(Resource):

	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('page', type = int, required = False, location = 'values')

		"""Search persistant storage for analysis matching argument paramenters."""
		args = parser.parse_args()
		if not args['page']: args['page'] = 1
		query = Analysis.select().order_by(Analysis.id)
		count=query.count()
		analyses = map(lambda x: get_dictionary_from_model(x), query) #query.paginate(args['page'],20)

		return { 'meta': {'count':count}, 'data': analyses }


	@marshal_with(analysis_marshall)
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id', type = int, required = False, location = 'json')
		parser.add_argument('frame', type = int, required = True, location = 'json')
		parser.add_argument('phrase', type = str, required = True, location = 'json')
		parser.add_argument('start_date', type = str, required = False, location = 'json')
		parser.add_argument('end_date', type = str, required = False, location = 'json')

		#subgroup a specific args
		parser.add_argument('states_a', type = list, required = False, location = 'json')
		parser.add_argument('party_a', type = str, required = True, location = 'json') #D or R

		#subgroup b specific args
		parser.add_argument('states_b', type = list, required = False, location = 'json')
		parser.add_argument('party_b', type = str, required = True, location = 'json') #D or R

		"""Compute analysis. Place in persistant storage."""
		args = parser.parse_args()

		# if args['start_date']:
		# 	args['start_date'] = dateparser.parse(args['start_date']).date()
		# 	args['end_date'] = dateparser.parse(args['start_date']).date()

		analysis_obj = Analysis.compute_analysis(
			id = args.get('id'),
			phrase = args.get('phrase'),
			frame = args.get('frame'),
			start_date = args.get('start_date'),
			end_date = args.get('end_date'),

			#Subgroups to Compare
			states_a = args.get('states_a'),
			party_a = args.get('party_a'),
			states_b = args.get('states_b'),
			party_b = args.get('party_b'),
			to_update = False
		)

		data = get_dictionary_from_model(analysis_obj)

		return { 'meta': None, 'data': data }

class AnalysisController(Resource):

	# parser = reqparse.RequestParser()
	# parser.add_argument('id', type=int, required=True, location='values')

	# curl -X POST -d '{"phrase": "immigration", "frame": 1}' http://localhost:5000/api/analyses/ -H "Content-Type: application/json"

	@marshal_with(analysis_marshall)
	def get(self, id):
		"""
		Return percent complete (meta).
		Return either empty json or completed frame and topic plot (text).
		"""
		analysis_obj = Analysis.get(Analysis.id == id)
		info = analysis_obj.check_if_complete()

		data = get_dictionary_from_model(analysis_obj)
		data['topic_plot'] = eval(data['topic_plot']) if data['topic_plot'] else None
		data['frame_plot'] = eval(data['frame_plot']) if data['frame_plot'] else None
		data['wordcount_plot'] = eval(data['wordcount_plot']) if data['wordcount_plot'] else None

		return { 'meta': info, 'data': data }

	def put(self, id):
		"""Update analysis in persistant storage"""
		pass


api.add_resource(AnalysisListController, '/api/analyses/', endpoint = 'analyses')
api.add_resource(AnalysisController, '/api/analyses/<int:id>/', endpoint = 'analysis')