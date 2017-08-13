from django.db import connection
from django.test import Client
import json
import time
from collections import OrderedDict
import logging

def wrap(qdict):
    return dict(search=qdict)

def tic():
    tic.start = time.time()
def toc():
    stop = time.time()
    return stop - tic.start

def try_queries():
    c = Client()
    af='/data/json-scrape/20170701/ct15m/smarts/c15e_170702_114228_cri.fits.json'
    of='/data/json-scrape/20170701/ct15m/smarts/c15e_170702_105436_cri.fits.json'
    search_dict = dict(
        coordinates = {"coordinates": { "ra": 181.368, "dec": -45.5396}},
        exposure    = {"exposure_time": [10.0, 19.9] },

        filename    = {"filename": af},      
        image_filter = {"image_filter": ["raw", "calibrated"]},#!!! MEMORY
        obs_date    = {"obs_date": ["2017-07-01", "2017-07-03"] },
        orig_file   = {"original_filename": of},

        pi          = {"pi": "Schlegel"}, # 3.366 8/10/17
        prop_id     = {"prop_id": "2014B-0404"}, #!!! MEMORY
        release     = {"release_date": ["2017-07-25", "2017-07-27"]},
        box_min     = {"search_box_min": 99,
                       "coordinates": { "ra": 181.3, "dec": -45.5 }},
        tele_inst   = {"telescope_instrument": [["ct4m","mosaic_2"],]},
        #tele_inst   = {"telescope_instrument":
        #               [['CTIO 4.0-m telescope', 'DECam'],]}, #!!! non-std vals
        )
    tic()
    qlist = list()
    for name,jsearch in search_dict.items():
        logging.debug('proto.try_queries(); name={}'.format(name))
        try:
            logging.debug('DBG1')
            response = c.post('/natica/search/',
                              content_type='application/json',
                              data=json.dumps(jsearch))
            logging.debug('DBG2')
        except Exception as err:
            logging.debug('DBG3')
            return dict(errorMessage = 'proto.try_queries: {}'.format(err))

        logging.debug('DBG: response.json()={}'.format(response.json()))

        if response.status_code != 200:
            return response.json()
        
        meta=response.json().get('meta')
        logging.debug('proto.try_queries(); result cnt={}'
                      .format(meta['total_count']))
        queries=connection.queries
        query = OrderedDict.fromkeys(['name',
                                      'time',
                                      'sql',
                                      'total_count',
                                      'timestamp',
                                      ])
        query.update(
            name = name,
            #sql = queries[0]['sql'],
            sql = meta['query'],
            time = queries[0]['time'],
            total_count = meta['total_count'],
            #to_here_count = meta['to_here_count'],
            #page_result_count = meta['page_result_count'],
            timestamp = meta['timestamp'],
            )
        qlist.append(query)

    total = toc()
    return dict(total_time=total,
                query_count=len(search_dict),
                query_list=qlist,
                )


