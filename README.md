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