# -*- coding: utf-8 -*-

from app import app

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.datasets.base import Bunch
from sklearn.cross_validation import cross_val_score

#
# We expected the graph to remain consistent after passing in
# a vocabulary to the TfidfVectorizer (thus casuing it to have a
# "fixed_vocabulary"). It was definitely not consistent and seemed
# to be much smoother. This may be because each window does not
# have all of the frame's words. By setting the vocabulary to the
# words of the frame we are going to get several words with 0 probability.
# This makes use of the laplace or lidstorm smoothing thus casuing smoother
# graphs. It might make more sense to just not pass in the frame words
# that don't exist in the current window; however, inconsitent frames
# across windows (and inconsistent frame lengths) can cause further
# complications.
#

class Classifier:
    """Used to allow the adding and removing of speeches to the classifer.
    This could be made faster by actually modifying or extending the MultinomialNB
    in scikit-learn rather than creating a new MultinomialNB object each time."""

    def __init__(self, vocab=None):
        self.vectorizer = TfidfVectorizer(min_df=2, vocabulary=vocab)
        self.classifier = MultinomialNB(alpha=0.1,fit_prior=True)

    def train_classifier(self, data, target):
        sparse_data = self.vectorizer.fit_transform(data)
        app.logger.debug("training classifier")
        self.classifier.fit(sparse_data, target)

    def classify_document(self, document):
        app.logger.debug("classifying document")
        tfidf_frames_vector = self.vectorizer.transform([document])
        return self.classifier.predict_proba(tfidf_frames_vector)[0]

    def cross_validation(self, documents, targets):
        """
        Instantiate a new classifier and run this function.
        Do not run train_classifier
        """
        # documentation
        # sklearn.cross_validation.cross_val_score(estimator, X, y=None, scoring=None,
        #   cv=None, n_jobs=1, verbose=0, fit_params=None, score_func=None, pre_dispatch='2*n_jobs')¶
        X = self.vectorizer.fit(documents)
        y = targets
        return cross_val_score(self.classifier, X, y, cv=5)

    @staticmethod
    def bunch_with_targets (speeches, target_function):
        '''This function is an alternative form of the loads in sklearn which loads
        from a partiular file structure. This function allows me to load from the database
        '''

        app.logger.debug('Building bunch containing data and target vector.')

        target = [] # 0 and 1 for subgroup a and b respectively
        target_names = ['a','b'] # target_names
        data = [] # data

        for speech in speeches:
            target.append(target_function(speech))
            speech_string = ''
            for sentence in speech.speaking:
                speech_string += sentence
            data.append(speech_string)

        DESCR = "Trained subgroup_a vs subgroup_b classifier"

        # Bunch - https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/datasets/base.py
        return Bunch(
            target = target,
            target_names = target_names,
            data = data,
            DESCR = DESCR
        )
