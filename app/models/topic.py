from app import app, db
from peewee import *

class Topic(db.Model):
    topic_id = PrimaryKeyField(null=True, db_column='id')
    phrase = CharField(null=True,unique=True)

    class Meta:
        db_table = 'topics'


def get_topic(topic_id=None):
	return Topic.get(Topic.topic_id == topic_id)
