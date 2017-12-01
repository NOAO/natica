#!/bin/sh
# Run ALL natica tests.  (on archive as vagrant)
# Generally should get all NATICATSITE stuff passing before doing TADA
# 

source /opt/natica/venv/bin/activate

echo "Run: NATICASITE web service tests."
pushd /sandbox/natica/naticasite
./manage.py test
popd

echo "Run: TADA-for-NATICA tests."
pushd /sandbox/natica/tada
python -m unittest  # auto discovery
popd
