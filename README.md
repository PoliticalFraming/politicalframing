# Set Up 
1. vagrant box add \ precise64 http://files.vagrantup.com/precise64.box
2. vagrant up

    web: gunicorn -w 1 -t 600 app:app


    celery worker --app app:celery
    celery worker --app app:celery --concurrency=4
    celery worker --app app:celery --autoreload
    celery worker --app app:celery --autoscale=10,2
    env CELERYD_FSNOTIFY=kqueue celery worker -l info --app app:celery --autoreload

for gunicorn to show errors use DEBUG = True
https://github.com/gipi/dokku-django-example


create persistent storage in dokku for solr at /var/tmp/solr_cache


# Real Setup
```
brew install rbenv ruby-build
rbenv install 1.9.3-p484
rbenv local 1.9.3-p484

gem install bundler
bundle install

brew install pyenv pyenv-virtualenvwrapper
pyenv install 2.7.8
pyenv local 2.7.8

mkvirtualenv pf
pip install numpy==1.7.1
pip install --upgrade setuptools
pip install --upgrade distribute
pip install -r requirements.txt

brew install node
npm install -g grunt bower
bower install
npm install

createdb framingappdb
python manage.py createdb
python manage.py seeddb
```
