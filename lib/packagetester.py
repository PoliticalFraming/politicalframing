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
	import pdb; pdb.set_trace()
	return basic_frame

# ### Methodology 2: Mulitple Seed Word

def multiword_basic_frame():

	framewords = []
	quit = False

	while not quit:
		user_input = raw_input("Enter 'seed' word for frame (-1 to quit): ")
		if user_input == '-1':
			quit = True
			break
		else:
			framewords.append(user_input)

	print framewords

	frame = reduce(lambda x,y: set(x).union(set(y)), [basic_frame(frameword) for frameword in framewords], [])
	print frame
	return frame


def flatten(l):
	return	[item for sublist in l for item in sublist]

def original_extended_frame(frameword):
	synsets = getSynsets(frameword)
	selected_synsets = picksynsets(synsets)

	frame = {word for synset in selected_synsets for word in getWords(synset)}

	print t.red("\nSeed Word: %s" % frameword)
	print t.red("Selected Synsets: %s\n" % selected_synsets)

	for synset in selected_synsets:
		print t.red("Words for %s" % synset.name)
		print t.green(str(getSynsetMetadata(synset)))
		words = getWords(synset)
		print str(words) + "\n"

	print t.red("Basic frame for %s" % str(selected_synsets))
	print frame


	# # Make Extended Frame
	related_synsets = flatten([getrelatedforms(synset) for synset in selected_synsets])
	print t.red("\nRelated yets: %s" % str(related_synsets))

	for synset in related_synsets:
		print t.red("Extension for %s" % synset.name)
		print t.green(str(getSynsetMetadata(synset)))
		extension = frameextension(synset)
		frame = frame.union(extension)
		print str(extension) + "\n"


	print "------------------frame-------------------"
	print frame
	# import pdb; pdb.set_trace()




# ### LEARNING MORE ABOUT WORDNET
frameword = raw_input("Enter 'seed' word for frame: ")
basic_frame(frameword)
# multiword_basic_frame()
