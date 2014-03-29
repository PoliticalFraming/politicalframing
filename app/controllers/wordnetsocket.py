from app import app
from framemaker import framemaker
from sets import Set

@app.route('/api/wordnetsocket/getQuestions/<word>')
def get_questions(word):
	"""Input a word, get some questions. A question is a dict that contains a 
	feild called 'name' - that is the name of the synset that you can pass back
	"""
	synsets = framemaker.getSynsets(word)
	questions = []
	for synset in synsets:
		metadata = framemaker.getSynsetMetadata(synset)
		questions.append(metadata)
	return questions

@app.route('/api/wordnetsocket/getQuestions/<synsets>')
def get_words(synsets):
	""" 
	Parameter - list of synsets
	Returns - set of words
	"""
	words = Set()
	for synset in synsets:
		words = words.union(synset.getWords())
	return words