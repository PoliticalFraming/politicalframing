from app import app, api
from peewee import *

from app.models.Speech import Speech
from app.models.Frame import Frame, get_frame
from app.models.SpeechTopic import SpeechTopic

from app.controllers.Speech import SpeechResource

from flask_peewee.rest import RestAPI, RestResource

from flask import request
from peewee import DJANGO_MAP



def highlight_speech(speech, frame):
	''' Takes a speech and modifies the speech.speaking variable to be
	a list containing a single string with frame words bolded. '''
	#maybe can be written more efficiently
	speaking = eval(speech.get('speaking'))
	# return speech
	frame = frame.word_string.split(' ')
	highlighted_text = ""
	
	for sentence in speaking:
		for word in sentence.split():  #change this to NLTK TOKENIZER
			if word in frame:
				highlighted_text += ' <strong>' + word + '</strong> '
			else:
				highlighted_text += ' ' + word + ' '

	speech['speaking'] = highlighted_text
	return speech

class SpeechTopicResource(RestResource):
	paginate_by = 100
	include_resources = {'speech': SpeechResource}
	highlighted_frame = None

	def get_api_name(self):
		return "speechtopics"

	def process_query(self, query):
		#modified to handle topics
		
		raw_filters = {}

		# clean and normalize the request parameters
		for key in request.args:
			orig_key = key
			if key.startswith('-'):
				negated = True
				key = key[1:]
			else:
				negated = False
			if '__' in key:
				expr, op = key.rsplit('__', 1)
				if op not in DJANGO_MAP:
					expr = key
					op = 'eq'
			else:
				expr = key
				op = 'eq'
			raw_filters.setdefault(expr, [])
			raw_filters[expr].append((op, request.args.getlist(orig_key), negated))

		# do a breadth first search across the field tree created by filter_fields,
		# searching for matching keys in the request parameters -- when found,
		# filter the query accordingly
		queue = [(self._field_tree, '')]
		while queue:
			node, prefix = queue.pop(0)
			for field in node.fields:
				filter_expr = '%s%s' % (prefix, field.name)
				if filter_expr in raw_filters:
					for op, arg_list, negated in raw_filters[filter_expr]:
						query = self.apply_filter(query, filter_expr, op, arg_list)

			for child_prefix, child_node in node.children.items():
				queue.append((child_node, prefix + child_prefix + '__'))

		for myfilter in raw_filters:
			if myfilter=='frame':
				my_frame = get_frame(raw_filters['frame'][0][1][0])
				# query = query.join(SpeechTopic).where(SpeechTopic.topic==my_topic)
				print "I FOUND A FRAME %d IN THE URL!!!!!!!!!!!!!!!!!!!!!!!!!!" % my_frame.frame_id
				self.highlighted_frame = my_frame

		print query
		return query

	def apply_filter(self, query, expr, op, arg_list):
		## speaker_state override
		## This will break functionality when multiple paramters are passed in
		## using repeated GET parameters:
		## localhost:5000?param1__in=x&param1__in=y
		## It will also break when x or y (from above) have a ',' in its value.
		if op == 'in' and expr == 'speech__speaker_state':
			arg_list = arg_list[0].split(',')

		return super(SpeechTopicResource, self).apply_filter(query, expr, op, arg_list)

	def get_request_metadata(self, paginated_query):
		response = super(SpeechTopicResource, self).get_request_metadata(paginated_query)

		#Add number of results to metadata
		response['count']=(paginated_query.query.count())
		return response

	def apply_ordering(self, query):
		ordering = request.args.get('ordering') or ''
		if ordering:
			desc, column = ordering.startswith('-'), ordering.lstrip('-')
			fields = self.model._meta.fields

			for child_prefix, child_node in self._field_tree.children.items():
				for n in child_node.fields:
					fields[n.db_column] = n

			if column in fields:
				field = self.model._meta.fields[column]
				query = query.join(Speech)
				query = query.order_by(field.asc() if not desc else field.desc())
			print "end"
		return query


	def prepare_data(self, obj, data):
		speech_data = data['speech']

		speech_data['relevance'] = data['relevance']
		speech_data['topic'] = data['topic']

		# print "========================================="
		# print (speech_data.get('speaking'))
		# print "========================================="
		if speech_data.get('speaking') != None and self.highlighted_frame!=None:
		  example_frame = Frame.get(Frame.frame_id==1)
		  highlight_speech(speech_data, self.highlighted_frame)

		return speech_data

api.register(SpeechTopic, SpeechTopicResource)