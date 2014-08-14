from nltk.corpus import wordnet
from sets import Set
import framemaker
from preprocessor import removestops, removepunctuation
from wordnettools import gethyponymsrecursive

## HOLY CRAP WEIGHTED FRAMES !!!

def frameextension(synset):
    extension = []
    for hyponym in gethyponymsrecursive(synset):
        for word in removestops(removepunctuation(hyponym.definition)).split():
            extension.append(word)
    return set(extension)

if __name__ == "__main__":
    crime = wordnet.synset('crime.n.01')
    print frameextension(crime)
