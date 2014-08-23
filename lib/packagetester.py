"""
This file contains code that tests the packages in lib folder.
"""


from framemaker import *

### Methodology 1: Single Seed Word

# Make Basic Frame
def method1():
	frameword = raw_input("Enter 'seed' word for frame: ")
	synsets = getSynsets(frameword)
	selected_synsets = picksynsets(synsets)
	basic_frame = reduce(lambda x,y: set(x).union(set(y)), [getWords(s) for s in selected_synsets], set([]))
	print "\n================================ output ================================\n"
	print "Basic frame for %s" % str(selected_synsets)
	print "%s\n" % basic_frame

	# # Make Extended Frame
	related_synsets = getrelatedforms(synsets[0])
	for synset in related_synsets:
		print "Extension for %s" % synset.name
		extension = frameextension(synset)
		print str(extension) + "\n"

	frame_extension = reduce(lambda x,y: set(x).union(set(y)), [getWords(s) for s in related_synsets], set([]))

	frame = basic_frame.union(frame_extension)

	print "------------------frame-------------------"
	print frame

# ### Methodology 2: Mulitple Seed Word
def method2():
	pass

### LEARNING MORE ABOUT WORDNET
synset = wordnet.synset('crime.n.01')
method1()