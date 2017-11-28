

# from vagrant@archive:/sandbox/natica/naticasite; apply venv, then
./manage.py shell -c "from natica.models import FitsFile; FitsFile.objects.all().delete()"
find /data/small-json-scrape -name "*.json" -print0 | xargs -0 python3 manage.py stuff_hdus 

 
