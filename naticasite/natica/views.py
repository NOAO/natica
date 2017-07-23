#! /usr/bin/env python
import sys
import argparse
import logging
import hashlib
import json
import requests
import datetime

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, renderer_classes

from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from .models import FitsFile, PrimaryHDU, ExtensionHDU
from . import exceptions as nex
from . import search_filters as sf

api_version = '0.0.1' # prototype only

@api_view(['GET'])
def index(request):
    """
    Return the number of reach kind of records.
    """
    counts = dict(FitsFile = FitsFile.objects.count(),
                  PrimaryHDU = PrimaryHDU.objects.count(),
                  ExtensionHDU = ExtensionHDU.objects.count(),
                  )
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
    dateobs_vals = hvalues('DATE-OBS') #!!!
    object_vals = hvalues('OBJECT')
    assert 1 == len(instrume_vals)
    assert 1 == len(telescop_vals)
    assert 0 < len(object_vals)
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
    prihdr = hdulist[0].header

    ## FITS File
    fits = FitsFile(id=vals['md5sum'],
                    original_filename=vals['src_fname'],
                    archive_filename=vals['arch_fname'],
                    filesize=vals['size'],
                    release_date=timezone.now() )
    fits.save()

    ## Primary HDU
    #!!! Add to naxisN array if appropriate
    notstored = {'SIMPLE', 'COMMENT', 'HISTORY', 'EXTEND', ''} #!
    extras = (set(prihdr.keys()) 
              - set([ f.name.upper() for f in PrimaryHDU._meta.get_fields()])
              - notstored)
    logging.debug('DBG-extras={}'.format(extras))
    extradict = {}
    for k in extras:
        extradict[k] = prihdr[k]
    primary = PrimaryHDU(fitsfile=fits,
                         bitpix=prihdr['BITPIX'],
                         naxis=prihdr['NAXIS'],
                         instrument = vals['instrument'],
                         telescope = vals['telescope'],
                         date_obs = vals['dateobs'],
                         obj = prihdr.get('OBJECT',''),
                         ra = prihdr.get('RA'),
                         dec = prihdr.get('DEC'),
                         extras = {vals['instrument']: extradict}
                         )
    primary.save()

    ## Extension HDUs
    #!!! Add to naxisN array if appropriate
    #!!! Should move/remove some values from Extension to Primary
    #    (e.g. instrument, telescope)
    extension_core = set([ f.name.upper()
                           for f in ExtensionHDU._meta.get_fields()])
    for idx,hdu in enumerate(hdulist[1:],1):
        extras = set(hdu.header.keys()) - extension_core - notstored
        logging.debug('DBG-HDU[{}] extras={}'.format(idx,extras))
        extradict = {}
        for k in extras:
            extradict[k] = hdu.header[k]
        extension = ExtensionHDU(fitsfile=fits,
                                 extension_idx=idx,
                                 xtension=hdu.header['XTENSION'],
                                 naxis=hdu.header['NAXIS'],
                                 pcount=hdu.header['PCOUNT'],
                                 gcount=hdu.header['GCOUNT'],
                                 date_obs  = hdu.header['DATE-OBS'],
                                 obj = hdu.header.get('OBJECT',''),
                                 ra = hdu.header.get('RA'),
                                 dec = hdu.header.get('DEC'),
                                 extras = {vals['instrument']: extradict}
                                 )
        extension.save()
        
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
        try: 
            store_metadata(hdulist,valdict)
        except Exception as err:
            raise nex.CannotStoreInDB(err)
            
#@csrf_exempt
@api_view(['POST'])
def ingest_fits(request):
    logging.debug('DBG-1: natica.ingest_fits({})'.format(request))
    if request.method == 'POST':
        logging.debug('DBG-1')
        handle_uploaded_file(request.FILES['file'])
    return JsonResponse(dict(result='file uploaded'))

# curl -H "Content-Type: application/json" -X POST -d @request-search-1.json http://localhost:8080/natica/search/ | python -m json.tool
@api_view(['POST'])
def search(request):
    """
    Search Archive, returns FITS metadata (header field/values).
    """
    if request.method != 'POST':
        raise Exception('Only accepts POST http method')
    if request.content_type != "application/json":
        raise Exception('Only accepts content_type = application/json')

    body = json.loads(request.body.decode('utf-8'))
    jsearch = body['search']
    logging.debug('jsearch={}'.format(jsearch))

    #!!! add validation against schema

    avail_fields = set([
        'search_box_min',
        'pi',
        'prop_id',
        'obs_date',
        'filename',
        'original_filename',
        'telescope_instrument',
        'release_date',
        'flag_raw',
        'image_filter',
        'exposure_time',
        'coordinates',
    ])
    used_fields = set(jsearch.keys())
    if not (avail_fields >= used_fields):
        unavail = used_fields - avail_fields
        #print('DBG: Extra fields ({}) in search'.format(unavail))
        raise dex.UnknownSearchField('Extra fields ({}) in search'
                                     .format(unavail))
    assert(avail_fields >= used_fields)

    # Construct query (anchored on FitsFile)
    slop = jsearch.get('search_box_min', .001)
    q = (sf.coordinates(jsearch.get('coordinates', None), slop)
         & sf.pi(jsearch.get('pi', None))
         & sf.propid(jsearch.get('propid', None))
         & sf.dateobs(jsearch.get('obs_date', None))
         & sf.archive_filename(jsearch.get('filename', None))
         & sf.original_filename(jsearch.get('original_filename', None))
         & sf.telescope_instrument(jsearch.get('telescope_instrument', None))
         & sf.release_date(jsearch.get('release_date', None))
         & sf.flag_raw(jsearch.get('flag_raw', None))
         & sf.image_filter(jsearch.get('image_filter', None))
         & sf.exposure_time(jsearch.get('exposure_time', None))
         )

    qs = FitsFile.objects.filter(q)
    meta = dict(
        api_version = api_version,
        timestamp = datetime.datetime.now(),
        comment = (
            'WARNING: Has not been tested AT ALL.'
            ' Much of the search is disabled..'
        ),
        query = str(qs.query)
        #! page_result_count = len(results),
        #! to_here_count = offset + len(results),
        #! total_count = total_count,
    )
    return JsonResponse(dict(meta=meta, results=list(qs.values())))
                        
def submit_fits_file(fits_file_path):
    """For use in a natica MANAGE command"""
    #!logging.debug('DBG-1: natica.submit_fits_file({})'.format(fits_file_path))
    f = open(fits_file_path, 'rb')
    urls = 'http://0.0.0.0:8000/natica/ingest/'
    r = requests.post(urls, files= {'file':f})
    print(r.status_code)
    
