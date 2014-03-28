"""This module provides tools for interfacing with WordNet2.1

Vocabulary:

Synset - Basic unit of wordnet: a set of "synonyms" that collectively form the definiton of a concept
Hypernym - A hypernym of a synset is a more general word under which it falls (like a category)
Hyponym - A hyponym of a synset is a more specific word which falls under it
Lemma - A single morphological form for a synset
Derivationally Related Form - 
Topic Domain - Wordnet synsets can be domain 
Region Domain -
Usage Domain - 


Functions:

printhypernyms(synset, depth)
printhyponyms(synset)
printhyponymsrecursive(synset, level = 0)
printlemmas(synset)
printrelatedforms(synset)
printsynset(synset)

getnamepretty(synset)
gethypernyms(synset, depth)
gethypernymsrecursive(synset)
hypernymrecursionhelper(list_of_hypernyms)
getlemmas(synset
gettopicdomainterms(synset)
getregiondomainterms(synset)
getusagedomainterms(synset)
getdomainterms(synset)
gethyponyms(synset)
gethyponymsrecursive(synset)
getrelatedforms(synset)
getallthings(synset)
getallthingspretty(synset)

"""

from nltk.corpus import wordnet
from sets import Set

#example synset for testing
#print wordnet.synset('crime.n.01')

#PRINT FUNCTIONS
def printhypernyms(synset, depth):
    """Print hypernyms 'depth' levels up from synset input.

        Arguments:
        synset -- wordnet.synset
        depth -- how many levels up you want to print hypernyms
        
    """
    print synset.hypernyms()
    if depth !=1:
        printhypernyms(synset.hypernyms()[0], depth - 1)

def printhyponyms(synset):
    """Print synsets that are immediate hyponyms of synset input."""
    print synset.hyponyms()

def printhyponymsrecursive(synset, level = 0):
    """Print synsets that are hyponyms of synset input with spacing that depicts the heirchy.

        Arguments:
        synset -- wordnet.synset

        Keyword Arguments:
        level -- counts the depth of iteration for pretty printing(default 0)
        
    """
    hyponymlist = synset.hyponyms()
    #generate spacing string
    spacing = ''
    for i in range(level):
        spacing += ' '

    #recur and print hyponyms    
    for x in hyponymlist:
        print spacing + str(x)
        if len(x.hyponyms()) > 0:
            printhyponymsrecursive(x, level+1)

def printlemmas(synset):
    """Print lemmas for a synset."""
    for lemma in synset.lemmas:
        print lemma

def printrelatedforms(synset):
    """Print synsets that are derivationally related forms of synset."""
    for lemma in synset.lemmas:
        for item in lemma.derivationally_related_forms():
            print item

def getnamepretty(synset):
    """Print just the name of the synset."""
    return synset.name.split('.')[0]

def printsynset(synset):
    """Print synset, its definitions, examples, lemmas, immediate hypernyms, immediate hyponyms"""
    print synset
    print synset.definition
    print synset.examples
    print '\nlemmas'
    for lemma in synset.lemmas:
        print str(lemma) + '\t' + str(lemma.name) 

    print '\nhypernms'
    for hypernym in gethypernymsrecursive(synset):
        print hypernym
    print "---> " + str(synset)
          
    print '\nhyponyms'
    for hyponym in synset.hyponyms():
         print hyponym
    
    

#GET FUNCTIONS

def gethypernyms(synset, depth):
    """Return a list of synsets that are hypernyms to synset and 'depth' levels up in the heiarchy.

    Arguments:
    synset -- wordnet.synset
    depth -- how many levels up you want to print hypernyms 

    """
    #improvement to make ->
    #return a tree with all hypernyms
    #instead of just synset.hypernyms()[0]
    hypernymlist = synset.hypernyms()
    if depth !=1:
        for item in gethypernyms(synset.hypernyms()[0], depth - 1):
            hypernymlist.append(item)
    return hypernymlist

def gethypernymsrecursive(synset):
    """Return a list containing hypernyms of a synset."""
    return hypernymrecursionhelper(synset.hypernyms())
def hypernymrecursionhelper(list_of_hypernyms):
    all_hypernyms = []
    for synset in list_of_hypernyms:
        all_hypernyms += hypernymrecursionhelper(synset.hypernyms())
    return all_hypernyms  + list_of_hypernyms

def getlemmas(synset):
    """Return a list containing lemmas of a synset"""
    return synset.lemmas

def gettopicdomainterms(synset):
    """Return a list containing synsets in the same topic domain as synset"""
    return synset._related('-c')

def getregiondomainterms(synset):
    """Return a list containing synsets in the same region domain as synset"""
    return synset._related('-r')

def getusagedomainterms(synset):
    """Return a list containing synsets in the same usage domain as synset"""
    return synset._related('-u')

def getdomainterms(synset):
    """Return a list containing synsets in the same usage, region, and topic domains as synset"""
    return (gettopicdomainterms(synset) + getregiondomainterms(synset) + gettopicdomainterms(synset))

def gethyponyms(synset):
    """Return a list containing immediate hyponyms of synset."""
    return synset.hyponyms()
    
def gethyponymsrecursive(synset):
    """Return a list containing all hyponyms of synset, recursively defined."""
    hyponymlist = synset.hyponyms()
    for x in hyponymlist:
        for item in gethyponymsrecursive(x):
            hyponymlist.append(item)
    return hyponymlist

def getrelatedforms(synset):
    """Return a list of synsets containing derivationally related forms to synset"""
    relatedforms = []
    for lemma in synset.lemmas:
        for item in lemma.derivationally_related_forms():
            relatedforms.append(item.synset)
    return relatedforms

def getallthings(synset):
    """Return a list of synsets containing all hypernyms, lemmas, related forms, hyponyms, and domain terms of synset"""
    allthings =[synset]
    allthings = (allthings
                 + gethypernymsrecursive(synset)
                 + getlemmas(synset)
                 + getrelatedforms(synset)
                 + gethyponymsrecursive(synset)
                 + getdomainterms(synset))
    return allthings

def getallthingspretty(synset):
    """Return a list of names containing all hypernyms, lemmas, related forms, hyponyms, and domain terms of synset"""
    return map(getnamepretty, getallthings(synset))

