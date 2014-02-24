from app import app, api, db
from peewee import *

from app.models.frame import Frame
from app.models.topic import Topic
from app.models.analysis import Analysis

from flask.ext.restful import Resource, fields, reqparse
from datetime import datetime
from dateutil import parser as dateparser



topic_plot_fields = {
	'democrat_speeches':fields.List(fields.Integer),
	'republican_speeches':fields.List(fields.Integer),
	'start_dates':fields.DateTime,
	'end_dates':fields.DateTime
}

frame_plot_fields = {
	'ratios':fields.List(fields.Float),
	'start_dates':fields.DateTime,
	'end_dates':fields.DateTime
}

analysis_fields = {
	'topic_plot':fields.Nested(topic_plot_fields),
	'frame_plot':fields.Nested(frame_plot_fields)
}

parser = reqparse.RequestParser()

class AnalysisListController(Resource):

	parser.add_argument('frame', type = str, required = True, location = 'values')
	parser.add_argument('phrase', type = str, required = True, location = 'values')
	parser.add_argument('start_date', type = str, required = False, location = 'values')
	parser.add_argument('end_date', type = str, required = False, location = 'values')
	parser.add_argument('states', type = list, required = False, location = 'values')
	parser.add_argument('analysis_id', type = int, required = False, location = 'values')

	def get(self):
		"""Search persistant storage for analysis matching argument paramenters."""
		pass

	def post(self):
		"""Compute analysis. Place in persistant storage."""
		args = parser.parse_args()

		if args['start_date']: 
			args['start_date'] = dateparser.parse(args['start_date']).date()
			args['end_date'] = dateparser.parse(args['start_date']).date()

		analysis_id = Analysis.compute_analysis(
			topic = args.get('phrase'), 
			frame = args.get('frame'), 
			start_date=args.get('start_date'), 
			end_date=args.get('end_date'), 
			states=args.get('states'))

		return analysis_id



class AnalysisController(Resource):

	parser.add_argument('analysis_id', type=int, required=True, location='values')

	def get(self):
		"""
		Return percent complete (meta). 
		Return either empty json or completed frame and topic plot (text).
		"""
		pass

	def put(self):
		"""Update analysis in persistant storage"""
		pass

	def delete(self):
		"""Delete analysis from persistant storage"""
		pass

	
api.add_resource(AnalysisController, '/api/analyses/', endpoint = 'analyses')
api.add_resource(AnalysisListController, '/api/analyses/<string:speech_id>/', endpoint = 'analysis')