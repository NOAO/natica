# Regression test of NATICA services
# MODIFIED from ~/sandbox/mars/marssite/dal/tests.py


from django.core.urlresolvers import reverse
from django.test import TestCase, Client, RequestFactory
from naticasite import settings
import json
#from . import expected as exp
from . import views
import logging
import sys
from contextlib import contextmanager

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


class SearchTest(TestCase):

    #############################################################################
    ### /natica/search
    ###
    af='/data/json-scrape/20170701/ct15m/smarts/c15e_170702_114228_cri.fits.json'
    of='/data/json-scrape/20170701/ct15m/smarts/c15e_170702_105436_cri.fits.json'
    search_dict = dict(
        # vals are (jsearch, response['results'])
        coordinates = ({"coordinates": { "ra": 19.9616, "dec": 0.8161}},
                       'NA'
                       ),
        exposure    = ({"exposure_time": [10.0, 19.9] },
                       'NA'),
        filename    = ({"filename": af},
                       []),
        image_filter = ({"image_filter": ["raw", "calibrated"]},#!!! MEMORY
                       'NA'),
        obs_date    = ({"obs_date": ["2017-07-01", "2017-07-03"] },
                       'NA'),
        orig_file   = ({"original_filename": of},
                       []),
        pi          = ({"pi": "Schlegel"}, # 3.366 8/10/17
                       []),
        prop_id     = ({"prop_id": "2014B-0404"}, #!!! MEMORY
                       []),
        release     = ({"release_date": ["2017-07-25", "2017-07-27"]},
                       []),
        box_min     = ({"search_box_min": 2,
                       "coordinates": { "ra": 20.0, "dec": 0.5 }},
                       'NA'),
        tele_inst   = ({"telescope_instrument": [["ct4m","decam"],]},
                       []),
        #tele_inst   = {"telescope_instrument":
        #               [['CTIO 4.0-m telescope', 'DECam'],]}, #!!! non-std vals
        )

    
#!    def test_search_many(self):
#!        c = Client()
#!        for name,(jsearch,resp) in self.search_dict.items():
#!            print('DBG: testing query for: {}'.format(name))
#!            try:
#!                response = c.post('/natica/search/',
#!                                  content_type='application/json',
#!                                  data=json.dumps(jsearch))
#!            except Exception as err:
#!                return dict(errorMessage = 'test_search_many: {}'.format(err))
#!
#!            print('DBG: name={}, response.json()={}'
#!                  .format(name, response.json()))
#!            meta=response.json().get('meta')
#!            self.assertContains(response.get('results','MISSING_RESULTS'),resp)
        
        
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
        print('DBG: response={}'.format(response.content.decode()))
        self.assertIn('meta', response.json())
        self.assertIn('timestamp', response.json()['meta'])
        self.assertIn('comment', response.json()['meta'])
        self.assertIn('query', response.json()['meta'])
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

    @testcase_log_console(logger)
    def test_search_1(self):
        "MVP-1. Basics. No validation of input"
        #! "filename": "foo",
        req = '''{
        "coordinates": {
            "ra": 181.368791666667,
            "dec": -45.5396111111111
        },
        "pi": "Cypriano",
        "search_box_min": 5.0,
        "prop_id": "noao",
        "obs_date": ["2009-04-01", "2009-04-03", "[]"],
        "original_filename": "/ua84/mosaic/tflagana/3103/stdr1_012.fits",
        "telescope_instrument": [["ct4m","mosaic_2"],["foobar", "bar"]],
        "exposure_time": 15,
        "release_date": "2010-10-01T00:00:00",
        "image_filter":["raw", "calibrated"]
        }'''
        response = self.client.post('/natica/search/',
                                    content_type='application/json',
                                    data=req  )
        #print('DBG: response={}'.format(response.content.decode()))
        self.assertJSONEqual(json.dumps(response.json()['resultset']),
                             json.dumps(json.loads(exp.search_1)['resultset']),
                             msg='Unexpected resultset')
        self.assertEqual(response.status_code, 200)
