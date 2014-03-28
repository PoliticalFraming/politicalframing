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

def makeframe(frameword):
    """Returns a frame (Set of synsets) based on frame word and user input to shell.
        See module docstring for more info.

        Arguments:
        frameword - a single word string

        Note:
        To best understand the functionality of this module, build a frame about 'love'
        and you can see its different senses very clearly.
        
    """

    framewordsynsets = wordnet.synsets(frameword) #synsets of frameword
    frame = Set() # words to include in frame
    parsedsynsets = Set() #keep track of parsed synsets so you don't ask about the same one twice

    
    for synset in framewordsynsets: #loop through each possible meaning of a word
        if not (synset in parsedsynsets):
            parsedsynsets.add(synset) #mark synset as "parsed"
            
            # Ask user if the synset is relevant to the frame they want to build
            print '\nDoes this fit the frame you have in mind?: '
            print str(synset) + '   ' + synset.definition
            print synset.examples

   
            #I have chosen not to ask the user about each realted form as they are
            #synonyms and it becomes cumbersome, but chose to display these anyways
            #to clarify the meaning that 'synset' conveys. 
            for rsynset in wordnettools.getrelatedforms(synset): 
                if not(rsynset in parsedsynsets):
                    print '\t' + str(rsynset) + '   ' + rsynset.definition
                    print '\t' + str(rsynset.examples)
                    parsedsynsets.add(rsynset) #mark as "parsed" 

            #Request user to accept or reject frame
            userin = raw_input('y or n: ')
            
            if userin.lower() == 'y':
                #include one hypernym, all lemmas, all related forms, all hyponyms, and all domain terms of synset
                #see implementation of "all-things" in wordnettools
                for subsynset in (wordnettools.gethypernymsrecursive(synset)
                             + wordnettools.getlemmas(synset)
                             + wordnettools.getrelatedforms(synset)
                             + wordnettools.gethyponymsrecursive(synset)
                             + wordnettools.getdomainterms(synset)):
                    frame.add(wordnettools.getnamepretty(subsynset))
                                    
            elif userin.lower() == 'n':
                print str(synset.name) + ' not included'
            else:
                print 'Error - only y or n are valid responses'
    

    return frame

def pickleframe(word):
    """Make and pickle a frame about 'word', dump it in 'word.txt'."""
    fname = word + '.txt'
    f = open(fname, 'w')
    pickle.dump(makeframe(word),f)
    f.close()

def picklemultiframe(framewords,word):
    """Make and pickle a frame about multiple framewords, dump it in 'word.txt'.

        Arguments:
        word - name of the file and overall name of the frame
        framewords - list of words which will collectively make up the frame

    """
    fname = '1' + word + '.txt'
    f = open(fname, 'w')
    pickle.dump(multimakeframe(framewords,word),f)
    f.close()

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


