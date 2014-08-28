from __future__ import division

import os, sys

root = os.path.dirname(os.path.realpath(__file__))
sys.path.append(root + "/..")

from app.utils import update_progress

import logging
from app import app
app.logger.setLevel(logging.INFO)

from app.models.frame import Frame
from app.models.speech import Speech
from app.models.subgroup import Subgroup
from app.models.analysis import Analysis
from app.classifier import Classifier

from math import exp, log, ceil
import operator
# import ipdb
import json
import datetime
import requests
from dateutil import parser

from blessings import Terminal

t = Terminal()

analysis_id = 8

analysis = Analysis.get(Analysis.id == analysis_id)
frame = analysis.frame
speech_windows = json.loads(analysis.speech_windows)

frame_plot = eval(analysis.frame_plot)
end_dates = frame_plot['end_dates']
ratios = frame_plot['ratios']
raw_ratios = frame_plot['raw_ratios']
lengaz = frame_plot['lengaz']
idz = frame_plot['ids']
datez = frame_plot['datez']

print "ASSUMING SUBGROUP A IS REPUBLICAN"
print "ASSUMING SUBGROUP B IS DEMOCRAT"

for speech_window_key, speech_window in speech_windows.items():

	print "----------------------------------------------------"
	print speech_window_key

	speech_window_start, speech_window_end = speech_window_key.split(" - ")

	end_date = datetime.datetime.combine(parser.parse(speech_window_end), datetime.time(12, 00))
	ids = idz[end_dates.index(end_date)]
	proba_ratio = ratios[end_dates.index(end_date)]
	raw_ratio = raw_ratios[end_dates.index(end_date)]
	log_proba_ratio = log(proba_ratio)

	vocabulary_proba = speech_windows[speech_window_key]
	frame_vocabulary_proba =  { word: (abs(vocabulary_proba.get(word)[0] - vocabulary_proba.get(word)[1])) if vocabulary_proba.get(word) != None else 0 for word in frame.word_string.split() }

	query_params = analysis.build_query_params(order='frame')
	query_params['analysis_id'] = analysis_id
	query_params['ids'] = ids
	query_params['start_date'] = speech_window_start
	query_params['end_date'] = speech_window_end

	num_found = Speech.get(rows=0, start=0, **query_params)['count']
	speech_dicts = Speech.get(rows=num_found, start=0, **query_params)['speeches']
	speeches = map(lambda x: Speech(**x), speech_dicts)
	num_found = len(speeches)
	speeches = Analysis.preprocess_speeches(speeches, analysis.subgroup_fn)

	# ipdb.set_trace()

	print "%d speeches after preprocessing" % len(speeches)

	dem_speeches = filter(lambda speech: speech.speaker_party == 'D', speeches)
	rep_speeches = filter(lambda speech: speech.speaker_party == 'R', speeches)

	print "%d republican speeches" % len(rep_speeches)
	print "%d democratic speeches" % len(dem_speeches)

	# ipdb.set_trace()

	# bayseian_prior_a_rep = len(rep_speeches) / len(speeches)
	# bayseian_prior_b_dem = len(dem_speeches) / len(speeches)
	# this frame vocabulary proba has tuples for the proba of class a and b
	# frame_vocabulary_proba =  { word: vocabulary_proba[word] if vocabulary_proba.get(word) != None else [0, 0] for word in frame.word_string.split() }
	# sum_log_probability_a_rep = sum(map(lambda (word,log_probabilities): log_probabilities[0],frame_vocabulary_proba.items()))
	# sum_log_probability_b_dem = sum(map(lambda (word,log_probabilities): log_probabilities[1],frame_vocabulary_proba.items()))
	# final_prob_a = bayseian_prior_a_rep * sum_log_probability_a_rep
	# final_prob_b = bayseian_prior_b_dem * sum_log_probability_b_dem

	print "Recompute Naieve Bayes Output For Classifying Frame (%s) Within Window (%s) for phrase %s" % (frame.seed_word, speech_window_key, analysis.phrase)
	naive_bayes = Classifier(vocab=frame.word_string.split())
	training_set = Classifier.bunch_with_targets(speeches, analysis.target_function2)
	naive_bayes.train_classifier(training_set.data, training_set.target)
	probabilities = naive_bayes.classify_document(frame.word_string)

	tfidf_frames_vector = naive_bayes.vectorizer.transform([frame.word_string])

	print "Predicted Class: ", naive_bayes.classifier.predict(tfidf_frames_vector)[0]
	print "Predict Proba: ", naive_bayes.classifier.predict_proba(tfidf_frames_vector)[0]

	print "Probability A (Rep): ", probabilities[0]
	print "Probability B (Dem): ", probabilities[1]

	if probabilities[0] > probabilities[1]:
		print t.red("A (Rep) NB Proba > B (Dem) NB Proba: Classify Republican")
	else:
		print t.cyan("B (Dem) NB Proba > A (Rep) NB Proba: Classify Democratic")

	print "[DB] Proba Ratio: ", proba_ratio
	print "[DB] Raw Ratios: ", raw_ratio
	print "Frame Plot Ratio (Log Prob Ratio): ", log_proba_ratio # visual ratio, what you see on the graph
	if proba_ratio < 1 and log_proba_ratio < 0:
		print t.cyan("Proba < 1 (Log Proba Ratio < 0): Classify Democratic")
	elif proba_ratio > 1 and log_proba_ratio > 0:
		print t.red("Proba > 1 (Log Proba Ratio > 0): Classify Republican")
	else:
		print t.red("!!! ERROR ERROR ERROR ERROR ERROR !!!")

	rep_frame_freq = sum(map(lambda speech: speech.frame_freq, rep_speeches))# / len(rep_speeches)
	dem_frame_freq = sum(map(lambda speech: speech.frame_freq, dem_speeches))# / len(dem_speeches)

	print "Rep Frame Freq", rep_frame_freq
	print "Dem Frame Freq", dem_frame_freq

	if rep_frame_freq > dem_frame_freq:
		print t.red("Rep Freq > Dem Freq: Classify Republican")
	else:
		print t.cyan("Dem Freq > Rep Freq: Classify Democratic")
