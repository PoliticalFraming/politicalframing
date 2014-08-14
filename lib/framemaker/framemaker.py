"""This module allows the user to build frames from the python shell.

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
import frameextender
import pickle

def getSynset(synset):
    return wordnet.synset(synset)

def getSynsets(word):
    """Returns synsets for a particular word."""
    return wordnet.synsets(word)

def getWords(synset):
    """Returns all framing words associated with the synset."""

    words = set() # words to include in frame

    for subsynset in (wordnettools.gethypernymsrecursive(synset)
        + wordnettools.getlemmasgetrelatedforms(synset)(synset)
        + wordnettools.getrelatedforms(synset)
        + wordnettools.gethyponymsrecursive(synset)
        + wordnettools.getdomainterms(synset)):
         words.add(wordnettools.getnamepretty(subsynset))

    return list(words) # return list

def getSynsetMetadata(synset):
    """Returns metadata related to a synset."""
    return {"related_synsets": wordnettools.getrelatedforms(synset),
            "definition": synset.definition,
            "examples": synset.examples,
            "name": synset.name}

####################### OLD FILE STARTS HERE ##############################

def picksynsets(synsets):
    """Returns the subset of synsets that the user selects."""

    parsedsynsets = set([])
    selected_synsets = set([])
    for synset in synsets:
        if not (synset in parsedsynsets):
            parsedsynsets.add(synset) #mark synset as "parsed"

            # Ask user if the synset is relevant to the frame they want to build
            print '\nDoes this fit the frame you have in mind?: '
            print str(synset) + '   ' + synset.definition
            print synset.examples

            # I have chosen not to ask the user about each realted form as they are
            # synonyms and it becomes cumbersome, but chose to display these anyways
            # to clarify the meaning that 'synset' conveys.
            for related_synset in wordnettools.getrelatedforms(synset):
                if not(related_synset in parsedsynsets):
                    print '\t' + str(related_synset) + '   ' + related_synset.definition
                    print '\t' + str(related_synset.examples)
                    parsedsynsets.add(related_synset) #mark as "parsed"

            #Request user to accept or reject synset
            userin = raw_input('y or n: ')
            if userin.lower() == 'y':
                selected_synsets.add(synset)
            elif userin.lower() == 'n':
                print str(synset.name) + ' not included'
            else:
                print 'Error - only y or n are valid responses'

    return selected_synsets

def makeframe(frameword):
    """Returns a frame (Set of synsets) based on frame word and user input to shell.
        See module docstring for more info.

        Arguments:
        frameword - a single word string

        Note:
        To best understand the functionality of this module, build a frame about 'love'
        and you can see its different senses very clearly.

    """

    synsets = getSynsets(frameword)
    selected_synsets = picksynsets(synsets)
    return reduce(lambda x,y: x.union(y), map(lambda s: set(getWords(s)), selected_synsets))

def pickleframe(word):
    """Make and pickle a frame about 'word', dump it in 'word.txt'."""
    fname = word + '.txt'
    f = open(fname, 'w')
    pickle.dump(makeframe(word),f)
    f.close()

# def picklemultiframe(framewords,word):
#     """Make and pickle a frame about multiple framewords, dump it in 'word.txt'.

#         Arguments:
#         word - name of the file and overall name of the frame
#         framewords - list of words which will collectively make up the frame

#     """
#     fname = '1' + word + '.txt'
#     f = open(fname, 'w')
#     pickle.dump(multimakeframe(framewords,word),f)
#     f.close()

def addset2pickledframe(frame, myset):
    """Add a set of synsets to an existing pickled frame and save in a .txt file.

        Arguments:
        frame - a pickled frame (Set of synsets)
        myset - set of synsets to add to the existing frame
    """
    fname = frame + '.txt'
    newset = pickle.load(frame).union(myset)
    f = open(fname, 'w')
    pickle.dump(newset,f)
    f.close()
    return newset

def load(word):
    """Load a frame from 'word.txt' and return it."""
    fname = word + '.txt'
    f = open(fname, 'r')
    p = pickle.load(f)
    f.close()
    return p


