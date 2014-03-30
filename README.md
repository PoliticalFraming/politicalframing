[![Stories in Ready](https://badge.waffle.io/politicalframing/politicalframing.png?label=ready&title=Ready)](https://waffle.io/politicalframing/politicalframing)
# Set Up
1. vagrant box add \ precise64 http://files.vagrantup.com/precise64.box
2. vagrant up

web: gunicorn -w 1 -t 600 app:app

for gunicorn to show errors use DEBUG = True


https://github.com/gipi/dokku-django-example