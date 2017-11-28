# from vagrant@archive:/sandbox/natica/naticasite; apply venv, then
./manage.py dumpdata --format json --indent 4 -o /data/naticadb/dump-natica-Proposal.json natica.Proposal
./manage.py dumpdata --format json --indent 4 -o /data/naticadb/dump-natica-FitsFile.json natica.FitsFile
./manage.py dumpdata --format json --indent 4 -o /data/naticadb/dump-natica-Hdu.json natica.Hdu
