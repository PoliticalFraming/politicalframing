FROM ubuntu:trusty

# ubuntu packages
RUN apt-get update
RUN apt-get install -y software-properties-common build-essential git g++ curl
RUN apt-get install -y libxml2-dev libxslt-dev
RUN apt-get install -y gfortran libatlas-dev libatlas-base-dev
RUN apt-get install -y libblas-dev libblas3gf libblas-doc liblapack3gf liblapack-dev liblapack-doc

# ruby
RUN apt-add-repository -y ppa:brightbox/ruby-ng
RUN apt-get install -y ruby2.3 ruby2.3-dev
RUN gem install sass
RUN gem install compass
RUN gem install sass-globbing

# node
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -
RUN apt-get install -y nodejs

