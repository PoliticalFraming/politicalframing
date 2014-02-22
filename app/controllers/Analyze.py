# Given:
#     - a set of speeches about a particular topic
#     - categories to observe / compare
#     - a frame 
#
# Find: 
#     - the log-likelihood of the frame being classified in each of the categories

### *** Note : The long term goal of this set of functions needs to be to faciliate
###            good analysis for the journalists. This means the data should be displayed 
###            in a meaningful way. Brainstorm what ways that might be and write functions 
###            that do that rather than simply classify into democrat/republican.


### Brainstorming
#
#   - right now it can compare 2 values and output them in a graph
#   - the next step is to compare multiple values and output them in a format non-relative to each other, but relative in time :
#     this may involve raw counts of frame words

import json
import os 
from app.findFrames import return_framing_data
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

# from pylab import *#plot, hold, pi, linspace, sin, cos, legend, show, title, xlabel, ylabel
import sklearn
from sklearn.datasets.base import Bunch

import datetime
from bintrees import BinaryTree

from app import app, celery
from flask import request, session, jsonify
from peewee import *
from app.models.Frame import Frame, get_frame
from app.models.Topic import Topic
from app.models.Speech import Speech, get_speeches_in_date_order

# from app.controllers.Speech import SpeechResource
from collections import deque
from flask_peewee.rest import RestAPI, RestResource
import math
import pickle
from celery import Celery

@celery.task(bind=True)
def analyze_task(self,topic_id, states, start_date, end_date, frame_id):
    speeches = get_speeches_in_date_order(topic_id, states, start_date, end_date)
    frame = Frame.get(Frame.frame_id == frame_id)
    topic = Topic.get(Topic.topic_id == topic_id)
    speeches = preprocess_speeches(speeches)
    print str(len(speeches)) + " speeches are being analyzed"

    # topic_plot = plot_topic_usage(speeches, topic, 100)
    topic_plot = plot_moivng_topic_usage(speeches, topic, 100)
    frame_plot = plot_discrete_average(self, frame, speeches, 100, topic.phrase)

    return pickle.dumps({'frame_plot':frame_plot,'topic_plot':topic_plot})
    # return str(jsonify(topic_plot=topic_plot, frame_plot=frame_plot))

def preprocess_speeches(speeches):
    '''removes speeches without party'''
    valid_speeches=[]
    for speech in speeches:
        if speech.speaker_party=="D" or speech.speaker_party=="R":
            valid_speeches.append(speech)
    return valid_speeches

def plot_topic_usage(speeches, topic, n):

    def date_compare(self, other):
        '''override compare to sort by date'''
        return self.date.toordinal() - other.date.toordinal()

    speeches = deque(sorted(speeches, cmp=date_compare))

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
                date_string = str(current_speech.date)
                if current_speech.speaker_party == "D":
                    dem_count +=1
                elif current_speech.speaker_party == "R":
                    rep_count +=1
            except:
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

    return {
    'title': "Ratio of Speeches about %s (%d speeches per bin)" % (topic.phrase, n),
    'ylabel': "D/R Ratio",
    'dates': dates, 
    'ratios':ratios,
    'dem_counts':dem_counts,
    'rep_counts':rep_counts}

def valid_speechset(speechset):
    """A valid speechset has at least one democrat and one republican speech"""
    dem_speech_exists = False
    rep_speech_exists = False

    for speech in speechset:
        if speech.speaker_party == 'D':
            dem_speech_exists = True
        if speech.speaker_party == 'R':
            rep_speech_exists = True
        if dem_speech_exists and rep_speech_exists:
            return True

    return False

def plot_moving_topic_usage(speeches, topic, n):

    print "plotting moving topic counts"
    # window_size=n

    start_dates = []
    end_dates = []
    dem_counts = []
    rep_counts = []
    total_counts = []

    window_first_date = speeches[0].date
    OFFSET = datetime.timedelta(days=90)
    window_last_date = window_first_date + OFFSET

    current_first_speech_index = 0
    while(window_last_date <= speeches[-1].date):#date of the last item
        dem_count=0
        rep_count=0
        current_speech_index = current_first_speech_index
        for speech in speeches[current_first_speech_index:]:
            current_speech_index +=1
            if speech.date >= window_first_date and speech.date <= window_last_date:
                if speech.speaker_party == "D":
                        dem_count +=1
                elif speech.speaker_party == "R":
                    rep_count +=1
            else:
                #redefine date window to start with this speech
                window_first_date = speech.date
                window_last_date = window_first_date + OFFSET
                current_first_speech_index = current_speech_index
                break

        start_dates.append(str(window_first_date))
        end_dates.append(str(window_last_date))
        dem_counts.append(dem_count)
        rep_counts.append(rep_count)
        total_counts.append(rep_count+dem_count)

 
    return {
    'title': "Number of Speeches about %s" % (topic.phrase),
    'ylabel': "Speeches Found",
    'start_dates': start_dates, 
    'end_dates': end_dates,
    'dem_counts':dem_counts,
    'rep_counts':rep_counts,
    'total_counts':total_counts}

