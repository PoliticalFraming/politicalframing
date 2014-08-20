import sys; sys.path.append("..")

from app.classifier import Classifier

from app.models.frame import Frame
from app.models.speech import Speech
from app.models.subgroup import Subgroup
from app.models.analysis import Analysis

from sklearn.cross_validation import cross_val_score
from numpy import array

topic = "immigration"

# Get speeches for a particular topic
print("Get speeches for topic '%s'" % topic)
speech_dicts = Speech.get(5000, 0, phrase=topic)['speeches']
speeches = map(lambda x: Speech(**x), speech_dicts)
speeches = filter(lambda x: x.speaker_party == 'D' or x.speaker_party == 'R', speeches)
print("Found %d speeches with a party." % len(speeches))

# Build Classifier
print("Create Classifier")
naive_bayes = Classifier()

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
data = naive_bayes.vectorizer.fit_transform(bunch.data) #.tocsr()#.toarray()
target = array(bunch.target)

# Run Cross Validation Checks
print "================== CROSS VALIDATION ========================="
print "F1 scores"
print cross_val_score(naive_bayes.classifier, data, target, scoring='f1', verbose=1) # f1 = weighted precision and recall (can weigh separately too)
print "Accuracy"
print cross_val_score(naive_bayes.classifier, data, target, scoring='accuracy', verbose=1)
print "Average precision"
print cross_val_score(naive_bayes.classifier, data, target, scoring='average_precision', verbose=1)
print "Precision"
print cross_val_score(naive_bayes.classifier, data, target, scoring='precision', verbose=1)
print "Recall"
print cross_val_score(naive_bayes.classifier, data, target, scoring='recall', verbose=1)