#!
#!    def test_search_fakeerror_0(self):
#!        "Fake Error for client testing: unknown type (return allowables)"
#!        req = '{ }'
#!        response = self.client.post('/natica/search/?error=foobar',
#!                                    content_type='application/json',
#!                                    data=req)
#!        expected = {'errorMessage':
#!                    'Unknown value (foobar) for URL ERROR parameter. Allowed: '
#!                    'bad_numeric,bad_search_json'}
#!        self.assertJSONEqual(json.dumps(response.json()), json.dumps(expected))
#!        self.assertEqual(response.status_code, 400)
#!
#!    def test_search_fakeerror_1(self):
#!        "Fake Error for client testing: bad_numeric"
#!        req = '{ }'
#!        response = self.client.post('/natica/search/?error=bad_numeric',
#!                                    content_type='application/json',
#!                                    data=req)
#!        expected = {'errorMessage': 'Bad numeric value'}
#!        self.assertJSONEqual(json.dumps(response.json()), json.dumps(expected))
#!        self.assertEqual(response.status_code, 400)
#!
#!    def test_search_error_1(self):
#!        "Error in request content: extra fields sent"
#!        req = '''{"coordinates": {
#!            "ra": 181.368791666667,
#!            "dec": -45.5396111111111
#!        },
#!        "TRY_FILENAME": "foo.fits",
#!        "image_filter":["raw", "calibrated"]
#!        }
#!        '''
#!        response = self.client.post('/natica/search/',
#!                                    content_type='application/json',
#!                                    data=req  )
#!        expected = {"errorMessage": "Extra fields ({'TRY_FILENAME'}) in search"}
#!        #!print('DBG0-tse-1: response={}'.format(response.content.decode()))
#!        #!self.assertJSONEqual(json.dumps(response.json()), json.dumps(expected))
#!        self.assertIn('Extra fields ({\'TRY_FILENAME\'}) in search',
#!                      json.dumps(response.json()['errorMessage']))
#!        self.assertEqual(response.status_code, 400)
#!
#!
#!    def test_search_error_2(self):
#!        "Error in request content: non-decimal RA"
#!        req = '''{ "coordinates": {
#!            "ra": "somethingbad",
#!            "dec": -45.5396111111111
#!        },
#!        "image_filter":["raw", "calibrated"]
#!        }
#!        '''
#!        response = self.client.post('/natica/search/',
#!                                    content_type='application/json',
#!                                    data=req  )
#!        expected = {'errorMessage':
#!                    "Unexpected Error!: Can't convert 'float' object to str implicitly"}
#!        #self.assertJSONEqual(json.dumps(response.json()), json.dumps(expected))
#!        self.assertIn('JSON did not validate against /etc/mars/search-schema.json',
#!                      json.dumps(response.json()['errorMessage']))
#!        self.assertEqual(response.status_code, 400)
#!
#!    def test_search_error_3(self):
#!        "Error in request content: obs_date is numeric (not valid per schema)"
#!        req = '{  "obs_date": 99  }'
#!        response = self.client.post('/natica/search/',
#!                                    content_type='application/json',
#!                                    data=req  )
#!        expected = {"errorMessage": "foo"}
#!        expected = {'errorMessage':
#!                    "JSON did not validate against /etc/mars/search-schema.json; "
#!                    "99 is not valid under any of the given schemas\n"
#!                    "\n"
#!                    "Failed validating 'anyOf' in "
#!                    "schema['properties']['search']['properties']['obs_date']:\n"
#!                    "    {'anyOf': [{'$ref': '#/definitions/date'}]}\n"
#!                    "\n"
#!                    "On instance['search']['obs_date']:\n"
#!                    "    99"}
#!        #self.assertJSONEqual(json.dumps(response.json()), json.dumps(expected))
#!        self.assertIn('JSON did not validate against /etc/mars/search-schema.json',
#!                      json.dumps(response.json()['errorMessage']))
#!        self.assertEqual(response.status_code, 400)
#!
#!    ###
#!    #############################################################################
#!    
#!    def test_tipairs_0(self):
#!        "Return telescope/instrument pairs."
#!        #print('DBG: Using archive database: {}'.format(settings.DATABASES['archive']['HOST']))
#!        response = self.client.get('/dal/ti-pairs/')
#!        #!print('DBG: response={}'.format(response.json()))
#!        #!print('DBG: expected={}'.format(exp.tipairs_0))
#!        self.assertJSONEqual(json.dumps(response.json()),
#!                             json.dumps(exp.tipairs_0))
#!        self.assertEqual(response.status_code, 200)
