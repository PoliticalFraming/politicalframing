from nltk.corpus import wordnet
from sets import Set
import framemaker
import preprocessor

## HOLY CRAP WEIGHTED FRAMES !!!

#crime = wordnet.synset('crime.n.01')

def frameextension(synset):
    extension = []
    for hyponym in framemaker.gethyponymsrecursive(synset):
        for word in preprocessor.removestops(myutilities.removepunctuation(hyponym.definition)).split():
            extension.append(word)
    return extension

#print set(frameextension(crime))
