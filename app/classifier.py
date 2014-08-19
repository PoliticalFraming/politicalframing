# -*- coding: utf-8 -*-

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.datasets.base import Bunch
from sklearn.cross_validation import cross_val_score

class Classifier:
    """Used to allow the adding and removing of speeches to the classifer.
    This could be made faster by actually modifying or extending the MultinomialNB
    in scikit-learn rather than creating a new MultinomialNB object each time."""

    def __init__(self, vocab=None):
        if vocab:
            self.vectorizer = TfidfVectorizer(min_df=0.5)
        else:
            self.vectorizer = TfidfVectorizer(min_df=0.5, vocabulary=vocab)
        self.classifier = MultinomialNB(alpha=1.0,fit_prior=False)

    def learn_vocabulary(self, documents):
        print "learning vocabulary"
        try:
            self.vectorizer.fit(documents)
        except ValueError as e:
            app.logger.debug(e)
            app.logger.debug(documents)
            raise

    def train_classifier(self, data, target):
        sparse_data = self.vectorizer.fit_transform(data)
        print "training classifier"
        self.classifier.fit(sparse_data, target)

    def classify_document(self, document):
        print "Classifying document"
        tfidf_frames_vector = self.vectorizer.transform([document])
        return self.classifier.predict_log_proba(tfidf_frames_vector)[0]

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
