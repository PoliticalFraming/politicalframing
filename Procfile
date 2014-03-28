web: gunicorn -k gevent --debug app:app
worker: celery worker --app app:celery