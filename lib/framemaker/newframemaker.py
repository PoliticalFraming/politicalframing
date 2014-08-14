"""This module allows the user to build frames .

Vocabulary:
Frame - a set of wordnet.synset objects that are collectivey related to a particular object

Functions:
pickleframe(word)
picklemultiframe(framewords,word)
addset2pickledframe(frame, myset)
load(word)
makeframe(frameword)

"""

from nltk.corpus import wordnet
from sets import Set
import wordnettools

def getSynsets(word):
	"""Returns synsets for a particular word."""
	return wordnet.synsets(word)

def getWords(synset):
	"""Returns all framing words associated with the synset."""

	words = Set() # words to include in frame

	for subsynset in (wordnettools.gethypernymsrecursive(synset)
		+ wordnettools.getlemmas(synset)
        + wordnettools.getrelatedforms(synset)
        + wordnettools.gethyponymsrecursive(synset)
        + wordnettools.getdomainterms(synset)):
         words.add(wordnettools.getnamepretty(subsynset))

	return map(lambda x: x, words) # return list

def getSynsetMetadata(synset):
	"""Returns metadata related to a synset"""
	related_synsets = wordnettools.getrelatedforms(synset)
	definition = synset.definition
	examples = synset.examples

	return {"related_synsets": related_synsets,
			"definition": definition,
			"examples": examples}

