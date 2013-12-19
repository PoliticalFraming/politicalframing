from app import app, db
from peewee import *

from app.models.Speech import Speech
from app.models.Topic import Topic
from app.models.Frame import Frame

class SpeechTopic(db.Model):
    relevance = IntegerField(null=True)
    speech = ForeignKeyField(Speech)
    topic = ForeignKeyField(Topic)

    class Meta():
        db_table = 'speech_topic'
        # primary_key = CompositeKey('speech', 'topic')