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
        {"coordinates": { "ra": 181.368791666667, "dec": -45.5396111111111 }},
        {"filename": 
         '/data/json-scrape/20170701/ct15m/smarts/c15e_170702_114228_cri.fits.json'
         },
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
        #meta.pop('to_here_count')
        #meta.pop('to_page_result_count')
        qlist.append(dict(meta=meta,
                          queries=connection.queries))

    total = toc()
    return(dict(total_time=total,
                query_count=len(search_list),
                query_list=qlist,
                ))


