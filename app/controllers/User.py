# from app import app, api
# from peewee import *

# from app.models.user import user

# from flask_peewee.rest import RestAPI, RestResource

# class UserResource(RestResource):
# 	paginate_by = 30
# 	def get_api_name(self):
# 		return "users"
        
# 	def get_request_metadata(self, paginated_query):
# 		response = super(SpeechResource, self).get_request_metadata(paginated_query)

# 		#Add number of results to metadata
# 		response['count']=(paginated_query.query.count())
# 		return response

# api.register(User, UserResource)