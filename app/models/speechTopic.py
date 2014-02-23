from app import app, db
from peewee import *

from app.models.speech import Speech
from app.models.topic import Topic
from app.models.frame import Frame

class SpeechTopic(db.Model):
    relevance = IntegerField(null=True)
    speech = ForeignKeyField(Speech)
    topic = ForeignKeyField(Topic)

    class Meta():
        db_table = 'speech_topic'
        # primary_key = CompositeKey('speech', 'topic')