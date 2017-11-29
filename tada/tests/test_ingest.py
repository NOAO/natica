# EXAMPLE:
#   python -m unittest tests/test_ingest.py
import unittest
import tada
import warnings

class TestIngest(unittest.TestCase):
    def setUp(self):
        self.fits1 = '/data/tada-test-data/short-drop/20141220/wiyn-whirc/obj_355.fits.fz'
        
    def test_submit_1(self):
        warnings.simplefilter("ignore", ResourceWarning)
        warnings.simplefilter("ignore", RuntimeWarning)
        arch_file='NA'
        print('fits1={}'.format(self.fits1))
        arch_file = tada.submit_to_archive(self.fits1, overwrite=True)
        exp='/data/natica-archive/20141219/WIYN/2012B-0500/kww_141220_130138_ori.fits.fz'
        self.assertEqual(arch_file, exp)
        
