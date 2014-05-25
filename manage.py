from flask.ext.script import Manager, Server
from flask.ext.assets import ManageAssets
from app import app, db

from peewee import *
from app.models.frame import Frame
from app.models.speech import Speech
from app.models.user import User
from app.models.analysis import Analysis
from app.models.subgroup import Subgroup

manager = Manager(app)
manager.add_command("runserver", Server(host="0.0.0.0", port=5000))
# manager.add_command("production", Server(host="0.0.0.0", port=5000, use_debugger=True, use_reloader=False, threaded=True))

# manager.add_command("assets", ManageAssets(assets))

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

