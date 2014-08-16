# -*- coding: utf-8 -*-
from __future__ import division

from flask.ext.script import Manager, Server, Shell
from flask.ext.assets import ManageAssets
from app import app, db

from peewee import *
from app import models
from app.models import *

manager = Manager(app)
manager.add_command("runserver", Server(host="0.0.0.0", port=5000))
# manager.add_command("production", Server(host="0.0.0.0", port=5000, use_debugger=True, use_reloader=False, threaded=True))
# manager.add_command("assets", ManageAssets(assets))

def shell_imports():

    # add yer imports here
    import os, pickle, json, requests, httplib2
    from sunburnt import SolrInterface
    from app.models import __all__
    for obj in __all__: exec "from app.models import %s" % obj

    solr_url = "http://politicalframing.com:8983/solr/collection1"
    h = httplib2.Http(cache="/var/tmp/solr_cache")
    si = SolrInterface(url = solr_url, http_connection = h)

    imports = {}

    for name, val in locals().items():
        if name not in ['name','val','imports','__all__']:
            imports[name] = eval(name)

    return imports

def _make_context():
    import_dic = shell_imports()
    return dict(app=app, db=db, models=models, division=division, **import_dic)

manager.add_command("shell", Shell(make_context=_make_context))

@manager.command
def hello():
    print "hello"

@manager.command
def createdb():
    Frame.create_table()
    Subgroup.create_table()
    Analysis.create_table()
    User.create_table()

@manager.command
def deletedb():
    db.database.execute_sql("DROP TABLE frames, users, analyses, subgroup;")

@manager.command
def seeddb():
    from app.models.frame import populate_frames_dummy_data
    populate_frames_dummy_data()

from app.controllers.analysis import *
## UNIT TESTS
@manager.command
def test_core_algorithm():
    """Tests plot_discrete_average. """
    pass
    # id=1

    # speeches = get_speeches()

    # get list of json objects from the database (query by topic - or also filter by some other subset of factors)
    # frame = Frame.get(Frame.id == id)

    #preprocess speeches
    # speeches = preprocess_speeches(speeches)

    # print str(len(speeches)) + " speeches are being analyzed"
    # frame_plot = plot_discrete_average(None, frame, speeches, 100, topic.phrase, testing=True)

    # return frame_plot


if __name__ == "__main__":
    manager.run()

