import os, sys

root = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root + "/..")

from app.utils import update_progress

from app.classifier import Classifier

from app.models.frame import Frame
from app.models.speech import Speech
from app.models.subgroup import Subgroup
from app.models.analysis import Analysis

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.datasets.base import Bunch
from sklearn.cross_validation import cross_val_score

from sklearn.cross_validation import cross_val_score
from numpy import array

phrase = "immigration"

# Get speeches for a particular phrase
num_speeches = Speech.get(0, 0, phrase=phrase, speaker_party="*")['count']
print("Getting up to 5000 of %d speeches for speaking:%s AND speaker_party:*" % (num_speeches, phrase))

speeches = []
for i in range(0, 5): # first 5 pages
    curr_speech_dicts = Speech.get(start=1000*i, rows=1000, phrase=phrase, speaker_party="*")['speeches']
    curr_speech_objs = map(lambda x: Speech(**x), curr_speech_dicts)
    speeches = speeches + curr_speech_objs
    update_progress((i+1)/5.0)
print ""

speeches = filter(lambda x: x.speaker_party == 'D' or x.speaker_party == 'R', speeches)
print("Found %d %s speeches with a party." % (len(speeches), phrase) )

# Build Classifier
print("Create Classifier")
naive_bayes = MultinomialNB(alpha=1.0,fit_prior=True)
vectorizer = TfidfVectorizer(min_df=0.5) #, vocabulary=vocab)

# Build Targets
print("Build target vector and data vector from documents")
def party_fn(speech):
    if speech.speaker_party == 'D':
        return 1
    elif speech.speaker_party == 'R':
        return 0
    else:
        raise Exception("Speech must have party 'D' or 'R': " + str(speech.speech_id))
bunch = Classifier.bunch_with_targets(speeches=speeches, target_function=party_fn)
data = vectorizer.fit_transform(bunch.data) #.tocsr()#.toarray()
print data
target = array(bunch.target)


# Run Cross Validation Checks
print "================== CROSS VALIDATION ========================="
print "F1 scores"
print cross_val_score(naive_bayes, data, target, scoring='f1', verbose=1) # f1 = weighted precision and recall (can weigh separately too)
print "Accuracy"
print cross_val_score(naive_bayes, data, target, scoring='accuracy', verbose=1)
print "Average precision"
print cross_val_score(naive_bayes, data, target, scoring='average_precision', verbose=1)
print "Precision"
print cross_val_score(naive_bayes, data, target, scoring='precision', verbose=1)
print "Recall"
print cross_val_score(naive_bayes, data, target, scoring='recall', verbose=1)
