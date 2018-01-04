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
    all_match_ids = set()
    af='/data/small-json-scrape/k21i_040811_004959_zri.fits.json'
    #of='/data/json-scrape/20170701/ct15m/smarts/c15e_170702_105436_cri.fits.json'
    of='/data/small-json-scrape/c09i_040811_051619_ori.fits.json'
    dd = dict(
        box_min     = {"search_box_min": 2,
                       "coordinates": { "ra": 20.0, "dec": 0.5 }},

        coordinates = {"coordinates": { "ra": 234.343, "dec": 30.599}},
        exposure    = {"exposure_time": [10.0, 19.9] },

        filename    = {"filename": af},      
        image_filter = {"image_filter": ["raw", "calibrated"]},#!!! MEMORY
        obs_date    = {"obs_date": ["2004-08-10", "2004-08-12"] },
        orig_file   = {"original_filename": of},

        pi          = {"pi": "Matthias Dietrich"}, 
        prop_id     = {"prop_id": "2014B-0404"}, #!!! MEMORY
        release     = {"release_date": ["2017-09-12", "2017-09-15"]},
        tele_inst   = {"telescope_instrument": [["ct4m","decam"],]},
        #tele_inst   = {"telescope_instrument":
        #               [['CTIO 4.0-m telescope', 'DECam'],]}, #!!! non-std vals
        )
    search_dict = OrderedDict(sorted(dd.items(), key=lambda t: t[0]))
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
                                      'id_list',
                                      'timestamp',
                                      ])
        hide = 'SELECT natica_fitsfile.id, natica_fitsfile.md5sum, natica_fitsfile.filesize, natica_fitsfile.proposal_id, natica_fitsfile.extras, natica_fitsfile.ra, natica_fitsfile.dec, natica_fitsfile.exposure, natica_fitsfile.archive_filename, natica_fitsfile.date_obs, natica_fitsfile.original_filename, natica_fitsfile.release_date, natica_fitsfile.instrument, natica_fitsfile.telescope FROM natica_fitsfile'
        idlist = [res['id'] for res in response.json()['resultset']]
        all_match_ids.update(idlist)
        query.update(
            name = name,
            #sql = queries[0]['sql'],
            sql = meta['query'].replace('"','').replace(hide,'...'),
            time = queries[0]['time'],
            total_count = meta['total_count'],
            id_list = sorted(idlist),
            #to_here_count = meta['to_here_count'],
            #page_result_count = meta['page_result_count'],
            timestamp = meta['timestamp'],
            )
        qlist.append(query)

    total = toc()
    return dict(total_time=total,
                query_count=len(search_dict),
                query_list=qlist,
                all_ids=sorted(list(all_match_ids))
                )


