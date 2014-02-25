from app import app, db, celery
from peewee import *

from app.models.topic import Topic
from app.models.frame import Frame

class Classifier:
    """Used to allow the adding and removing of speeches to the classifer.
    This could be made faster by actually modifying or extending the MultinomialNB 
    in scikit-learn rather than creating a new MultinomialNB object each time."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB(alpha=1.0,fit_prior=True)

    def learn_vocabulary(self, vocabulary):
        self.vocabulary = vocabulary
        self.vectorizer.fit(vocabulary)

    def train_classifier(self, data, target):
        sparse_data = self.vectorizer.transform(data)
        self.classifier.fit(sparse_data, target)

    def classify_document(self, document):
        tfidf_frames_vector = self.vectorizer.transform(document)
        return self.classifier.predict_log_proba(tfidf_frames_vector)[0]

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

        analysis_obj = Analysis(
            update = False, 
            frame = frame,
            topic = topic,
            start_date = start_date,
            end_date = end_date,
            states = states)

        result = analysis_obj.analyze_task.delay(topic, frame, speeches)
        analysis_obj.celery_id = result.id
        celery.close()


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

    def check_if_complete(self):

        if not self.celery_id: 
            return {'state':"No Celery Task", 'porcent_complete':"n/a"}

        async_res = celery.AsyncResult(self.celery_id)

        if async_res.ready() == True:
            return {'state':async_res.state, 'percent_complete':async_res.info}
        

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

    def build_training_set(self, speeches):
        '''This function is an alternative form of the loads in sklearn which loads 
        from a partiular file structure. This function allows me to load from a the database
        '''
        
        app.logger.debug('Building training set.')

        def target_function(speech):
            if speech.speaker_party == 'D':
                return 0
            elif speech.speaker_party == 'R':
                return 1
            else:
                print "Speech must be categorized as D or R : " + str(speech.speech_id)

        target = [] #0 and 1 for D or R respectively  
        target_names = ['D','R'] #target_names
        data = [] #data

        for speech in speeches:  
            target.append(target_function(speech))
            speech_string = ''
            for sentence in speech.speaking:
                speech_string += sentence    
            data.append(speech_string)
        
        DESCR = "Trained D vs R classifier"

        #Bunch - https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/datasets/base.py
        return Bunch(
            target = target,
            target_names = target_names,
            data = data,
            DESCR = DESCR)
        
    def plot_frame_usage(self,frame, ordered_speeches, window_size, offset, topic, testing=False):
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
            start_dates.append(current_window[0].date)
            end_dates.append(current_window[-1].date)

            training_set = build_training_set(current_window)

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

            return {
                'title': "Usage of %s Frame in Speeches about %s" % (frame.name, topic),
                'ylabel': "D/R Ratio of Log-Likelihoods",
                'start_dates': start_dates,
                'end_dates': date_strings,
                'ratios': ratios}