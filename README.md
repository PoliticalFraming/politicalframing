# Set Up
1. vagrant box add \ precise64 http://files.vagrantup.com/precise64.box
2. vagrant up



web: gunicorn -w 1 -t 600 app:app

for gunicorn to show errors use DEBUG = True


# ToDo

- use https://pypi.python.org/pypi/inflect to pluralize all API urls instead of manually doing it

- logging
- error handling

- database handling (for security and speed)

- in DB table SPEECH_TOPICS - add a constraint to make a particular speech/topic pair unique
- in DB table TOPICS - add constarint to make 'phrase' feild unique
- combined/composite primary key in SpeechTopic

*** Lanyap ***
- Figure out the structure for the python package. Do i need to be importing app everywhere? Do i need to be passing around the DB like I do?
- figure out why DB has to be on the outside (does it have to do with where runserver.py is?)