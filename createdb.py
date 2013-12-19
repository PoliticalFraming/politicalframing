from app import app,db
from peewee import *

from app.models.Frame import Frame, populate_frames_dummy_data
from app.models.Speech import Speech
from app.models.Topic import Topic
from app.models.SpeechTopic import SpeechTopic
from app.models.User import User

Frame.create_table(fail_silently=True)
Speech.create_table(fail_silently=True)
Topic.create_table(fail_silently=True)
SpeechTopic.create_table(fail_silently=True)
User.create_table(fail_silently=True)

db.database.execute_sql("ALTER TABLE speech_topic ADD CONSTRAINT speech_topic_unique UNIQUE(speech_id,topic_id);")

populate_frames_dummy_data()
