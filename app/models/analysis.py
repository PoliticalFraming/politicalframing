from __future__ import division 

from app import app, db, celery
from peewee import *
from collections import deque
import datetime

# from app.models.topic import Topic
from app.models.frame import Frame
from app.models.speech import Speech

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.datasets.base import Bunch

from dateutil import parser as dateparser

import inspect
import math

class Classifier:
    """Used to allow the adding and removing of speeches to the classifer.
    This could be made faster by actually modifying or extending the MultinomialNB 
    in scikit-learn rather than creating a new MultinomialNB object each time."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB(alpha=1.0,fit_prior=True)

    def learn_vocabulary(self, document):
        # self.vocabulary = vocabulary
        self.vectorizer.fit([document])
        print "learning vocabulary"
        # print self.vectorizer.vocabulary_

    def train_classifier(self, data, target):
        sparse_data = self.vectorizer.transform(data)
        print "training classifier"
        self.classifier.fit(sparse_data, target)
        # print self.vectorizer.vocabulary_

    def classify_document(self, document):
        print "Classifying document"
        tfidf_frames_vector = self.vectorizer.transform([document])
        # print self.vectorizer.vocabulary_

        thing = self.classifier.predict_log_proba(tfidf_frames_vector)[0]
        # print self.classifier.feature_log_prob_
        # print class_count_
        # print feature_count_

        return thing

class Analysis(db.Model):
    id = PrimaryKeyField(null=False, db_column='id', primary_key=True, unique=True)
    frame = ForeignKeyField(Frame, null=False)
    phrase = CharField(null=False)

    celery_id = CharField(null=True)
    to_update = BooleanField(null=True)
    start_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    states = TextField(null=True) #example: [MA, TX, CA]
    topic_plot = TextField(null=True)
    frame_plot = TextField(null=True)

    class Meta:
        db_table = 'analyses'

    @classmethod
    def compute_analysis(cls, phrase, frame, start_date=None, end_date=None, states=None, to_update=None):
        """
        Class Method:
        - Queries DB for speeches with parameters specified in args.
        - Computes an analysis
        - stores results of the analysis in an instance of the Analysis class.
        - returns ID of that instance
        """

        analysis_obj = Analysis(
            frame = Frame.get(Frame.id == frame), 
            phrase = phrase,
            start_date = start_date, 
            end_date = end_date, 
            states = states, 
            to_update = to_update
        )

        analysis_obj.save()

        # deal with states
        query = {'phrase': phrase, 'frame': frame, 'start_date': start_date, 'end_date': end_date, 'order': 'date' }

        result = Analysis.analyze_task.delay(analysis_obj, query)
        analysis_obj.celery_id = result.id
        analysis_obj.save()
        # celery.close()

        app.logger.debug("Computed Analysis %d for phrase=%s and frame=%d", analysis_obj.id, phrase, frame)

        print analysis_obj

        return analysis_obj

    ####################### CELERY TASK #######################

    @staticmethod
    @celery.task(bind=True)
    def analyze_task(self, analysis_obj, query):
        celery_id = self.request.id
        celery_obj = self
        phrase = query['phrase']
        frame = Frame.get(Frame.id == query['frame'])
        numFound = Speech.get(0, 0, **query)['count']
        speeches = []
        pages = int(math.ceil(numFound/1000))

        celery_obj.update_state(state='PROGRESS', meta={'current': 0, 'total': pages})

        for i in range(0, pages):
            speeches = speeches + Speech.get(start=1000*i, rows=1000, **query)['speeches']
            celery_obj.update_state(state='PROGRESS', meta={'stage': "fetch", 'current': i, 'total': pages})

        speeches = Analysis.preprocess_speeches(speeches, Analysis.party_fn)
        app.logger.debug(str(len(speeches)) + " speeches are being analyzed")
        analysis_obj.topic_plot = analysis_obj.plot_topic_usage(speeches, phrase, 100, celery_obj)
        analysis_obj.frame_plot = analysis_obj.plot_frame_usage(frame, speeches, 100, 100, phrase, celery_obj)

        indexes_to_delete = []
        for i, current_end_date in enumerate(analysis_obj.topic_plot['end_dates']):
            if current_end_date.year > 2013:
                indexes_to_delete.append(i)
        
        analysis_obj.topic_plot['end_dates'] = map(lambda x: x[1], filter(lambda (i,x) : i not in indexes_to_delete, 
            enumerate(analysis_obj.topic_plot['end_dates'])))

        analysis_obj.topic_plot['start_dates'] = map(lambda x: x[1], filter(lambda (i,x) : i not in indexes_to_delete, 
            enumerate(analysis_obj.topic_plot['start_dates'])))

        analysis_obj.topic_plot['dem_counts'] = map(lambda x: x[1], filter(lambda (i,x) : i not in indexes_to_delete, 
            enumerate(analysis_obj.topic_plot['dem_counts'])))

        analysis_obj.topic_plot['rep_counts'] = map(lambda x: x[1], filter(lambda (i,x) : i not in indexes_to_delete, 
            enumerate(analysis_obj.topic_plot['rep_counts'])))

        analysis_obj.frame_plot['end_dates'] = map(lambda x: x[1], filter(lambda (i,x) : i not in indexes_to_delete, 
            enumerate(analysis_obj.frame_plot['end_dates'])))

        analysis_obj.frame_plot['start_dates'] = map(lambda x: x[1], filter(lambda (i,x) : i not in indexes_to_delete, 
            enumerate(analysis_obj.frame_plot['start_dates'])))

        analysis_obj.frame_plot['ratios'] = map(lambda x: x[1], filter(lambda (i,x) : i not in indexes_to_delete, 
            enumerate(analysis_obj.frame_plot['ratios'])))

        analysis_obj.save()

        return self

    ####################### UTILITIES #######################

    @classmethod
    def party_fn(cls, speech):
        if speech['speaker_party']=="D" or speech['speaker_party']=="R":
            return True
        else:
            return False

    @classmethod
    def preprocess_speeches(cls, speeches, relevance_fn):
        '''Includes only speeches that the '''
        relevant = relevance_fn #plug in what is relevant

        valid_speeches=[]
        for speech in speeches:
            if relevant(speech):
                valid_speeches.append(speech)
        return valid_speeches

    def check_if_complete(self):
        if not self.celery_id: 
            return {'state':"No Celery Task", 'percent_complete':"n/a"}
        async_res = celery.AsyncResult(self.celery_id)
        if async_res: #.ready() == True:
            return {'state':async_res.state, 'percent_complete':async_res.info}
        return "why am i here?"
        

    ####################### LOGIC #######################

    def plot_topic_usage(self, ordered_speeches, phrase, n, celery_obj):
        """
        ordered_speeches - list of speech objects in date order
        phrase - string

        *** needs to be modified
        """
        app.logger.debug("plot_topic_usage")

        speeches = deque(ordered_speeches)
        dem_counts = []
        rep_counts = []
        start_dates = []
        end_dates = []

        first_speech_time = speeches[0]['date']
        last_speech_time = speeches[-1]['date']

        print "first_speech_time " + str(first_speech_time)
        print "last_speech_time " + str(last_speech_time)

        timedelta_total = last_speech_time - first_speech_time
        window_timedelta = timedelta_total // n

        window_start = first_speech_time
        window_end = first_speech_time + window_timedelta

        print "window_start " + str(window_start)
        print "window_end " + str(window_end)

        while speeches:
            #clear current window
            current_window  = []
            dem_count = 0
            rep_count = 0

            print  "speeches[0]['date'] " + str(speeches[0]['date'])
            print "speeches[-1]['date'] " + str(speeches[-1]['date'])

            print window_start
            print window_end

            #get speeches in current window
            while(speeches and (speeches[0]['date'] >= window_start) and (speeches[0]['date'] <= window_end)):
                current_window.append(speeches.popleft())

            #process speeches in current window
            for current_speech in current_window:
                if current_speech['speaker_party'] == "D":
                    dem_count +=1
                elif current_speech['speaker_party'] == "R":
                    rep_count +=1

            dem_counts.append(dem_count)
            rep_counts.append(rep_count)

            #move current window time
            start_dates.append(window_start)
            end_dates.append(window_end)

            window_start = window_start + window_timedelta
            window_end = window_start + window_timedelta

            if window_end > last_speech_time:
                window_end = last_speech_time   

        self.topic_plot = {
            'title': "Speeches about %s" % phrase,
            'ylabel': "Number of Speeches",
            'start_dates': start_dates, 
            'end_dates': end_dates,
            'dem_counts':dem_counts,
            'rep_counts':rep_counts
        }

        return self.topic_plot

    def build_training_set(self, speeches):
        '''This function is an alternative form of the loads in sklearn which loads 
        from a partiular file structure. This function allows me to load from a the database
        '''
        
        app.logger.debug('Building training set.')

        def target_function(speech):
            if speech['speaker_party'] == 'D':
                return 0
            elif speech['speaker_party'] == 'R':
                return 1
            else:
                print "Speech must be categorized as D or R : " + str(speech['speech_id'])

        target = [] #0 and 1 for D or R respectively  
        target_names = ['D','R'] #target_names
        data = [] #data

        for speech in speeches:  
            target.append(target_function(speech))
            speech_string = ''
            for sentence in speech['speaking']:
                speech_string += sentence
            data.append(speech_string)
        
        DESCR = "Trained D vs R classifier"

        #Bunch - https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/datasets/base.py
        return Bunch(
            target = target,
            target_names = target_names,
            data = data,
            DESCR = DESCR)
        
    def plot_frame_usage(self, frame, ordered_speeches, window_size, offset, phrase, celery_obj):
        """ 
        frame = frame object
        speeches = list of speech objects in date order
        n = number of data points to plot
        testing = True if accessing this method from unit tests

        returns json with dates that correlate to log_likelihoods to plot
        """

        speeches = deque(ordered_speeches)

        #setup current window
        current_window = []
        try:
            for _ in range(window_size):
                current_window.append(speeches.popleft())
        except:
            app.logger.error('window_size smaller than number of speeches! waaaaay to small')
            raise


        #declare return variables
        app.logger.debug("Create empty return variables")
        start_dates = []
        end_dates = []
        r_likelihoods = []
        d_likelihoods = []
        ratios = []

        #loop through and plot each point
        while speeches:
            celery_obj.update_state(state='PROGRESS', meta={'stage': 'analyze', 'current': len(speeches), 'total': len(ordered_speeches)})
            start_dates.append(current_window[0]['date'])
            end_dates.append(current_window[-1]['date'])

            #create_classifier
            app.logger.debug("Create Classifier")
            naive_bayes = Classifier()

            #Learn Vocabulary
            app.logger.debug("Learn Vocabulary")
            naive_bayes.learn_vocabulary(frame.word_string)

            #Build Training Set
            app.logger.debug("Building Training Set")
            training_set = self.build_training_set(current_window)

            #train classifier on speeches in current window
            app.logger.debug("Training Classifier")
            naive_bayes.train_classifier(training_set.data, training_set.target)

            #populate return data
            app.logger.debug("Request Log Probability of Frame %s " , frame.name)
            log_probabilities = naive_bayes.classify_document(frame.word_string)
            
            d_likelihoods.append(log_probabilities[0])
            r_likelihoods.append(log_probabilities[1])

            #move current window over by 'offset'
            app.logger.debug("Move window over by %d", offset)
            for _ in range(offset):
                if speeches:
                    current_window.append(speeches.popleft())
                    current_window = current_window[1:]

            # do something about the div by zero error
            ratios = map(lambda x,y: x/y, d_likelihoods, r_likelihoods)

            #stringify dates
            # start_dates = map(lambda x: utils.formatdate(time.mktime(x.timetuple())), start_dates)
            # end_dates = map(lambda x: utils.formatdate(time.mktime(x.timetuple())), end_dates)

        app.logger.debug("Populate Return Values")
        self.frame_plot = {
            'title': "Usage of %s Frame in Speeches about %s" % (frame.name, phrase),
            'ylabel': "D/R Ratio of Log-Likelihoods",
            'start_dates': start_dates,
            'end_dates': end_dates,
            'ratios': ratios
        }

        return self.frame_plot
