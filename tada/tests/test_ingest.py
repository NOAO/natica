# EXAMPLE:
#   cd /sandbox/natica/tada
#   python -m unittest tests.test_ingest.TestTada.test_submit_0
#   python -m unittest tests/test_ingest.py
#   python -m unittest  # auto discovery
import unittest
import tada
import warnings
import logging
import sys
import json
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



class TestTada(unittest.TestCase):
    maxDiff = None # too see full values in DIFF on assert failure
    
    def setUp(self):
        self.fits1 = '/data/tada-test-data/short-drop/20141220/wiyn-whirc/obj_355.fits.fz'
        
    #@testcase_log_console(logger)
    def test_submit_0(self):
        warnings.simplefilter("ignore", ResourceWarning)
        warnings.simplefilter("ignore", RuntimeWarning)
        arch_file='NA'
        #print('fits1={}'.format(self.fits1))

        # Duplicate submit to raise error
        #with self.assertRaises(Exception) as cm:
        arch_file = tada.submit_to_archive(self.fits1, overwrite=False)
        arch_file = tada.submit_to_archive(self.fits1, overwrite=False)

        #!logger.debug('DBG-2: arch_file: "{}"'.format(arch_file))

        jresponse = {'errorMessage': 'Could not store metadata; duplicate key value violates unique constraint \"natica_fitsfile_md5sum_key\"\nDETAIL:  Key (md5sum)=(06822d2641fc8d332fe2961059138863) already exists.\n'}
        exp=('Failed to ingest using natica/store webservice with'
             ' /var/tada/cache/2148387e3e6eec69f04e9360043f61e4.fits.fz; {}')\
             .format(json.dumps(jresponse))
        exp='Failed to ingest using natica/store webservice with /var/tada/cache/2148387e3e6eec69f04e9360043f61e4.fits.fz; {\'errorMessage\': \'Could not store metadata; duplicate key value violates unique constraint "natica_fitsfile_md5sum_key"\\nDETAIL:  Key (md5sum)=(06822d2641fc8d332fe2961059138863) already exists.\\n\'}'
        self.assertEqual(arch_file, exp)

            
        

    def test_submit_1(self):
        warnings.simplefilter("ignore", ResourceWarning)
        warnings.simplefilter("ignore", RuntimeWarning)
        arch_file='NA'
        #print('fits1={}'.format(self.fits1))
        arch_file = tada.submit_to_archive(self.fits1, overwrite=True)
        exp='/data/natica-archive/20141219/WIYN/2012B-0500/kww_141220_130138_ori.fits.fz'
        self.assertEqual(arch_file, exp)
        
