from app import app, api, db
from peewee import *

from app.models.frame import Frame
from app.models.analysis import Analysis

from flask.ext.restful import Resource, reqparse, fields, marshal_with
from flask_peewee.utils import get_dictionary_from_model
from datetime import datetime
from dateutil import parser as dateparser

topic_plot_fields = {
	'democrat_speeches': fields.List(fields.Integer),
	'republican_speeches': fields.List(fields.Integer),
	'start_dates': fields.DateTime,
	'end_dates': fields.DateTime
}

frame_plot_fields = {
	'ratios': fields.List(fields.Float),
	'start_dates': fields.DateTime,
	'end_dates': fields.DateTime
}

analysis_fields = {
	'topic_plot': fields.Nested(topic_plot_fields),
	'frame_plot': fields.Nested(frame_plot_fields)
}

analysis_marshall = { 
	'meta': fields.Raw,
	'data': fields.Nested(analysis_fields)
}

parser = reqparse.RequestParser()

class AnalysisListController(Resource):

	parser.add_argument('id', type = int, required = False, location = 'json')
	parser.add_argument('frame', type = int, required = True, location = 'json')
	parser.add_argument('phrase', type = str, required = True, location = 'json')
	parser.add_argument('start_date', type = str, required = False, location = 'json')
	parser.add_argument('end_date', type = str, required = False, location = 'json')
	parser.add_argument('states', type = list, required = False, location = 'json')

	def get(self):
		"""Search persistant storage for analysis matching argument paramenters."""
		pass

	@marshal_with(analysis_marshall)
	def post(self):
		"""Compute analysis. Place in persistant storage."""
		args = parser.parse_args()

		if args['start_date']: 
			args['start_date'] = dateparser.parse(args['start_date']).date()
			args['end_date'] = dateparser.parse(args['start_date']).date()

		## HI
		## HELLO
		## HI
		## DO THIS KAAY THX
		# move this code the fuck out of here!!!!!!!!!!!!!!!!!!!!!!!!
		analysis_obj = Analysis.compute_analysis(
			phrase = args.get('phrase'), 
			frame = args.get('frame'),
			start_date = args.get('start_date'), 
			end_date = args.get('end_date'), 
			states = args.get('states'),
			to_update=False
		)

		return { 'meta':null, 'data': get_dictionary_from_model(analysis_obj) }

class AnalysisController(Resource):

	# parser = reqparse.RequestParser()
	# parser.add_argument('id', type=int, required=True, location='values')

	@marshal_with(analysis_marshall)
	def get(self, id):
		"""
		Return percent complete (meta). 
		Return either empty json or completed frame and topic plot (text).
		"""
		analysis_obj = Analysis.get(Analysis.id == id)
		info = analysis_obj.check_if_complete()

		return { 'meta':info, 'data': get_dictionary_from_model(analysis_obj) }

	def put(self, id):
		"""Update analysis in persistant storage"""
		pass


api.add_resource(AnalysisListController, '/api/analyses/', endpoint = 'analyses')
api.add_resource(AnalysisController, '/api/analyses/<int:id>/', endpoint = 'analysis')