def order_by_frame_prevalance(speeches, frame):
    """ Orders speehes by frame prevelance. """

    speech_prevalances = [] #array of tuples containing speeches and ther prevalance values
    for speech in speeches:
        framewords_count = 0
        for word in frame.word_string.split():
            if word in speech.speaking:
                framewords_count += 1
        
        # adjust count for speech length
        frame_prevalance = framewords_count / len(speech.speaking.split())

        speech_prevalances.append((speech, frame_prevalance))

    return map(lambda x:x[0] , sorted(speech_prevalances, key=lambda x: x[1]))




    # ################################################################
    # # Better Implementaiton Stub - if simple counts don't work well
    # ################################################################
    #for speech in speeches:
    #     frame_words = {} #dict containing word:count_in_speech
    #     for word in frame.word_string.split():
    #         if word in speech.speaking:
    #             frame_words[word] = frame_words.get(word,0) + 1
    #     # do better ordering using frame_words dictionary 
    #     # (maybe something like tf/idf based counts) 
    # ################################################################

@app.route('/analyze')
def analyze():
    # get topic as URL get parameter
    topic_id = request.args.get('topic')
    states = request.args.get('speaker_state')
    if states: states = states.split(',')
    # # party = request.args.get('speaker_party')
    start_date = request.args.get('start_date')

    end_date = request.args.get('end_date')
    frame_id = request.args.get('frame')

    result = analyze_task.delay(topic_id, states, start_date, end_date, frame_id)
    celery.close()
    return result.id

@app.route('/analyze/datapoint')
def show_datapoint():
    #Parse URL parameters
    topic_id = request.args.get('topic')
    states = request.args.get('speaker_state')
    if states: states = states.split(',')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    frame_id = request.args.get('frame')

    #Get speeches and Frame
    speeches = get_speeches_in_date_order(topic_id, states, start_date, end_date)
    frame = get_frame(frame_id)
    
    #more data about the speeches
    num_democrat = 0
    num_republican = 0
    for speech in speeches:
        if speech.speaker_party.lower() == 'd':
            num_democrat +=1
        elif speech.speaker_party.lower() == 'r':
            num_republican +=1

    return jsonify(speeches=order_by_frame_prevalance(speeches, frame),
        start_date = start_date,
        end_date = end_date,
        num_speeches = len(speeches),
        democrat_speeches = num_democrat,
        republican_speeches = num_republican)

    
@app.route('/check')
def check_if_complete():
    task_id = request.args.get('task_id')

    if task_id:
        async_res = celery.AsyncResult(task_id)
        if async_res.ready() == True:
            print 'yay'
            result = pickle.loads(async_res.get())
            topic_plot=result['topic_plot']
            frame_plot=result['frame_plot']
            return jsonify(state=async_res.state, meta=async_res.info, topic_plot=topic_plot, frame_plot=frame_plot)
        else:
            print 'nay'
            return jsonify(state=async_res.state, meta=async_res.info)

@app.route('/analyze2')
def analyze2():
    
    # get topic as URL get parameterTraining set.

    topic_id = request.args.get('topic')
    states = request.args.get('speaker_state')
    if states: states = states.split(',')
    # # party = request.args.get('speaker_party')
    start_date = request.args.get('start_date')

    end_date = request.args.get('end_date')
    frame_id = request.args.get('frame')

    speeches = get_speeches_in_date_order(topic_id, states, start_date, end_date)
    # get list of json objects from the database (query by topic - or also filter by some other subset of factors)
    frame = Frame.get(Frame.frame_id == frame_id)
    topic = Topic.get(Topic.topic_id == topic_id)

    # speeches = get_speeches(topic)
    speeches = preprocess_speeches(speeches)

    topic_plot = plot_topic_usage(speeches, topic, 100)
    frame_plot = plot_moving_average(frame,speeches, 100)
    return jsonify(topic_plot=topic_plot, frame_plot=frame_plot)


def build_btree(speeches):
    """Build Binary Tree - Oranize Speeches by Date"""
    speech_tree = BinaryTree() #binary tree whose values are ID/Date tuples and is aranged by date
    # build a binary tree of file numbers arranged by (date,file_number) tuple
    for speech in speeches:
        date_id_key = speech.date, speech.speech_id #unique for each file, allows sort by date order
        speech_tree.insert(date_id_key, speech)  
    return speech_tree
    # find the earliest and latest date in the folder
    # min_speech_date = speech_tree.min_item()
    # max_speech_date = speech_tree.max_item()

def build_training_set(speeches):
    '''This function is an alternative form of the loads in sklearn which loads 
    from a partiular file structure. This function allows me to load from a the database'''
    
    print 'building training set'
    bunch = Bunch() #sklearn data structure - https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/datasets/base.py
    
    def target_function(speech):
        #/home/dhrumil/Desktop/PoliticalFraming/data/immigration/D/123.json
        if speech.speaker_party == 'D':
            return 0
        elif speech.speaker_party == 'R':
            return 1
        else:
            print "Speech must be categorized as D or R : " + str(speech.speech_id)

    bunch['target'] = [] #1 or 0 for D or R    
    bunch['target_names'] = ['D','R'] #target_names
    bunch['data'] = [] #data

    for speech in speeches:  
        bunch['target'].append(target_function(speech))
        speech_string = ''
        for sentence in speech.speaking:
            speech_string += sentence    
        bunch['data'].append(speech_string)
    
    bunch['DESCR'] = "Trained D vs R classifier" #DESCR
    
    return bunch    

