from __future__ import division

import os, sys

root = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root + "/..")

from app.utils import update_progress

from app.models.frame import Frame
from app.models.speech import Speech
from app.models.subgroup import Subgroup
from app.models.analysis import Analysis

from math import exp, log, ceil
import operator
import pdb
import json
import datetime
from dateutil import parser

from blessings import Terminal

t = Terminal()

analysis_id = 3
frame_id = 1

frame = Frame.get(Frame.id == frame_id)
analysis = Analysis.get(Analysis.id == analysis_id)
frame_words = frame.word_string
speech_windows = json.loads(analysis.speech_windows)

frame_plot = eval(analysis.frame_plot)
end_dates = frame_plot['end_dates']
ratios = frame_plot['ratios']

query_params = analysis.build_query_params(order='frame')
query_params['analysis_id'] = analysis_id

print "ASSUMING SUBGROUP A IS REPUBLICAN"
print "ASSUMING SUBGROUP B IS DEMOCRAT"

for speech_window_key, speech_window in speech_windows.items():

	print "----------------------------------------------------"
	print speech_window_key

	speech_window_start, speech_window_end = speech_window_key.split(" - ")
	query_params['start_date'] = speech_window_start
	query_params['end_date'] = speech_window_end

	num_found = Speech.get(0, 0, **query_params)['count']
	pages = int(ceil(num_found/1000))

	print "Downloading %d speeches for analysis %d for window %s ordered by frame ..." % (num_found, analysis_id, speech_window_key)

	speeches = []
	for i in range(0, pages):
	    curr_speech_dicts = Speech.get(start=1000*i, rows=1000, **query_params)['speeches']
	    curr_speech_objs = map(lambda x: Speech(**x), curr_speech_dicts)
	    speeches = speeches + curr_speech_objs
	    update_progress((i+1)/pages)
	print ""

	dem_speeches = filter(lambda speech: speech.speaker_party == 'D', speeches)
	rep_speeches = filter(lambda speech: speech.speaker_party == 'R', speeches)

	print "%d republican speeches" % len(rep_speeches)
	print "%d democratic speeches" % len(dem_speeches)

	print "Recompute Naieve Bayes Output For Classifying Frame (%s) Within Window (%s)" % (frame.seed_word, speech_window_key)
	naive_bayes = Classifier(vocab=frame.word_string.split())
	naive_bayes.learn_vocabulary(map(lambda speech: " ".join(speech.speaking),current_window))
	training_set = Classifier.bunch_with_targets(current_window, analysis.target_function)
	naive_bayes.train_classifier(training_set.data, training_set.target)
	log_probabilities = naive_bayes.classify_document(frame.word_string)

	print "MANUALLY recompute Naieve Bayes Output For Classifying Frame (%s) Within Widnow (%s)" % (frame.seed_word, speech_window_key)
	vocabulary_proba = speech_windows[speech_window_key]
	frame_vocabulary_proba =  { word: vocabulary_proba['word'] if vocabulary_proba.get(word) != None else [0, 0] for word in frame_words.split() }

	bayseian_prior_a_rep = len(rep_speeches) / len(speeches)
	bayseian_prior_b_dem = len(dem_speeches) / len(speeches)

	print "Bayseian Prior A (Rep): ", bayseian_prior_a_rep
	print "Bayseian Prior B (Dem): ", bayseian_prior_b_dem

	sum_log_probability_a_rep = sum(map(lambda (word,log_probabilities): log_probabilities[0],frame_vocabulary_proba.items()))
	sum_log_probability_b_dem = sum(map(lambda (word,log_probabilities): log_probabilities[1],frame_vocabulary_proba.items()))

	print "NB Sum Log Proba A (Rep): ", sum_log_probability_a_rep
	print "NB Sum Log Proba B (Dem): ", sum_log_probability_b_dem

	final_prob_a = bayseian_prior_a_rep * sum_log_probability_a_rep
	final_prob_b = bayseian_prior_b_dem * sum_log_probability_b_dem

	print "Bayseian Prior * Sum Log Proba, A (Rep): ", final_prob_a
	print "Bayseian Prior * Sum Log Proba, B (Dem): ", final_prob_b

	if final_prob_a > final_prob_b:
		print t.red("A (Rep) Prior * Sum Log Proba > B (Dem) Prior * Sum Log Proba: Classify Republican")
	else:
		print t.cyan("B (Dem) Prior * Sum Log Proba > A (Rep) Prior * Sum Log Proba: Classify Democratic")

	end_date = datetime.datetime.combine(parser.parse(speech_window_end), datetime.time(12, 00))
	log_proba_ratio = ratios[end_dates.index(end_date)]
	log_of_log_proba_ratio = log(log_proba_ratio)

	print "Log Proba Ratio: ", log_proba_ratio
	print "Frame Plot Ratio (Log of Log Proba Ratio): ", log_of_log_proba_ratio
	if log_proba_ratio < 1 and log_of_log_proba_ratio < 0:
		print t.cyan("Log Proba < 1 (Log of Log Proba Ratio < 0): Classify Democratic")
	elif log_proba_ratio > 1 and log_of_log_proba_ratio > 0:
		print t.red("Log Proba > 1 (Log of Log Proba Ratio > 0): Classify Republican")
	else:
		print t.red("!!! ERROR ERROR ERROR ERROR ERROR !!!")

	rep_frame_freq = sum(map(lambda speech: speech.frame_freq, rep_speeches))
	dem_frame_freq = sum(map(lambda speech: speech.frame_freq, dem_speeches))

	print "Rep Frame Freq", rep_frame_freq
	print "Dem Frame Freq", dem_frame_freq

	if rep_frame_freq > dem_frame_freq:
		print t.red("Rep Freq > Dem Freq: Classify Republican")
	else:
		print t.cyan("Dem Freq > Rep Freq: Classify Democratic")
