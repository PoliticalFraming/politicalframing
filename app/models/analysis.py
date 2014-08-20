from __future__ import division

from app import app, db, celery
from peewee import *
from collections import deque
import datetime

from app.classifier import Classifier

from app.models.frame import Frame
from app.models.speech import Speech
from app.models.subgroup import Subgroup

from dateutil import parser as dateparser

# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)

import inspect
import math
from celery.contrib import rdb

#Constants (Move creation to where speeches are ingested)
OLDEST_RECORD_DATE = datetime.datetime(1994,1,1)

class Analysis(db.Model):
    id = PrimaryKeyField(null=False, db_column='id', primary_key=True, unique=True)
    frame = ForeignKeyField(Frame, null=False)

    #Phrase Being Queried
    phrase = CharField(null=False)

    #Subgroups to compare
    subgroupA = ForeignKeyField(Subgroup, null=False, related_name='analysis_parent1')
    subgroupB = ForeignKeyField(Subgroup, null=False, related_name='analysis_parent2')

    celery_id = CharField(null=True)
    to_update = BooleanField(null=True) #mark to regularly update with latest information or not

    start_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)

    topic_plot = TextField(null=True)
    frame_plot = TextField(null=True)


    def build_query_params(self, order='date'):
        """
        Returns a dict of params for the solr query that will get all
        speeches related to this analysis.
        """

        return {
        'phrase': self.phrase,
        'frame': self.frame,
        'start_date': self.start_date.strftime("%Y-%m-%d"),
        'end_date': self.end_date.strftime("%Y-%m-%d"),
        'order': order}

    class Meta:
        db_table = 'analyses'

    @classmethod
    def compute_analysis(cls, phrase, frame, id=None, start_date=None, end_date=None,
        states_a=None, party_a=None, states_b=None, party_b=None, to_update=None):
        """
        Class Method:
        - Queries DB for speeches with parameters specified in args.
        - Computes an analysis
        - stores results of the analysis in an instance of the Analysis class.
        - returns ID of that instance
        """

        # If start or end date not set, set them
        start_date = dateparser.parse(start_date).date() if start_date else OLDEST_RECORD_DATE
        end_date = dateparser.parse(end_date).date() if end_date else datetime.datetime.now()

        if id != None:
            # Update existing Analysis Object with a new start_date and end_date
            analysis_obj = Analysis.get(Analysis.id == id)
            analysis_obj.start_date = start_date_isadate
            analysis_obj.end_date = end_date_isadate
        else:
            # Create new Analysis Object

            subgroup_a = Subgroup(
                states = states_a,
                party = party_a
            )

            subgroup_a.save()

            subgroup_b = Subgroup(
                states = states_b,
                party = party_b
            )

            subgroup_b.save()

            analysis_obj = Analysis(
                frame = Frame.get(Frame.id == frame),
                phrase = phrase,
                start_date = start_date,
                end_date = end_date,
                subgroupA = subgroup_a,
                subgroupB = subgroup_b,
                to_update = to_update
            )

        analysis_obj.save()

        result = Analysis.analyze_task.delay(analysis_obj)
        analysis_obj.celery_id = result.id
        analysis_obj.save()
        # celery.close()

        app.logger.debug("Computed Analysis %d for phrase=%s and frame=%d", analysis_obj.id, phrase, frame)

        print analysis_obj

        return analysis_obj

    ####################### CELERY TASK #######################

    @staticmethod
    @celery.task(bind=True)
    def analyze_task(self, analysis_obj):
        celery_id = self.request.id
        celery_obj = self
        phrase = analysis_obj.phrase

        query_params = analysis_obj.build_query_params(order='score')
        app.logger.debug(str(query_params))

        frame = Frame.get(Frame.id == analysis_obj.frame)
        # numFound = Speech.get(0, 0, **query_params)['count']
        speeches = []
        pages = 5 # int(math.ceil(numFound/1000))

        celery_obj.update_state(state='PROGRESS', meta={'current': 0, 'total': pages})

        # get speeches by page from api and convert to speech objects
        for i in range(0, pages):
            speech_dicts = Speech.get(start=1000*i, rows=1000, **query_params)['speeches']
            speeches = speeches + map(lambda x: Speech(**x), speech_dicts)
            update_progress((i+1)/pages)
            celery_obj.update_state(state='PROGRESS', meta={'stage': "fetch", 'current': i, 'total': pages})

        # order speeches by date

        app.logger.debug("started sorting")

        speeches = sorted(speeches, key=lambda speech: speech.date )

        app.logger.debug("ended sorting")

        app.logger.debug("first %s and last %s speech" % (str(speeches[0].date), str(speeches[-1].date)))

        speeches = Analysis.preprocess_speeches(speeches, analysis_obj.subgroup_fn)
        app.logger.debug(str(len(speeches)) + " speeches are being analyzed")
        analysis_obj.topic_plot = analysis_obj.plot_topic_usage(speeches, phrase, 100, celery_obj)
        analysis_obj.frame_plot = analysis_obj.plot_frame_usage(frame, speeches, 100, 100, phrase, celery_obj)

        indexes_to_delete = []
        for i, current_end_date in enumerate(analysis_obj.topic_plot['end_dates']):
            if current_end_date.year > 2013:
                indexes_to_delete.append(i)

        # this removes last bucket post analysis

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

        # when recomputing an analysis, this prevents the old celery_id from overwriting the new celery_id
        # this can be done less hackily later
        analysis_obj.celery_id = celery_id

        analysis_obj.save()

        return self

    ####################### UTILITIES #######################

    def subgroup_fn(self, speech):
        if speech.belongs_to(self.subgroupA) or speech.belongs_to(self.subgroupB):
            return True
        else:
            return False

    @classmethod
    def preprocess_speeches(cls, speeches, relevance_fn):
        '''Includes only speeches that pass the relevance_fn'''
        relevant = relevance_fn #plug in what is relevant

        valid_speeches=[]
        invalid_speeches = []
        for speech in speeches:
            if relevant(speech):
                valid_speeches.append(speech)
            else:
                invalid_speeches.append(speech)

        app.logger.debug("%d valid speeches, %d invalid speeches" % (len(valid_speeches), len(invalid_speeches)))

        return valid_speeches

    def check_if_complete(self):

        if self.topic_plot and self.frame_plot:
            return {'state':'SUCCESS', 'percent_complete': {"current": 100, "total": 100, "stage": "analyze"}}
        if not self.celery_id:
            return {'state':"No Celery Task", 'percent_complete':"n/a"}
        async_res = celery.AsyncResult(self.celery_id)
        if async_res: #.ready() == True:
            return {'state':async_res.state, 'percent_complete':async_res.info}
        # return "why am i here?"

    ####################### LOGIC #######################

    def plot_topic_usage(self, ordered_speeches, phrase, n, celery_obj):
        """
        ordered_speeches - list of speech objects in date order
        phrase - string
        n - # of buckets

        *** needs to be modified
        """
        app.logger.debug("plot_topic_usage")

        speeches = deque(ordered_speeches)
        subgroup_a_counts = []
        subgroup_b_counts = []
        start_dates = []
        end_dates = []

        first_speech_time = speeches[0].date
        last_speech_time = speeches[-1].date

        print "first_speech_time " + str(first_speech_time)
        print "last_speech_time " + str(last_speech_time)

        timedelta_total = last_speech_time - first_speech_time
        window_timedelta = timedelta_total // n

        window_start = first_speech_time
        window_end = first_speech_time + window_timedelta

        print "window_start " + str(window_start)
        print "window_end " + str(window_end)

        while speeches:
            # clear current window
            current_window  = []
            subgroup_a_count = 0
            subgroup_b_count = 0

            print  "speeches[0].date " + str(speeches[0].date)
            print "speeches[-1].date " + str(speeches[-1].date)

            print window_start
            print window_end

            # get speeches in current window
            while(speeches and (speeches[0].date >= window_start) and (speeches[0].date <= window_end)):
                current_window.append(speeches.popleft())

            # process speeches in current window
            for current_speech in current_window:
                if current_speech.belongs_to(self.subgroupA):
                    subgroup_a_count +=1
                elif current_speech.belongs_to(self.subgroupB):
                    subgroup_b_count +=1

            subgroup_a_counts.append(subgroup_a_count)
            subgroup_b_counts.append(subgroup_b_count)

            # move current window time
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
            'dem_counts':subgroup_a_counts,
            'rep_counts':subgroup_b_counts
            # TODO: Change these names to subgroup_a and subgroup_b counts
        }

        return self.topic_plot


    def plot_frame_usage(self, frame, ordered_speeches, window_size, offset, phrase, celery_obj):
        """
        frame = frame object
        speeches = list of speech objects in date order
        n = number of data points to plot
        testing = True if accessing this method from unit tests

        returns json with dates that correlate to log_likelihoods to plot
        """

        speeches = deque(ordered_speeches)

        # setup current window
        current_window = []
        try:
            for _ in range(window_size):
                current_window.append(speeches.popleft())
        except:
            app.logger.error('window_size smaller than number of speeches! waaaaay to small')
            raise


        # declare return variables
        app.logger.debug("Create empty return variables")
        start_dates = []
        end_dates = []

        subgroup_a_likelihoods = []
        subgroup_b_likelihoods = []
        ratios = []

        # loop through and plot each point
        while speeches:
            celery_obj.update_state(state='PROGRESS', meta={'stage': 'analyze', 'current': len(ordered_speeches) - len(speeches), 'total': len(ordered_speeches)})
            start_dates.append(current_window[0].date)
            end_dates.append(current_window[-1].date)

            # create_classifier
            app.logger.debug("Create Classifier")
            naive_bayes = Classifier(vocab=frame.word_string.split())

            # Learn Vocabulary
            app.logger.debug("Learn Vocabulary")
            naive_bayes.learn_vocabulary(map(lambda speech: " ".join(speech.speaking),current_window))

            # Build Training Set
            app.logger.debug("Building Training Set")
            def target_function(speech):
                if speech.belongs_to(self.subgroupA):
                    return 0
                elif speech.belongs_to(self.subgroupB):
                    return 1
                else:
                    raise Exception("Speech must belong to subgroup a or b: " + str(speech.speech_id))
            training_set = Classifier.bunch_with_targets(current_window, target_function)

            # train classifier on speeches in current window
            app.logger.debug("Training Classifier")
            naive_bayes.train_classifier(training_set.data, training_set.target)

            # populate return data
            app.logger.debug("Request Log Probability of Frame %s " , frame.name)
            log_probabilities = naive_bayes.classify_document(frame.word_string)

            subgroup_a_likelihoods.append(log_probabilities[0])
            subgroup_b_likelihoods.append(log_probabilities[1])

            # move current window over by 'offset'
            app.logger.debug("Move window over by %d", offset)
            for _ in range(offset):
                if speeches:
                    current_window.append(speeches.popleft())
                    current_window = current_window[1:]

            # do something about the div by zero error
            ratios = map(lambda x,y: x/y, subgroup_a_likelihoods, subgroup_b_likelihoods)

            # stringify dates
            # start_dates = map(lambda x: utils.formatdate(time.mktime(x.timetuple())), start_dates)
            # end_dates = map(lambda x: utils.formatdate(time.mktime(x.timetuple())), end_dates)

        celery_obj.update_state(state='PROGRESS', meta={'stage': 'analyze', 'current': len(ordered_speeches), 'total': len(ordered_speeches)})

        app.logger.debug("Populate Return Values")
        self.frame_plot = {
            'title': "Usage of %s Frame in Speeches about %s" % (frame.name, phrase),
            'ylabel': "a/b Ratio of Log-Likelihoods",
            'start_dates': start_dates,
            'end_dates': end_dates,
            'ratios': ratios
        }

        return self.frame_plot
