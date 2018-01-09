# Regression test of NATICA services
# MODIFIED from ~/sandbox/mars/marssite/dal/tests.py
# EXAMPLE:
#   cd /sandbox/natica/naticasite
#  ./manage.py test natica.tests.StoreTest
#  ./manage.py test natica.tests.SearchTest.test_search_0
#  ./manage.py test natica.tests.SearchTest.test_search_many
#  ./manage.py test natica.tests.SearchTest
#  ./manage.py test
#   


import logging
import sys
from pprint import pformat
from contextlib import contextmanager
import hashlib
import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory
from naticasite import settings
from . import expected as exp
from . import views
from .search_query_response import search_dict

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@contextmanager
def streamhandler_to_console(lggr):
    # Use 'up to date' value of sys.stdout for StreamHandler,
    # as set by test runner.
    stream_handler = logging.StreamHandler(sys.stdout)
    lggr.addHandler(stream_handler)
    yield
    lggr.removeHandler(stream_handler)

def testcase_log_console(lggr):
    def testcase_decorator(func):
        def testcase_log_console(*args, **kwargs):
            with streamhandler_to_console(lggr):
                return func(*args, **kwargs)
        return testcase_log_console
    return testcase_decorator

logger = logging.getLogger('django_test')


class StoreTest(TestCase):
    maxDiff = None # too see full values in DIFF on assert failure
    fixtures = ['natica.yaml', ]

    def setUp(self):
        self.fits1 = '/data/natica-archive/20141225/ct13m/smarts/c13a_141226_070040_ori.fits.fz'

    @testcase_log_console(logger)
    def test_store_0(self):
        """No duplicate, valid FITS for NATICA"""
        overwrite=False
        expected = {'archive_filename': '/data/natica-archive/20141225/ct13m/smarts/c13a_141226_070040_ori.fits.fz',
                    'result': 'file uploaded: c13a_141226_070040_ori.fits.fz'}
        with open(self.fits1, 'rb') as f:
            response = self.client.post(
                '/natica/store/',
                dict(md5sum=md5(self.fits1), file=f))
        jresponse=response.json()
        #!logger.debug('DBG: store_0 jresponse={}'.format(pformat(jresponse)))
        self.assertJSONEqual(json.dumps(jresponse),
                             json.dumps(expected),
                             msg='Unexpected response')
        self.assertEqual(response.status_code, 200)
        
            
    @testcase_log_console(logger)
    def test_store_1(self):
        """Error: Duplicate"""
        overwrite=False
        expected = {'errorMessage':
                    'Could not store metadata; duplicate key value violates '
                    'unique constraint "natica_fitsfile_md5sum_key"\n'
                    'DETAIL:  Key (md5sum)=(8e0cbc0669e8f07427ef0295becfeda8) '
                    'already exists.\n'}
        with open(self.fits1, 'rb') as f:
            response = self.client.post(
                '/natica/store/',
                dict(md5sum=md5(self.fits1), file=f))
        with open(self.fits1, 'rb') as f:
            response = self.client.post(
                '/natica/store/',
                dict(md5sum=md5(self.fits1), file=f))
        jresponse=response.json()
        #!logger.debug('DBG: store_1 jresponse={}'.format(pformat(jresponse)))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(json.dumps(jresponse), json.dumps(expected),
                             msg='Unexpected response3')

        

