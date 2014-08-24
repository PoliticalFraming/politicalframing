import os
import urlparse
import psycopg2
import httplib2
import logging
from flask import Flask, make_response, render_template
from flask.ext.cors import origin
from flask.ext.restful import Api
from flask_peewee.db import Database
from flask.ext import restful
from sunburnt import SolrInterface
from werkzeug.wsgi import SharedDataMiddleware
# from flask_peewee.rest import RestAPI, RestResource
# from flask.ext.assets import Environment, Bundle

from celery import Celery
from celery.signals import task_prerun
from celery.signals import setup_logging
import sys

import environment

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/../lib')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)


class Api(restful.Api):
    def unauthorized(self, response):
        return response

@task_prerun.connect
def on_task_init(*args, **kwargs):
    db.database.close()

@setup_logging.connect
def app_setup_logging(loglevel, logfile, format, colorize, **kwargs):
    # stream_handler.setFormatter(logging.Formatter(format))
    logger = logging.getLogger('celery')
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)
    return logger

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
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
DEBUG = False

if 'REDIS_URL' not in os.environ:
    os.environ['REDIS_URL'] = 'redis://localhost:6379'

if 'HEROKU' in os.environ:
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
else:
    DATABASE = {
        'engine': 'peewee.PostgresqlDatabase',
        'name': 'framingappdb',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': 5432 ,
        'threadlocals': True
    }

solr_url = "http://politicalframing.com:8983/solr" # "http://localhost:8983/solr/"
h = httplib2.Http(cache="/var/tmp/solr_cache")
si = SolrInterface(url = solr_url, http_connection = h)

SECRET_KEY='poop'
CELERY_BROKER_URL = os.environ['REDIS_URL']
CELERY_RESULT_BACKEND = os.environ['REDIS_URL'] + '/0'
# CELERY_REDIRECT_STDOUTS = True
# CELERY_REDIRECT_STDOUTS_LEVEL = 'DEBUG'
# CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_TRACK_STARTED = True
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Instantiate Flask
app = Flask(__name__)
app.config.from_object(__name__)
app.logger.addHandler(stream_handler)
celery = make_celery(app)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, { '/': os.path.join(os.path.dirname(__file__), 'static') })
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, { '/': os.path.join(os.path.dirname(__file__), 'static/.tmp') })

# Instantiate Flask Peewee Database ORM
db = Database(app)
db.database.get_conn().set_client_encoding('UTF8')

# Instantiate Flask Peewee REST API
# api = RestAPI(app)
api = Api(app)

@api.representation('application/json')
def restful_json(data, code, headers=None):

    def serialize_date(obj):
        import datetime
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")

    import json
    resp = make_response(json.dumps(data, default=serialize_date), code)
    resp.headers.extend(headers or {})
    return resp

# Transaction
db.database.set_autocommit(True)

# Import All Models and Controllers
# from app import database_views
from app import decorators
from app import classifier
from app.models import frame
from app.models import user
from app.controllers import frame
# from app.controllers import user
from app.controllers import speech
from app.controllers import analysis
from app.controllers import wordnetsocket

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

# Set up Logging

# from logging import Formatter, FileHandler
# from logging.handlers import TimedRotatingFileHandler
# from logging.handlers import SysLogHandler

# root = os.path.dirname(os.path.realpath(__file__))
# if os.environ.get('HEROKU') is None:
#     from logging.handlers import RotatingFileHandler
#     LOG_FILENAME = root + '/../logs/framingapp.log'
#     with open(LOG_FILENAME,'a') as file:
#         # file_handler = FileHandler(LOG_FILENAME)
#         # file_handler = RotatingFileHandler(LOG_FILENAME, 'a', 1 * 1024 * 1024, 10)
#         file_handler = TimedRotatingFileHandler(LOG_FILENAME, when='D', interval=1, delay=False, utc=False)
#     # file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#     file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s ' '[in %(pathname)s:%(lineno)d]'))
#     file_handler.setLevel(logging.DEBUG)
#     app.logger.addHandler(file_handler)

app.logger.info('PoliticalFraming Startup')
