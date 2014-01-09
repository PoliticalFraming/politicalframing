from flask.ext.script import Manager
from flask.ext.assets import ManageAssets
from app import app, assets

manager = Manager(app)

manager.add_command("assets", ManageAssets(assets))

@manager.command
def hello():
    print "hello"

if __name__ == "__main__":
    manager.run()


## CREATE DATABASE
# from app import app,db
# from peewee import *

# from app.models.Frame import Frame, populate_frames_dummy_data
# from app.models.Speech import Speech
# from app.models.Topic import Topic
# from app.models.SpeechTopic import SpeechTopic
# from app.models.User import User

# Frame.create_table(fail_silently=True)
# Speech.create_table(fail_silently=True)
# Topic.create_table(fail_silently=True)
# SpeechTopic.create_table(fail_silently=True)
# User.create_table(fail_silently=True)

# db.database.execute_sql("ALTER TABLE speech_topic ADD CONSTRAINT speech_topic_unique UNIQUE(speech_id,topic_id);")

# populate_frames_dummy_data()



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
# from app.models.Frame import populate_frames_dummy_data
# populate_frames_dummy_data()

# #Populate Speeches
# from app.database_views import download_speeches_for_topic
# download_speeches_for_topic('gay')
# download_speeches_for_topic('tomato')
# download_speeches_for_topic('potato')