class SearchTest(TestCase):

    maxDiff = None # too see full values in DIFF on assert failure
    #fixtures = ['dump-natica.json',]
    #fixtures = ['small-dump.json']
    fixtures = ['dump.natica.yaml',
                'search_hits.Proposal.yaml',
                'search_hits.FitsFile.yaml',
    ]
    
    #############################################################################
    ### /natica/search
    ###
    
    @testcase_log_console(logger)
    def test_search_many(self):
        "Try one of each type of search clause supported by DAL."
        c = Client()
        for name,(jsearch,expected) in search_dict.items():
            #! print('DBG: testing query for: {}'.format(name))
            try:
                response = c.post('/natica/search/',
                                  content_type='application/json',
                                  data=json.dumps(jsearch))
            except Exception as err:
                return dict(errorMessage = 'test_search_many: {}'.format(err))

            #!print('DBG: name={}, response.json()=\n{}'
            #!      .format(name, pformat(response.json()['resultset'])))
            self.assertJSONEqual(json.dumps(response.json()['resultset']),
                                 json.dumps(expected))
        
    #@testcase_log_console(logger)
    def test_search_0(self):
        "No filter. Verify: API version."
        req = '{ }'
        #print('DBG: settings.DATABASES={}'.format(settings.DATABASES))
        print('DBG: Using archive database: {}'
              .format(settings.DATABASES['default']['HOST']))
        response = self.client.post('/natica/search/',
                                    content_type='application/json',
                                    data=req  )
        meta = {"natica_version": "0.1.6",
                "timestamp": "2017-07-05T11:44:05.946",
                "comment": "WARNING: Prototype only!",
                "query": "SELECT ...",
                "page_result_count": 100,
                "to_here_count": 100,
                "total_count": 11583954}
        jresponse=response.json()
        #print('DBG: jresponse=',pformat(jresponse))
        del jresponse['meta']['query']
        logger.debug('DBG: search_0 response={}'.format(pformat(jresponse)))
        self.assertIn('meta', response.json())
        self.assertIn('timestamp', response.json()['meta'])
        self.assertIn('comment', response.json()['meta'])
        #self.assertIn('query', response.json()['meta'])
        self.assertIn('page_result_count', response.json()['meta'])
        self.assertIn('to_here_count', response.json()['meta'])
        self.assertIn('total_count', response.json()['meta'])
        self.assertIsInstance(response.json()['meta']['page_result_count'], int)
        self.assertIsInstance(response.json()['meta']['to_here_count'], int)
        self.assertIsInstance(response.json()['meta']['total_count'], int)
        self.assertTrue(response.json()['meta']['page_result_count']
                        <= response.json()['meta']['to_here_count']
                        <= response.json()['meta']['total_count'])
        self.assertEqual(json.dumps(response.json()['meta']['api_version']),
                         '"0.1.7"',
                         msg='Unexpected API version')
        self.assertEqual(response.status_code, 200)
        #!self.assertJSONEqual(json.dumps(response.json()['resultset']),
        #!                     json.dumps(json.loads(exp.search_0)['resultset']),
        #!                     msg='Unexpected resultset')
        
    @testcase_log_console(logger)
    def test_search_1(self):
        "MVP-1. Basics. No validation of input"
        req = '''{
    "coordinates": { "ra": 323, "dec": -1 },
    "search_box_min": 2.0,
    "pi": "Vivas",
    "prop_id": "2017B-0951",
    "obs_date": ["2017-08-10", "2017-08-20", "[]"],
    "original_filename": 
        "/data/small-json-scrape/c4d_170815_054546_ori.fits.json",
    "telescope_instrument": [["ct4m","decam"],["foobar", "bar"]],
    "exposure_time": 10,	
    "release_date": "2017-09-14"
}
'''
#@@@    "image_filter":["raw", "calibrated"],

        response = self.client.post('/natica/search/',
                                    content_type='application/json',
                                    data=req  )
        jresponse=response.json()
        del jresponse['meta']['query']
        #!logger.debug('DBG: search_1 response={}'.format(pformat(jresponse)))
        self.assertJSONEqual(json.dumps(response.json()['resultset']),
                             json.dumps(json.loads(exp.search_1)['resultset']),
                             msg='Unexpected resultset')
        self.assertEqual(response.status_code, 200)


    def test_search_error_1(self):
        "Error in request content: extra fields sent"
        req = '''{"coordinates": {
            "ra": 181.368791666667,
            "dec": -45.5396111111111
        }, "EXTRA_FIELD": "foo.fits"}'''
        response = self.client.post('/natica/search/',
                                    content_type='application/json',
                                    data=req  )
        expected = {"errorMessage": "Extra fields ({'EXTRA_FIELD'}) in search"}
        #print('DBG0-tse-1: response={}'.format(response.content.decode()))
        #!self.assertJSONEqual(json.dumps(response.json()), json.dumps(expected))
        self.assertJSONEqual(json.dumps(expected['errorMessage']),
                             json.dumps(response.json()['errorMessage']))
        self.assertEqual(response.status_code, 400)

    def test_search_error_2(self):
        "Error in request content: non-decimal RA"
        req = '''{ "coordinates": {
            "ra": "somethingbad",
            "dec": -45.5396111111111
        }}'''
        response = self.client.post('/natica/search/',
                                    content_type='application/json',
                                    data=req  )
        #print('DBG0-tse-2: response={}'.format(response.content.decode()))
        expected = {"errorMessage": "JSON did not validate against /etc/natica/search-schema.json; 'somethingbad' is not of type 'number'"}
        self.assertJSONEqual(json.dumps(response.json()),
                             json.dumps(expected))
        self.assertEqual(response.status_code, 400)


    ###
    #############################################################################
    
    #!def test_tipairs_0(self):
    #!    "Return telescope/instrument pairs."
    #!    response = self.client.get('/natica/ti-pairs/')
    #!    print('DBG: response={}'.format(response.json()))
    #!    print('DBG: expected={}'.format(exp.tipairs_0))
    #!    self.assertJSONEqual(json.dumps(response.json()),
    #!                         json.dumps(exp.tipairs_0))
    #!    self.assertEqual(response.status_code, 200)
