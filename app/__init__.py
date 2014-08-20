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
import sys

import environment

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/../lib')


class Api(restful.Api):
    def unauthorized(self, response):
        return response

@task_prerun.connect
def on_task_init(*args, **kwargs):
    db.database.close()

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
if 'HEROKU' in os.environ:
    DEBUG = True
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
    #  http://docs.celeryproject.org/en/latest/configuration.html#logging
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_REDIRECT_STDOUTS = True
    CELERY_REDIRECT_STDOUTS_LEVEL = 'DEBUG'
    CELERY_TRACK_STARTED = True
    # CELERY_TASK_SERIALIZER = 'pickle' # change this to json
    # Can be pickle (default), json, yaml, msgpack

solr_url = "http://politicalframing.com:8984/solr" # "http://localhost:8983/solr/"
h = httplib2.Http(cache="/var/tmp/solr_cache")
si = SolrInterface(url = solr_url, http_connection = h)

# Instantiate Flask

SECRET_KEY='poop'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

app = Flask(__name__)
app.config.from_object(__name__)
celery = make_celery(app)

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, { '/': os.path.join(os.path.dirname(__file__), 'static') })
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, { '/': os.path.join(os.path.dirname(__file__), 'static/.tmp') })

# Compile Assets

# assets = Environment(app)
# assets.url = app.static_url_path

# css_bundle = Bundle('css/home.css.sass', filters='sass', output='all.css')
# assets.register('css_all', css_bundle)

# js_bundle = Bundle('js/test.js.coffee', filters='coffeescript', output='all.js')
# assets.register('js_all', js_bundle)

# Instantaite Flask Peewee Database ORM
db = Database(app)
db.database.get_conn().set_client_encoding('UTF8')

# Instatiate Flask Peewee REST API
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
from app.models import frame
from app.models import user
from app.controllers import frame
# from app.controllers import user
from app.controllers import speech
from app.controllers import analysis
from app.controllers import wordnetsocket

# # Set up Cross Origin Requests
# @app.after_request
# @origin("*") #allow all origins all methods everywhere in the app
# def after(response): return response

# Set Root Route

# @app.route("/")
# def index():
#     if not app.debug:
#       return send_file('app/templates/index.html') # production (cached response sent)
#     else:
#       return make_response(open('app/templates/index.html').read()) # development (no cached response)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print path
    return render_template('index.html')

# Set up Logging

from logging import Formatter, FileHandler
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import SysLogHandler

if os.environ.get('HEROKU') is None:
    from logging.handlers import RotatingFileHandler
    LOG_FILENAME = 'logs/framingapp.log'

    with open(LOG_FILENAME,'a') as file:
        # file_handler = FileHandler(LOG_FILENAME)
        # file_handler = RotatingFileHandler(LOG_FILENAME, 'a', 1 * 1024 * 1024, 10)
        file_handler = TimedRotatingFileHandler(LOG_FILENAME, when='D', interval=1, delay=False, utc=False)

    # file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s ' '[in %(pathname)s:%(lineno)d]'))

    ##########################################
    if not app.debug:
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
    ##########################################

    app.logger.addHandler(file_handler)
else:
    stream_handler = logging.StreamHandler()

    ##########################################
    if not app.debug:
        app.logger.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.DEBUG)
    ##########################################

    app.logger.addHandler(stream_handler)

# app.logger.info('PoliticalFraming Startup')
