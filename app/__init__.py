# from app import *
# __all__ = ['models', 'controllers']
# TODO: understand __all__ 

import os
import urlparse
import psycopg2
import logging
from flask import Flask, make_response
from flask.ext.cors import origin
from flask_peewee.db import Database
from flask_peewee.rest import RestAPI, RestResource
# from flask.ext.assets import Environment, Bundle
from logging import Formatter, FileHandler
from logging.handlers import TimedRotatingFileHandler

from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    print celery.backend
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

# heroku addons:add heroku-postgresql:dev
# heroku config:set HEROKU=1
if 'HEROKU' in os.environ:
    DEBUG = False
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])  
    DATABASE = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': url.path[1:],
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port,
    }
    CELERY_BROKER_URL = os.environ['REDIS_URL']
    CELERY_RESULT_BACKEND = os.environ['REDIS_URL'] + '/0'

else:
    DEBUG = True
    DATABASE = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': 'framingappdb',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': 5432 ,
        'threadlocals': True
    }
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


# Instantiate Flask

SECRET_KEY='poop'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(__name__)
print app.config
celery = make_celery(app)

# Instantaite Flask Peewee Database ORM
db = Database(app)
db.database.get_conn().set_client_encoding('UTF8')

# Instatiate Flask Peewee REST API

api = RestAPI(app)

# Import All Models and Controllers

from app import database_views
from app import decorators
from app.models import Topic
from app.models import Frame 
from app.models import User
from app.models import Speech
from app.models import SpeechTopic
from app.controllers import Topic
from app.controllers import Frame
from app.controllers import User
from app.controllers import Speech
from app.controllers import SpeechTopic
from app.controllers import Analyze

# Register API

api.setup()

# Set up Cross Origin Requests

@app.after_request 
@origin("*") #allow all origins all methods everywhere in the app
def after(response): return response

# Set Root Route

@app.route("/")
def index():
    if not app.debug:
      return send_file('app/templates/index.html') # production (cached response sent)
    else:
      return make_response(open('app/templates/index.html').read()) # development (no cached response)

# Set up Logging

# if not app.debug:
#   LOG_FILENAME = 'logs/framingapp.log'
#   file_handler = TimedRotatingFileHandler(LOG_FILENAME, when='D', interval=1, delay=False, utc=False) 
#   app.logger.setLevel(logging.INFO)
#   file_handler.setLevel(logging.INFO)
# else:
#   LOG_FILENAME = 'logs/framingapp_debug.log'
#   file_handler = FileHandler(LOG_FILENAME) 
#   app.logger.setLevel(logging.DEBUG)
#   file_handler.setLevel(logging.DEBUG)

# file_handler.setFormatter(Formatter(
#     '%(asctime)s %(levelname)s: %(message)s '
#     '[in %(pathname)s:%(lineno)d]'
# ))

# app.logger.addHandler(file_handler)
# app.logger.info("Starting framingapp __init__ file.")
