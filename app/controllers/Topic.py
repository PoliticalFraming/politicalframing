from app import app, api
from peewee import *

from app.models.Topic import Topic
from flask_peewee.rest import RestAPI, RestResource

class TopicResource(RestResource):
	paginate_by = 30

	def get_api_name(self):
		return "topics"
        
api.register(Topic, TopicResource)