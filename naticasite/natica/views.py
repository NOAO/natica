#! /usr/bin/env python
import sys
import argparse
import logging
import hashlib
import json
import requests
import datetime
import pytz

import dateutil.parser
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, renderer_classes

from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.management.base import CommandError

from .models import FitsFile, Hdu
from . import exceptions as nex
from . import search_filters as sf

api_version = '0.0.1' # prototype only

@api_view(['GET'])
def index(request):
    """
    Return the number of reach kind of records.
    """
    counts = dict(FitsFile=FitsFile.objects.count(),
                  PrimaryHDU=Hdu.objects.filter(hdu_idx=0).count(),
                  ExtensionHDU=ExtensionHDU.objects.exclude(hdu_idx=0).count(),
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
    #!!! Insure TELESCOP and INSTRUME have known values (enum)

    def hvalues(k):
        return set([hdu.header.get(k, None) for hdu in hdulist]) - {None}

    def just_one(k):
        vals = hvalues(k)
        if 0 == len(vals):
            raise nex.MissingFieldError('Missing FITS field {}'.format(k))
        if 1 < len(vals):
            raise nex.ConflictingValuesError(
                'Conflicting FITS field values for {}'.format(k))
        return vals.pop()

    def at_least_one(k):
        vals = hvalues(k)
        if 0 == len(vals):
            raise nex.MissingFieldError('Missing FITS field {}'.format(k))
        #return vals.pop()
        return vals

    instrument = just_one('INSTRUME')
    telescope = just_one('TELESCOP')
    dateobs_set = at_least_one('DATE-OBS') #!!!
    #obj_set = at_least_one('OBJECT') 
    ra_set = at_least_one('RA') 
    dec_set = at_least_one('DEC') 
    return(dict(instrument=instrument,
                telescope=telescope,
                dateobs=dateobs_set,
                #obj=object_set,
                ra=ra_set,
                dec=dec_set,
    ))
    
    
#src_fname, arch_fname, md5sum, size,  
def store_metadata(hdulist, vals):
    """Store ALL of the FITS header values into DB."""
    def localize(dateval):
        if dateval == None:
            return None
        else:
            return pytz.utc.localize(dateutil.parser.parse(dateval))

    ## FITS File
    fits = FitsFile(id=vals['md5sum'],
                    original_filename=vals['src_fname'],
                    archive_filename=vals['arch_fname'],
                    filesize=vals['size'],
                    release_date=timezone.now(), #!!!
                    instrument=vals['instrument'],
                    telescope=vals['telescope'],
                    date_obs=localize(vals['dateobs'].pop()), #!!!
                    ra=vals['ra'].pop(), #!!!
                    dec=vals['dec'].pop(), #!!!
    )

    fits.save()

    notstored = {'SIMPLE', 'COMMENT', 'HISTORY', 'EXTEND', ''} #!
    core = set([ f.name.upper() for f in Hdu._meta.get_fields()])
    for idx,hdu in enumerate(hdulist):
        extras = set(hdu.header.keys()) - core - notstored
        logging.debug('DBG-extras={}'.format(extras))
        extradict = {}
        for k in extras:
            extradict[k] = hdu.header[k]
            hduobj = Hdu(fitsfile=fits,
                         hdu_idx=idx,
                         xtension=hdu.header.get('XTENSION',''),
                         bitpix=hdu.header['BITPIX'],
                         naxis=hdu.header['NAXIS'],
                         pcount=hdu.header.get('PCOUNT',None),
                         gcount=hdu.header.get('GCOUNT',None),
                         
                         instrument=hdu.header.get('INSTRUME',''),
                         telescope=hdu.header.get('TELESCOP',''),
                         date_obs  = localize(hdu.header.get('DATE-OBS',None)),
                         obj = hdu.header.get('OBJECT',''),
                         ra = hdu.header.get('RA'),
                         dec = hdu.header.get('DEC'),
                         
                         extras = extradict
            )
            #!!! Add to naxisN array if appropriate
        hduobj.save()
        
def handle_uploaded_file(f, md5sum):
    import astropy.io.fits as pyfits
    tgtfile = '/data/upload/foo.fits' #!!!
    with open(tgtfile, 'wb+') as destination:
        hdulist = pyfits.open(f)
        # Validate headers, abort with approriate error if bad for Archive
        valdict = validate_header(hdulist)

        for chunk in f.chunks():
            destination.write(chunk)
        valdict.update(dict(src_fname = f.name,
                            arch_fname = tgtfile,
                            md5sum = md5sum,
                            size = f.size))
        store_metadata(hdulist,valdict)
    
#@csrf_exempt
@api_view(['POST'])
def ingest(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'],  request.data['md5sum'])

    return JsonResponse(dict(result='file uploaded: {}'
                             .format(request.FILES['file'].name)))

#curl -H "Content-Type: application/json" -X POST -d @natica/fixtures/request-search-1.json http://localhost:8000/natica/search/ | python -m json.tool
@api_view(['POST'])
def search(request):
    """
    Search Archive, returns FITS metadata (header field/values).
    """
    if request.method != 'POST':
        raise Exception('Only accepts POST http method')
    if request.content_type != "application/json":
        raise Exception('Only accepts content_type = application/json')

    page_limit = int(request.GET.get('limit','100')) # num of records per page
    page = int(request.GET.get('page','1'))
    offset = (page-1) * page_limit
    # order:: comma delimitied, leading +/-  (ascending/descending)
    order_fields = request.GET.get('order','original_filename')

    
    body = json.loads(request.body.decode('utf-8'))
    jsearch = body['search']
    logging.debug('jsearch={}'.format(jsearch))

    #!!! add validation against schema

    avail_fields = set([
        'search_box_min',
        'coordinates',
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
        'extras',
    ])
    used_fields = set(jsearch.keys())
    if not (avail_fields >= used_fields):
        unavail = used_fields - avail_fields
        raise nex.ExtraSearchFieldError('Extra fields ({}) in search'
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
         & sf.extras(jsearch.get('extras', None))
         )
    logging.debug('DBG: q={}'.format(str(q)))
    total_count = FitsFile.objects.count()
    qs = FitsFile.objects.filter(q).distinct()\
                                   .order_by(order_fields)[offset:page_limit]
    results=list(qs.values())

    meta = OrderedDict.fromkeys(['api_version',
                                 'timestamp',
                                 'comment',
                                 'query',
                                 'page_result_count',
                                 'to_here_count',
                                 'total_count'])
    meta.update(
        api_version = api_version,
        timestamp = datetime.datetime.now(),
        comment = 'WARNING: Disabled searches: PI, EXPOSURE_TIME ',
        query = str(qs.query),
        page_result_count = len(results),
        to_here_count = offset + len(results),
        total_count = total_count,
    )
    logging.debug('DBG: query={}'.format(qs.query))
    return JsonResponse(dict(meta=meta, results=list(qs.values())))
                        
def submit_fits_file(fits_file_path):
    """For use in a natica MANAGE command"""
    #!logging.debug('DBG-1: natica.submit_fits_file({})'.format(fits_file_path))
    f = open(fits_file_path, 'rb')
    urls = 'http://0.0.0.0:8000/natica/ingest/'
    r = requests.post(urls,
                      data=dict(md5sum=md5(fits_file_path)),
                      files={'file':f})
    logging.debug('submit_fits_file: {}, {}'.format(r.status_code,r.json()))
    if r.status_code != 200:
        raise CommandError(r.json()['errorMessage'])
    return False
    
