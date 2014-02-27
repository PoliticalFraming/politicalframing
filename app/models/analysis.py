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

import math

@celery.task(bind=True)
def analyze_task(self, analysis_obj, topic, frame, speeches):
    app.logger.debug(str(len(speeches)) + " speeches are being analyzed")
    analysis_obj.topic_plot = analysis_obj.plot_topic_usage(speeches, topic, 100)
    analysis_obj.frame_plot = analysis_obj.plot_frame_usage(frame, speeches, 100, 100, topic)
    analysis_obj.save()

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

    def train_classifier(self, data, target):
        sparse_data = self.vectorizer.transform(data)
        self.classifier.fit(sparse_data, target)

    def classify_document(self, document):
        tfidf_frames_vector = self.vectorizer.transform(document)
        return self.classifier.predict_log_proba(tfidf_frames_vector)[0]

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

        # deal with states
        query = {'phrase': phrase, 'frame': frame, 'start_date': start_date, 'end_date': end_date }

        numFound = Speech.get(0, 0, **query)['count']

        speeches = []
        for i in range(0, int(math.ceil(numFound/10000))):
            speeches = speeches + Speech.get(start=10000*i, rows=10000, **query)['speeches']

        speeches = Analysis.preprocess_speeches(speeches, Analysis.party_fn)

        frame = Frame.get(Frame.id == frame)
        analysis_obj = Analysis(
            frame = frame, 
            phrase = phrase,
            start_date = start_date, 
            end_date = end_date, 
            states = states, 
            to_update = to_update
        )
        analysis_obj.save()

        result = analyze_task.delay(analysis_obj, phrase, frame, speeches)
        analysis_obj.celery_id = result.id
        analysis_obj.save()
        # celery.close()

        app.logger.debug("Computed Analysis %d for phrase=%s and frame=%s", analysis_obj.id, phrase, frame.name)

        return analysis_obj

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

    def plot_topic_usage(self, ordered_speeches, phrase, n):
        """
        ordered_speeches - list of speech objects in date order
        phrase - string

        *** needs to be modified
        """
        app.logger.debug("plot_topic_usage")

        speeches = deque(ordered_speeches)
        dates = []
        dem_counts = []
        rep_counts = []

        while speeches:
            dem_count = 0
            rep_count = 0
            date_string = ""
            for i in range(n):
                try:
                    current_speech = speeches.popleft()
                    date_string = str(current_speech['date'])
                    if current_speech['speaker_party'] == "D":
                        dem_count +=1
                    elif current_speech['speaker_party'] == "R":
                        rep_count +=1
                except IndexError:
                    # @DhrumilMehta I think this is for the last bucket which won't have all 100 speeches??
                    pass

            if dem_count>0 and rep_count>0:
                #skips datapoints that don't have at least one speech in each category to avoid ZeroDivisionError
                dates.append(date_string)
                dem_counts.append(dem_count)
                rep_counts.append(rep_count)
            
        def get_ratio(x,y):
            try:
                return float(x)/float(y)
            except:
                raise #if it gets here, something is really wrong (ZeroDivisionError)

        ratios = map(lambda x,y: get_ratio(x,y), dem_counts, rep_counts)

        self.topic_plot = {
            'title': "Speeches about %s" % phrase,
            'ylabel': "Number of Speeches",
            'dates': dates, 
            'ratios':ratios,
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
        
    def plot_frame_usage(self, frame, ordered_speeches, window_size, offset, topic, testing=False):
        """ 
        frame = frame object
        speeches = list of speech objects in date order
        n = number of data points to plot
        testing = True if accessing this method from unit tests

        returns json with dates that correlate to log_likelihoods to plot
        """

        app.logger.debug('entering plot discrete average')

        speeches = deque(ordered_speeches)

        #setup current window
        current_window = []
        try:
            for _ in range(window_size):
                current_window.append(speeches.popleft())
        except:
            app.logger.error('window_size smaller than number of speeches! waaaaay to small')
            raise

        #create_classifier
        naive_bayes = Classifier()
        naive_bayes.learn_vocabulary(frame.word_string)

        #declare return variables
        start_dates = []
        end_dates = []
        r_likelihoods = []
        d_likelihoods = []
        ratios = []

        #loop through and plot each point
        while speeches:

            if not testing: #Don't update state if accessing from unit tests (there is no self)
                self.update_state(state='PROGRESS', 
                    meta={'current': len(speeches), 
                    'total': len(ordered_speeches)})
                
            start_dates.append(current_window[0]['date'])
            end_dates.append(current_window[-1]['date'])

            training_set = self.build_training_set(current_window)

            #train classifier on speeches in current window
            naive_bayes.train_classifier(training_set.data, training_set.target)

            #populate return data
            log_probabilities = naive_bayes.classify_document(frame.word_string)
            d_likelihoods.append(log_probabilities[0])
            r_likelihoods.append(log_probabilities[1])

            #move current window over by 'offset'
            for _ in range(offset):
                if speeches:
                    current_window.append(speeches.popleft())
                    current_window = current_window[1:]

            # do something about the div by zero error
            ratios = map(lambda x,y: x/y, d_likelihoods, r_likelihoods)

            #stringify dates
            start_dates = map(lambda x: str(x), start_dates)
            end_dates = map(lambda x: str(x), end_dates)

        self.frame_plot = {
            'title': "Usage of %s Frame in Speeches about %s" % (frame.name, topic),
            'ylabel': "D/R Ratio of Log-Likelihoods",
            'start_dates': start_dates,
            'end_dates': end_dates,
            'ratios': ratios
        }

        return self.frame_plot
