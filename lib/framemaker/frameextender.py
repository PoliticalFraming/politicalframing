from nltk.corpus import wordnet
from sets import Set
import framemaker
from preprocessor import removestops, removepunctuation
from wordnettools import gethyponymsrecursive

## HOLY CRAP WEIGHTED FRAMES !!!
def flatten(l):
  return  [item for sublist in l for item in sublist]

def frameextension(synset):
	extension = []

	# Get words in definition of this synset
	extension += removestops(removepunctuation(synset.definition)).split()
	# Get words in example of this synset
	wordlists = [removestops(removepunctuation(example)).split() for example in synset.examples]
	extension += reduce(lambda x,y: x+y, wordlists, [])

	# Get hyponyms recursively
	for hyponym in gethyponymsrecursive(synset):
		definitionwords = removestops(removepunctuation(hyponym.definition)).split()
		examplewordlists = [removestops(removepunctuation(example)).split() for example in hyponym.examples]
		examplewords = reduce(lambda x,y: x+y, wordlists, [])
		extension += definitionwords
		extension += examplewords

	return set(extension)

if __name__ == "__main__":
	crime = wordnet.synset('crime.n.01')
	print frameextension(crime)
	import pdb; pdb.set_trace()
