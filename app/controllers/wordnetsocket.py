from app import app
from framemaker import framemaker
# from sets import Set
import json
from flask import request

@app.route('/api/wordnetsocket/getQuestions/<word>')
def get_questions(word):
	"""Input a word, get some questions. A question is a dict that contains a 
	feild called 'name' - that is the name of the synset that you can pass back
	"""
	synsets = framemaker.getSynsets(word)
	questions = []
	for synset in synsets:
		metadata = framemaker.getSynsetMetadata(synset)
		metadata['related_synsets'] = map(lambda synset: synset.name, metadata['related_synsets'])
		questions.append(metadata)
	return json.dumps(questions)

@app.route('/api/wordnetsocket/getWords/')
def get_words():
	""" 
	Parameter - list of synsets, comma separated
	Returns - set of words
	"""
	synsets = request.args.get('synsets', '')
	synsets = synsets.split(',')

	# Return unique list of getWords for all synsets
	words = []
	for synset in synsets:
		synset = framemaker.getSynset(synset)
		words = list(set(words + framemaker.getWords(synset)))
	return json.dumps(words)

	# Return dict of getWords for each synset
	# words = {}
	# for synset in synsets:
	# 	words[synset] = framemaker.getWords(framemaker.getSynset(synset))
	# return json.dumps(words)
	