#!/bin/sh
# EXAMPLE:
#   on mars as vagrant
#   /sandbox/natica/dev-start.sh

pushd /sandbox/natica/naticasite
#source /home/vagrant/venv/bin/activate
source /opt/natica/venv/bin/activate
nohup python3 -u manage.py runserver 0.0.0.0:8000 > /var/log/natica/server.log &

