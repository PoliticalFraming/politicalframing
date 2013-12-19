from app import app, api
from peewee import *

from app.models.Topic import Topic
from flask_peewee.rest import RestAPI, RestResource

class TopicResource(RestResource):
	paginate_by = 100

	def get_api_name(self):
		return "topics"
        
api.register(Topic, TopicResource)