from app import app, api
from peewee import *

from app.models.Speech import Speech, get_speeches
from app.models.Topic import Topic, get_topic
from app.models.SpeechTopic import SpeechTopic

from flask_peewee.rest import RestAPI, RestResource

from flask import request
from peewee import DJANGO_MAP

class SpeechResource(RestResource):
    paginate_by = 30
    # exclude = ('speaking')

    def get_api_name(self):
        return "speeches"

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
            if myfilter=='topic':
                my_topic = get_topic(raw_filters['topic'][0][1][0])
                query = query.join(SpeechTopic).where(SpeechTopic.topic==my_topic)

        print query
        return query

    def apply_filter(self, query, expr, op, arg_list):
    	## speaker_state override
    	## This will break functionality when multiple paramters are passed in
    	## using repeated GET parameters:
    	## localhost:5000?param1__in=x&param1__in=y
    	## It will also break when x or y (from above) have a ',' in its value.
    	if op == 'in' and expr == 'speaker_state':
    		arg_list = arg_list[0].split(',')

    	return super(SpeechResource, self).apply_filter(query, expr, op, arg_list)

    def get_request_metadata(self, paginated_query):
    	response = super(SpeechResource, self).get_request_metadata(paginated_query)

    	#Add number of results to metadata
    	response['count']=(paginated_query.query.count())
    	return response

api.register(Speech, SpeechResource)