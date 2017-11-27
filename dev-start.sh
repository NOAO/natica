#!/bin/sh

pushd /sandbox/natica/naticasite
source /home/vagrant/venv/bin/activate
nohup python3 -u manage.py runserver 0.0.0.0:8000 > /var/log/natica/server.log &

