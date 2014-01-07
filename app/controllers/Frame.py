from app import app, api
from peewee import *

from flask_peewee.rest import RestAPI, RestResource
from app.models.Frame import Frame

from flask.ext.cors import origin

class FrameResource(RestResource):
	paginate_by = 30
	def get_api_name(self):
		return "frames"

api.register(Frame, FrameResource)