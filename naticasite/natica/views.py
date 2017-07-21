#! /usr/bin/env python
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, renderer_classes

import sys
import argparse
import logging
from datetime import datetime
import hashlib

from .models import FitsFile, PrimaryHDU, ExtensionHDU

@api_view(['GET'])
def index(request):
    """
    Return the number of reach kind of records.
    """
    counts = dict(FitsFile = FitsFile.objects.count(),
                  PrimaryHDU = PrimaryHDU.objects.count(),
                  ExtensionHDU = ExtensionHDU.objects.count(),
                  )
    logging.debug('DBG-0')
    return JsonResponse(counts)

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def validate_header(hdulist):
    """Raise exception if FITS header is not good enuf for Archive.

    INSTRUME and TELESCOP must exist in at least one HDU and have the
    same value in all of them.

    """
    #! Insure TELESCOP and INSTRUME have known values

    def hvalues(k):
        return set([hdu.header.get(k, None) for hdu in hdulist]) - {None}

    hdrkeys = set()
    for hdu in hdulist:
        hdrkeys.update(hdu.header.keys())
    #assert 'INSTRUME' in hdulist[0].header.keys()
    assert 'INSTRUME' in hdrkeys
    assert 'TELESCOP' in hdrkeys
    instrume_vals = hvalues('INSTRUME')
    telescop_vals = hvalues('TELESCOP')
    dateobs_vals = hvalues('DATE-OBS') #!
    assert 1 == len(instrume_vals)
    assert 1 == len(telescop_vals)
    logging.debug('DBG: instrume_vals={}'.format(instrume_vals))
    logging.debug('DBG: telescop_vals={}'.format(telescop_vals))
    return(dict(instrument=instrume_vals.pop(),
                telescope=telescop_vals.pop(),
                dateobs=dateobs_vals.pop(),
                ))
    
    
#src_fname, arch_fname, md5sum, size,  
def store_metadata(hdulist, vals):
    """Store ALL of the FITS header values into DB."""
    logging.debug('DBG-vals={}'.format(vals))
    fits = FitsFile(id=vals['md5sum'],
                    original_filename=vals['src_fname'],
                    archive_filename=vals['arch_fname'],
                    filesize=vals['size'],
                    release_date=datetime.now() )
    fits.save()

    notstored = {'SIMPLE', 'COMMENT', 'EXTEND'}
    extras = (set(hdulist[0].header.keys()) 
              - set([ f.name.upper() for f in PrimaryHDU._meta.get_fields()])
              - notstored)
    logging.debug('DBG-extras={}'.format(extras))
    extradict = {}
    for k in extras:
        extradict[k] = hdulist[0].header[k]
    primary = PrimaryHDU(fitsfile=fits,
                         bitpix=hdulist[0].header['BITPIX'],
                         naxis=hdulist[0].header['NAXIS'],
                         instrument = vals['instrument'],
                         telescope = vals['telescope'],
                         date_obs  = vals['dateobs'],
                         extras = {vals['instrument']: extradict}
                         )
    primary.save()
    
def handle_uploaded_file(f):
    import astropy.io.fits as pyfits
    tgtfile = '/data/upload/foo.fits' #!!!
    with open(tgtfile, 'wb+') as destination:
        hdulist = pyfits.open(f)
        #!!! Validate headers, abort with approriate error if bad for Archive
        valdict = validate_header(hdulist)
            
        logging.debug('DBG-PrimaryHDU keys:{}'
                      .format(','.join(set(hdulist[0].header.keys()))))
        extkeys = set()
        for hdu in hdulist[1:]:
            extkeys.update(hdu.header.keys())
        logging.debug('DBG-ExtensionHDU keys:{}'.format(','.join(extkeys)))

        for chunk in f.chunks():
            destination.write(chunk)
        valdict.update(dict(src_fname = f.name,
                            arch_fname = tgtfile,
                            md5sum = md5(tgtfile),
                            size = f.size))
        store_metadata(hdulist,valdict)
            
@api_view(['POST'])
def ingest_fits(request):
    logging.debug('DBG-1: natica.ingest_fits({})'.format(request))
    if request.method == 'POST':
        logging.debug('DBG-1')
        handle_uploaded_file(request.FILES['file'])
    return JsonResponse(dict(result='file uploaded'))


##############################################################################

def test_submit_fits(fits_file_path):       
    logging.debug('DBG-1: natica.test_submit_fits({})'.format(fits_file_path))
    import requests
    f = open(fits_file_path, 'rb')
    urls = 'http://0.0.0.0:8000/natica/ingest/'
    logging.debug('DBG-2')
    r = requests.post(urls, files= {'file':f})
    logging.debug('DBG-3')
    print(r.status_code)
    
ff1 = '/data/tada-test-data/basic/kp109391.fits.fz'
ff2 = '/data/tada-test-data/drop-test/20160314/kp4m-mosaic3/mos3.75870.fits.fz'

def main():
    "Parse command line arguments and do the work."
    print('EXECUTING: %s\n\n' % (' '.join(sys.argv)))

    parser = argparse.ArgumentParser(
        description='My shiny new python program',
        epilog='EXAMPLE: %(prog)s a b"'
        )
    parser.add_argument('--version', action='version', version='1.0.1')
    parser.add_argument('infile', # type=argparse.FileType('r'),
                        help='Input file')
    #!parser.add_argument('outfile', type=argparse.FileType('w'),
    #!                    help='Output output')

    parser.add_argument('--loglevel',
                        help='Kind of diagnostic output',
                        choices=['CRTICAL', 'ERROR', 'WARNING',
                                 'INFO', 'DEBUG'],
                        default='WARNING')
    args = parser.parse_args()
    #!args.outfile.close()
    #!args.outfile = args.outfile.name

    #!print 'My args=',args
    #!print 'infile=',args.infile

    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        parser.error('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=log_level,
                        format='%(levelname)s %(message)s',
                        datefmt='%m-%d %H:%M')
    logging.debug('Debug output is enabled in %s !!!', sys.argv[0])

    my_test_submit_fits(args.infile)

if __name__ == '__main__':
    main()
