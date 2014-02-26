#!/usr/bin/env bash

if [ ! -f /var/log/framingapp_setup ];
then
  echo "Setting up Framing App"
  echo "----------------------------------------"

  export PATH="$HOME/.pyenv/bin:$PATH"
  export PATH="/home/vagrant/.pyenv/shims:$PATH"
  export WORKON_HOME=/home/vagrant/.virtualenvs
  . /home/vagrant/.pyenv/versions/2.7.5/bin/virtualenvwrapper.sh
  pyenv rehash

  cd /vagrant
  mkvirtualenv app
  lsvirtualenv

  # Set up Postgres and create Database
  sudo -u postgres psql -U postgres -d postgres -c "CREATE DATABASE framingappdb;"

  # Start virtualenv on login via bashrc
  echo 'workon app' >> /home/vagrant/.bashrc 

  # Install all python dependencies
  pip install numpy==1.7.0
  pip install -r /vagrant/requirements.txt

  # Create database models

  python manage.py createdb

  sudo touch /var/log/framingapp_setup

fi
