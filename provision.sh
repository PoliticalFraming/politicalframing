#!/usr/bin/env bash

# Create generic virtual machine with up to date versions of Ruby, Python, and Node

if [ ! -f /var/log/ubuntu_setup ];
then

	echo "Installing Ubuntu Dependencies"
	echo "----------------------------------------"

	sudo apt-get update
	sudo apt-get install -y python-software-properties
	sudo apt-get install -y vim
	sudo apt-get install -y build-essential
	sudo apt-get install -y make
	sudo apt-get install -y g++
	sudo apt-get install -y libbz2-dev
	sudo apt-get install -y libsqlite3-dev
	sudo apt-get install -y git
	sudo apt-get install -y libatlas-dev
	sudo apt-get install -y libatlas-base-dev
	sudo apt-get install -y gfortran
	sudo apt-get install -y libpng12-dev
	sudo apt-get install -y libjpeg-dev
	sudo apt-get install -y libfreetype6-dev
	sudo apt-get install -y zlib1g-dev
	sudo apt-get install -y openssl
	sudo apt-get install -y postgresql
	sudo apt-get install -y postgresql-contrib
	sudo apt-get install -y python-psycopg2
	sudo apt-get install -y libpq-dev
	sudo apt-get install -y libevent-dev
	sudo apt-get install -y nginx

	sudo apt-get install -y libblas-dev
	sudo apt-get isnatll -y libblas3gf
	sudo apt-get install -y libblas-doc
	sudo apt-get install -y liblapack3gf
	sudo apt-get install -y liblapack-dev
	sudo apt-get install -y liblapack-doc

	sudo add-apt-repository -y ppa:chris-lea/node.js
	sudo apt-get update
	sudo apt-get install -y nodejs

	sudo touch /var/log/ubuntu_setup
fi

# Download and install Ruby

if [ ! -f /var/log/ruby_setup ];
then
	git clone git://github.com/sstephenson/rbenv.git /home/vagrant/.rbenv
	git clone https://github.com/sstephenson/ruby-build.git /home/vagrant/.rbenv/plugins/ruby-build
	echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> /home/vagrant/.bashrc
	echo 'eval "$(rbenv init -)"' >> /home/vagrant/.bashrc
	
	# cannot source .bashrc in provision script for some reason
	# so I'm manually exporting these for use
	export PATH="$HOME/.rbenv/bin:$PATH"
	export PATH="/home/vagrant/.rbenv/shims:$PATH"

	rbenv install 2.0.0-p247
	rbenv global 2.0.0-p247
	rbenv rehash

	gem install sass
	gem install compass
	gem install sass-globbing

	sudo touch /var/log/ruby_setup
fi

# Download and install pyenv

if [ ! -f /var/log/python_setup ];
then
	git clone git://github.com/yyuu/pyenv.git /home/vagrant/.pyenv
	echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> /home/vagrant/.bashrc
	echo 'eval "$(pyenv init -)"' >> /home/vagrant/.bashrc

	# cannot source .bashrc in provision script for some rason
	# so I'm manually exporting these for use
	export PATH="$HOME/.pyenv/bin:$PATH"
	export PATH="/home/vagrant/.pyenv/shims:$PATH"

	pyenv install 2.7.5
	pyenv global 2.7.5
	pyenv rehash

	sudo touch /var/log/python_setup
fi

if [ ! -f /var/log/virtualenv_setup ];
then
	export PATH="$HOME/.pyenv/bin:$PATH"
	export PATH="/home/vagrant/.pyenv/shims:$PATH"

	echo "Installing VirtualEnv"
	echo "----------------------------------------"

	pip install virtualenv
	pip install virtualenvwrapper
	pyenv rehash
	mkdir -p /home/vagrant/.virtualenvs
	echo 'export WORKON_HOME=~/.virtualenvs' >> /home/vagrant/.bashrc
	echo 'source /home/vagrant/.pyenv/versions/2.7.5/bin/virtualenvwrapper.sh' >> /home/vagrant/.bashrc

	export WORKON_HOME=/home/vagrant/.virtualenvs
	source /home/vagrant/.pyenv/versions/2.7.5/bin/virtualenvwrapper.sh

	sudo touch /var/log/virtualenv_setup

fi

if [ ! -f /var/log/postgres_setup ];
then
	echo "Set up Postgres"
	echo "----------------------------------------"

	sudo -u postgres psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"
	sudo -u postgres psql -U postgres -d postgres -c "CREATE ROLE vagrant WITH CREATEDB CREATEROLE SUPERUSER LOGIN REPLICATION PASSWORD 'postgres';"
	sudo -u postgres psql -U postgres -d postgres -c "CREATE DATABASE vagrant;"

	sudo touch /var/log/postgres_setup
fi

if [ ! -f /var/log/app_setup ];
then
  echo "Setting up App"
  echo "----------------------------------------"
  
  echo 'cd /vagrant' >> /home/vagrant/.bashrc
  sudo touch /var/log/app_setup
  
  if [ -f /vagrant/setup.sh ];
  then
  	sudo chmod +x /vagrant/setup.sh
  	source /vagrant/setup.sh
  fi

fi
