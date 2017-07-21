#! /usr/bin/env python
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, renderer_classes

import sys
import argparse
import logging

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

def handle_uploaded_file(f):
    import astropy.io.fits as pyfits
    with open('/data/upload/foo.fits', 'wb+') as destination:
        hdulist = pyfits.open(f)
        #logging.debug('DBG-hdulist.info: {}'.format(hdulist.info()))
        logging.debug('DBG-PrimaryHDU keys:{}'
                      .format(','.join(set(hdulist[0].header.keys()))))
        extkeys = set()
        for hdu in hdulist[1:]:
            extkeys.update(hdu.header.keys())
        logging.debug('DBG-ExtensionHDU keys:{}'.format(','.join(extkeys)))
        for chunk in f.chunks():
            destination.write(chunk)
            
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
