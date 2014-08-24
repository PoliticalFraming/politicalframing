"""
This file contains code that tests the packages in lib folder.
"""


from framemaker import *
from blessings import Terminal

t = Terminal()

### Methodology 1: Single Seed Word

# Make Basic Frame
def basic_frame(frameword):
	synsets = getSynsets(frameword)
	selected_synsets = picksynsets(synsets)

	basic_frame = {word for synset in selected_synsets for word in getWords(synset)}

	print t.red("\nSeed Word: %s" % frameword)
	print t.red("Selected Synsets: %s\n" % selected_synsets)

	for synset in selected_synsets:
		print t.red("Words for %s" % synset.name)
		print t.green(str(getSynsetMetadata(synset)))
		words = getWords(synset)
		print str(words) + "\n"

	print t.red("Basic frame for %s" % str(selected_synsets))
	print "%s\n" % basic_frame
	# import pdb; pdb.set_trace()


# ### Methodology 2: Mulitple Seed Word
def extended_frame():

	pass

### LEARNING MORE ABOUT WORDNET
frameword = raw_input("Enter 'seed' word for frame: ")
basic_frame(frameword)