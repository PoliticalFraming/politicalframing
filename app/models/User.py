from app import app, db
from peewee import *

class User(db.Model):
    first_name = CharField()
    user_id = PrimaryKeyField(null=True, db_column='id')
    last_name = CharField()
    organization = CharField()

    class Meta:
        db_table = 'users'