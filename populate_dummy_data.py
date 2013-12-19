import os 

#Delete the database
try:
	os.remove('database.db')
	print "Database Deleted"
except:
	pass

#Create new DB
execfile('createdb.py')
print "new database created"

#Populate Frames
from app.models.Frame import populate_frames_dummy_data
populate_frames_dummy_data()

#Populate Speeches
from app.database_views import download_speeches_for_topic
download_speeches_for_topic('gay')
download_speeches_for_topic('tomato')
download_speeches_for_topic('potato')