from flask.ext.script import Manager, Server
from flask.ext.assets import ManageAssets
from app import app, db

from peewee import *
from app.models.frame import Frame, populate_frames_dummy_data
from app.models.speech import Speech
from app.models.user import User
from app.models.analysis import Analysis

manager = Manager(app)
manager.add_command("runserver", Server(host="0.0.0.0", port=5000))
# manager.add_command("assets", ManageAssets(assets))

@manager.command
def hello():
    print "hello"

@manager.command
def createdb():
	Frame.create_table(fail_silently=True)
	Analysis.create_table(fail_silently=True)
	Speech.create_table(fail_silently=True)
	Topic.create_table(fail_silently=True)
	SpeechTopic.create_table(fail_silently=True)
	User.create_table(fail_silently=True)
	db.database.execute_sql("ALTER TABLE speech_topic ADD CONSTRAINT speech_topic_unique UNIQUE(speech_id,topic_id);")
	populate_frames_dummy_data()

@manager.command
def deletedb():
	db.database.execute_sql("DROP TABLE frames, speeches, topics, speech_topic, users;")

from app.controllers.analysis import * 
## UNIT TESTS
@manager.command
def test_core_algorithm(): 
	"""Tests plot_discrete_average. """
 	frame_id=1
	topic_id=1

	speeches = get_speeches(topic_id)

	# get list of json objects from the database (query by topic - or also filter by some other subset of factors)
	frame = Frame.get(Frame.frame_id == frame_id)
	topic = Topic.get(Topic.topic_id == topic_id)
	
	#preprocess speeches
	speeches = preprocess_speeches(speeches)
	
	print str(len(speeches)) + " speeches are being analyzed"
	frame_plot = plot_discrete_average(None, frame, speeches, 100, topic.phrase, testing=True)

	return frame_plot

if __name__ == "__main__":
    manager.run()


### SEEEEEEED DATA
# import os 

# #Delete the database
# try:
# 	os.remove('database.db')
# 	print "Database Deleted"
# except:
# 	pass

# #Create new DB
# execfile('createdb.py')
# print "new database created"

# #Populate Frames
# from app.models.frame import populate_frames_dummy_data
# populate_frames_dummy_data()

# #Populate Speeches
# from app.database_views import download_speeches_for_topic
# download_speeches_for_topic('gay')
# download_speeches_for_topic('tomato')
# download_speeches_for_topic('potato')
