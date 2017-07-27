from django.db import connection
from django.test import Client
import json
import time

def wrap(qdict):
    return dict(search=qdict)

def tic():
    tic.start = time.time()
def toc():
    stop = time.time()
    return stop - tic.start

def try_queries():
    c = Client()
    search_list = [
        { "exposure_time": [10.0, 19.9] },
        { "obs_date": ["2017-07-01", "2017-07-03"] },
    ]
    tic()
    qlist = list()
    for jsearch in search_list:
        response = c.post('/natica/search/',
                          content_type='application/json',
                          data=json.dumps(wrap(jsearch)))
        meta=response.json().get('meta')
        meta.pop('api_version')
        meta.pop('comment')
        meta.pop('query')
        qlist.append(dict(meta=meta,
                          queries=connection.queries))

    total = toc()
    return(dict(total_time=total,
                query_count=len(search_list),
                query_list=qlist,
                ))