def return_framing_datum(training_set, frame):
    '''This is hacky- fix it later'''

    frames = [frame.word_string];

    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(training_set.data)
    
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    
    clf = MultinomialNB(alpha=1.0,fit_prior=False).fit(X_train_tfidf,training_set.target)
    
    X_new_counts = count_vect.transform(frames)
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)
    predicted_logs = clf.predict_log_proba(X_new_tfidf)
    print predicted_logs
    return predicted_logs[0]


def plot_discrete_average(self,frame, speeches, n, topic, testing=False):
    """ 
    frame = frame object
    speech = list of speech objects
    n = number of data points to plot
    testing = True if accessing this method from unit tests

    returns json with dates that correlate to log_likelihoods to plot
    """

    app.logger.debug('entering plot discrete average')
    
    b = build_btree(speeches)
    number_of_datapoints = 0
    dates = []
    r_likelihoods = []
    d_likelihoods = []

    #Generate data for discrete buckets of n speeches
    count = 0
    while not b.is_empty():
        ordered_speeches = []
        count = count + 1
        #Run clasifier for n items at a time
        # n=100
        dates.append(max(b.nsmallest(n, pop = False))[0][0])
        for item in b.nsmallest(n,pop=True):
            ordered_speeches.append(item[1])
        # print 'ordered_speeches is ' + str(map(lambda x: x.date, ordered_speeches)) #works fine
        # print "ordered_speeches is " + str(len(ordered_speeches)) + " items long"
        
        if valid_speechset(ordered_speeches):
            try:
                training_set = build_training_set(ordered_speeches)
                #log_likelihoods        
                log_likelihoods = return_framing_datum(training_set, frame)    
                d_likelihoods.append(log_likelihoods[0])
                r_likelihoods.append(log_likelihoods[1])
                num_of_trainigsets = int(math.ceil(len(speeches)/float(n)))
                print "processed training set " + str(count) + " of " + str(num_of_trainigsets)
                

                if not testing: #Don't update state if accessing from unit tests (there is no self)
                    self.update_state(state='PROGRESS', meta={'current': count, 'total': num_of_trainigsets})

                
            except ValueError as e:
                print "Could not build training set " + str(count) + " of " + str(int(math.ceil(len(speeches)/float(n))))
                print e

            number_of_datapoints = number_of_datapoints + 1

            if b.is_empty(): #to fix  error where it tries to build an extra training set with no data
                break

        # print log_likelihoods[0]
        # print ""
        # print log_likelihoods[1]
        # print "----------------------"
    # d_likelihoods = map(lambda x: math.log(abs(x)), d_likelihoods)
    # r_likelihoods = map(lambda x: math.log(abs(x)), r_likelihoods)

    ratios = map(lambda x,y: x/y, d_likelihoods, r_likelihoods)
    

    date_strings = map(lambda x: str(x), dates)
    return {
    'title': "Usage of %s Frame in Speeches about %s" % (frame.name, topic),
    'ylabel': "D/R Ratio of Log-Likelihoods",
    'dates': date_strings,
    'ratios': ratios}    


def plot_moving_average(frame, speeches,n):
    
    window_size = n #analyze 500 speeches at a time
    offset = 10 #slide 50 across each time
    num_bins=len(speeches)/offset
    current_bin = 0
    print 'entering plot moving average'
    b = build_btree(speeches)
    number_of_datapoints = 0
    dates = []
    r_likelihoods = []
    d_likelihoods = []
    
    while not b.is_empty():
        ordered_speeches = []
        dates.append(max(b.nsmallest(n, pop = False))[0][0])
        for item in b.nsmallest(window_size,pop=False):#add 500 speeches to the file_list to analyze
            ordered_speeches.append(item[1])
        b.nsmallest(offset, pop = True) #slide window right by 50 speeches
        current_bin=current_bin+1
        print "analyzing bin %d of %d" % (current_bin, num_bins)
        # print ordered_speeches
        training_set = build_training_set(ordered_speeches)
        
        #from findFrames import return_framing_data
        log_likelihoods = return_framing_datum(training_set, frame)    
        d_likelihoods.append(log_likelihoods[0])
        r_likelihoods.append(log_likelihoods[1])

        print log_likelihoods[0]
        print ""
        print log_likelihoods[1]
        print "----------------------"
        
        number_of_datapoints = number_of_datapoints + 1

    ratios = map(lambda x,y: x/y, d_likelihoods, r_likelihoods)
    date_strings = map(lambda x: str(x), dates)
    return {'title': "Usage of %s Frame " % (frame.name),
    'ylabel': "D/R Ratio of Log-Likelihoods",
    'dates': date_strings, 
    'ratios': ratios} 
