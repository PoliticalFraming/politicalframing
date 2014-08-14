"""This module provides tools pre-processing words or longer strings (texts).
This includes removing grammar, removing stopwords, and stemming with a
Lancaster Stemmer provided in the NLTK for python.

Vocabulary:
stemming - stemming a word means removing the prefixes and suffixes and trying to get at the root of a word
Lancaster Stemmer - a rather strong stemmer that seems to work well for our purposes

Functions:
isastopword(word)
stem(word)
preprocess_word(word)
removepunctuation(text)
removestops(text)
preprocess_text(text)

"""
# NOTE
#   I will use stemming in version 0.0 of this project, if results are intuitive,
#   I will instead take the approach of expanding a frame to include all conjugations
#   of the words in it. This will work because frames are normalized by size in analyisis.

from sets import Set
import string
import os

# LOADING STOPWORDS
#   stopwords is a set containing raw stopwords without any pre-processing.
#   this means it may contain words with apostrophes or hyphens
stopwords = Set()

PACKAGEROOT = os.path.dirname(os.path.abspath(__file__))
stopwordsfiles = [
open(PACKAGEROOT + '/data/stopwords/stopwords1.txt', 'r'),
open(PACKAGEROOT + '/data/stopwords/stopwords2.txt', 'r'),
open(PACKAGEROOT + '/data/stopwords/stopwords3.txt', 'r'),
open(PACKAGEROOT + '/data/stopwords/stopwords4.txt', 'r'),
open(PACKAGEROOT + '/data/stopwords/stopwords5.txt', 'r')]

for f in stopwordsfiles:
    for word in f.readlines():
        stopwords.add(word.replace("\n", ""))
    f.close()

# PREPROCESSING TOOLS
from nltk.stem.lancaster import LancasterStemmer

# tools for preprocessing single words
def isastopword(word):
    """If the word is a stopword return True, otherwise return False."""
    return word in stopwords

def stem(word):
    """Return the stemmed word using a Lancaster Stemmer."""
    st = LancasterStemmer()
    return st.stem(word)

def preprocess_word(word):
    """Return the word preprocessed with the following:
        spaces removed
        lower-cased
        punctuation removed except for apostrophes
        stemmed if not a stopword, empty string returned otherwise

    """
    word = word.replace(' ','')
    word = word.lower()
    word = removepunctuation(word)
    if isastopword(word):
        return ''
    else:
        return stem(word)


# tools for preprocessing texts

def removepunctuation(text):
    """Removes punctuation from a text. Does not remove apostrophes."""
    return text.translate(string.maketrans("",""), string.punctuation.replace('\'',''))

def removestops(text):
    """Removes stop-words from a text, as well as all punctuation except for apostrophes."""
    newtext = ''
    for word in text.split():
        if not isastopword(removepunctuation(word)):
            newtext = newtext + removepunctuation(word) + ' '
    return newtext.strip()

def preprocess_text(text):
    """Preprocess the text by taking each space deliniated token and doing the following:
        spaces removed
        lower-cased
        punctuation removed except for apostrophes
        stemmed if not a stopword, empty string returned otherwise

    """
    newtext = ''
    for word in text.split():
        if preprocess_word(word) != '':
            newtext += preprocess_word(word) + ' '
    return newtext.strip()


