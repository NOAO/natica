#!/bin/sh

pushd /sandbox/natica/naticasite
nohup python3 -u manage.py  runserver --insecure  0.0.0.0:8000 > /var/log/natica/server.log &


