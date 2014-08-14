"""
This file contains code that tests the packages in lib folder.
"""

# How frames are currently made:
# ==============================
# * User enters a seed word
#		ex. 'crime'
# * Program finds all wordnet 'synsets' related to that word and ask the user if each is relevant
#		ex. 'crime.n.01'
# * For each relevant synset, program gets a list of synsets containing derivationally related forms to synset
# 		ex. [Synset('accuse.v.01'), Synset('transgress.v.01'), Synset('criminal.s.03'), Synset('outlaw.v.01'), Synset('incriminate.v.01')]

from framemaker import *
