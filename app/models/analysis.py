from app import app, db
from peewee import *

from app.models.topic import Topic
from app.models.frame import Frame

class Analysis(db.Model):

    analysis_id = PrimaryKeyField(null=True, db_column='id')
    celery_id = IntegerField(Null=True)    

    update = BooleanValue(Null=True)

    frame = ForeignKeyField(Frame)
    topic = ForeignKeyField(Topic)
    start_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    states = TextField(null=True) #example: [MA, TX, CA]

    topic_plot = TextField(null=True)
    frame_plot = TextField(null=True)

    class Meta:
        db_table = 'analyses'

    @classmethod
    def compute_analysis(cls, phrase, frame, start_date=None, end_date=None, states=None):
        """
        Class Method:
        - Queries DB for speeches with parameters specified in args.
        - Computes an analysis
        - stores results of the analysis in an instance of the Analysis class.
        - returns ID of that instance
        """

        frame = Frame.get(Frame.name == frame)
        topic = Topic.get(Topic.phrase == phrase)

        speeches = get_speeches_in_date_order(topic.topic_id, states, start_date, end_date)
        speeches = self.remove_irrelevant_speeches(speeches)

        topic_plot, frame_plot = analyze_task.delay(topic, frame, speeches)
        celery.close()

        analysis_obj = Analysis(
            celery_id = result.id,
            update = False, 

            frame = frame,
            topic = topic,
            start_date = start_date,
            end_date = end_date,
            states = states,

            topic_plot = str(topic_plot),
            frame_plot = str(frame_plot))

        app.logger.debug("Computed Analysis %d for topic=%s and frame=%s", 
            analysis_obj.analysis_id,
            topic.phrase,
            frame.name)

        return analysis_obj.analysis_id
    
    @celery.task(bind=True)
    def analyze_task(self, topic, frame, speeches):
        print str(len(speeches)) + " speeches are being analyzed"

        topic_plot = plot_moving_topic_usage(speeches, topic, 100)
        frame_plot = plot_discrete_average(self, frame, speeches, 100, topic.phrase)

        return topic_plot, frame_plot

    ####################### UTILITIES #######################

    def party_fn(self, speeches):
        if speech.speaker_party=="D" or speech.speaker_party=="R":
            return True
        else:
            return False

    def preprocess_speeches(self, speeches, relevance_fn):
        '''Includes only speeches that the '''
        relevant = relevance_fn #plug in what is relevant

        valid_speeches=[]
        for speech in speeches:
            if relevant(speech):
                valid_speeches.append(speech)
        return valid_speeches

    ####################### LOGIC #######################

    def plot_topic_usage(self, ordered_speeches, topic, n):
        """
        ordered_speeches - list of speech objects in date order
        topic - Topic object

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
        'title': "Speeches about %s" % topic.phrase,
        'ylabel': "Number of Speeches",
        'dates': dates, 
        'ratios':ratios,
        'dem_counts':dem_counts,
        'rep_counts':rep_counts}

    def plot_frame_usage(self,frame, speeches, window_size, offset, topic, testing=False):
        """ 
        frame = frame object
        speeches = list of speech objects in date order
        n = number of data points to plot
        testing = True if accessing this method from unit tests

        returns json with dates that correlate to log_likelihoods to plot
        """

        app.logger.debug('entering plot discrete average')

        speeches = deque(sorted(speeches, cmp=date_compare))
        current_window = []

        #setup current window
        for _ in range(window_size):
            current_window.append(speeches.popleft())

        while speeches:

            #move current window over by 'offset'
            for _ in range(offset):
                if speeches:
                    current_window.append(speeches.popleft())
                    current_window = current_window[offset:]
















        
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


