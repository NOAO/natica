#! /usr/bin/env python
import sys
import argparse
import logging
import hashlib
import json
import requests
import datetime
import pytz
from collections import OrderedDict, defaultdict

import astropy.coordinates as coord
import astropy.units as u

import dateutil.parser
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, renderer_classes

from django.test import Client
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.management.base import CommandError
from django.views.decorators.cache import never_cache
import django_tables2 as tables

from .models import FitsFile, Hdu
from .forms import SearchForm
from . import exceptions as nex
from . import search_filters as sf
from . import proto

api_version = '0.0.2' # prototype only

def todeg(sexstr):
    return coord.Angle(sexstr, unit=u.deg).degree

def proto_html(ttime, qcount, query_list):
    html = '''<ul>
<li>Total Time: {total_time}</li>
<li>Number of queries: {query_count}</li>
</ul>
'''.format(total_time=ttime, query_count=qcount)

    html+='<table><tr><th>Time</th><th>Name</th><th>Count</th><th>SQL</th></tr>'
    for q in query_list:
        html += '<tr> <td>{time}</td><td>{name}</td><td>{total_count}</td><td>{sql}</td> </tr>'.format(**q)
    html += '</table>'
    return html
    

@api_view(['GET'])
@never_cache
def prot(request):
    """
    Try some queries.
    """
    #elapsed = proto.try_queries()
    response = proto.try_queries()

    #return JsonResponse(response, json_dumps_params=dict(indent=4))
    return HttpResponse(proto_html(response['total_time'],
                                   response['query_count'],
                                   response['query_list']))



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['GET'])
def index(request):
    """
    Return the number of reach kind of records.
    """
    ip = get_client_ip(request)
    counts = dict(FitsFile=FitsFile.objects.count(),
                  HDU=Hdu.objects.all().count(),
                  ip=ip,
                  )
    #return JsonResponse(counts)
    return HttpResponse('''<h3>Object Counts</h3>
    <table>
    <tr> <th align="left">FitsFile</th> <td>{FitsFile}</td> </tr>
    <tr> <th align="left">HDU</th> <td>{HDU}</td> </tr>
    <tr> <th align="left">IP</th> <td>{ip}</td> </tr>
    </table>'''.format(**counts))

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def validate_header(hdudictlist):
    """Raise exception if FITS header is not good enuf for Archive.

    INSTRUME and TELESCOP must exist in at least one HDU and have the
    same value in all of them.
    """
    #!!! Insure TELESCOP and INSTRUME have known values (enum)

    def hvalues(k):
        return set([hd.get(k, None) for hd in hdudictlist]) - {None}

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
    

api_extras = [
    'DTPROPID',
    'EXPTIME',
    'FILTER',
    'IMAGETYP',
    'OBSMODE',
    'OBSTYPE',
    'PROCTYPE',
    'PRODTYPE',
    'PROPOSER',
    'SEEING',
    ]
def aggregate_extras_as_list(hdudict_list):
    agg = defaultdict(set)   
    for hdudict in hdudict_list:
        for k in api_extras:
            agg[k].add(hdudict.get(k))
    jagg = dict()
    for k,v in agg.items():
        val = list(v - {None})
        jagg[k] = val if (len(val) > 0) else None

    return jagg

# as single value (='' if none found in HDUs)
def aggregate_extras(hdudict_list):
    agg = dict()
    for k in api_extras:
        for hdudict in hdudict_list:
            if k in hdudict:
                agg[k] = hdudict.get(k)
                continue # got one, ignore rest of HDUs
    return agg
    

def PATCH_store_metadata():
    print('PATCHING: ', end='', flush=True)
    for fobj in FitsFile.objects.all():
        agg = aggregate_extras([hobj.extras for hobj in fobj.hdu_set.all()])
        fobj.extras = agg
        #print('DBG: agg={}'.format(agg))
        fobj.save()
        #print('PATCHED {}'.format(fobj.original_filename))
        print('.', end='', flush=True)
    print('\nDone!')
    
#src_fname, arch_fname, md5sum, size,  
def store_metadata(hdudict_list, vals):
    """Store ALL of the FITS header values into DB."""
    def localize(dateval):
        if dateval == None:
            return None
        else:
            return pytz.utc.localize(dateutil.parser.parse(dateval))

    agg = aggregate_extras(hdudictlist)
    ## FITS File
    fits = FitsFile(md5sum=vals['md5sum'],
                    original_filename=vals['src_fname'],
                    archive_filename=vals['arch_fname'],
                    filesize=vals['size'],
                    release_date=timezone.now(), #!!!
                    instrument=vals['instrument'],
                    telescope=vals['telescope'],
                    date_obs=localize(vals['dateobs'].pop()), #!!!
                    ra=vals['ra'].pop(), #!!!
                    dec=vals['dec'].pop(), #!!!
                    extras = agg
    )
    fits.save()

    notstored = {'SIMPLE', 'COMMENT', 'HISTORY', 'EXTEND', ''} #!
    core = set([ f.name.upper() for f in Hdu._meta.get_fields()])
    for idx,hdudict in enumerate(hdudict_list):
        extras = set(hdudict.keys()) - core - notstored
        #logging.debug('DBG-extras={}'.format(extras))
        extradict = {}
        for k in extras:
            extradict[k] = hdudict[k]
        hduobj = Hdu(fitsfile=fits,
                     hdu_idx=idx,
                     xtension=hdudict.get('XTENSION',''),
                     bitpix=hdudict['BITPIX'],
                     naxis=hdudict['NAXIS'],
                     pcount=hdudict.get('PCOUNT',None),
                     gcount=hdudict.get('GCOUNT',None),
                     instrument=hdudict.get('INSTRUME',''),
                     telescope=hdudict.get('TELESCOP',''),
                     date_obs  = localize(hdudict.get('DATE-OBS',None)),
                     obj = hdudict.get('OBJECT',''),
                     ra = hdudict.get('RA'),
                     dec = hdudict.get('DEC'),
                     extras = extradict
        )
        #!!! Add to naxisN array if appropriate
        hduobj.save()

def hdudictlist(hdulist):
    return [dict(hdu.header.items()) for hdu in hdulist]
                
def handle_uploaded_file(f, md5sum):
    import astropy.io.fits as pyfits
    tgtfile = '/data/upload/foo.fits' #!!!
    with open(tgtfile, 'wb+') as destination:
        hdulist = pyfits.open(f)
        # Validate headers, abort with approriate error if bad for Archive
        valdict = validate_header(hdudictlist(hdulist))

        for chunk in f.chunks():
            destination.write(chunk)
        valdict.update(dict(src_fname = f.name,
                            arch_fname = tgtfile,
                            md5sum = md5sum,
                            size = f.size))
        store_metadata(hdudictlist(hdulist),valdict)
    
#@csrf_exempt
@api_view(['POST'])
def ingest(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'],  request.data['md5sum'])

    return JsonResponse(dict(result='file uploaded: {}'
                             .format(request.FILES['file'].name)))

search_fields = set([
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
    #'xtension', # new
    'extras',
])

def wrap(qdict):
    return dict(search=qdict)


@api_view(['POST'])
def search2(request):
    """
    Search Archive, returns FITS metadata (header field/values).
    """
    if request.method != 'POST':
        raise Exception('Only accepts POST http method')
    ct = "application/x-www-form-urlencoded"
    if request.content_type !=  ct :
        raise Exception("Only accepts content_type = {}. Got '{}'"
                        .format(ct, request.content_type))
    formdict = request.POST
    logging.debug('search2-formdict={}'.format(formdict))    
    jsearch = dict()
    for k in formdict.keys():
        if len(formdict[k]) == 0:
            continue
        if k in search_fields:
            jsearch[k] = formdict[k]
        
    logging.debug('search2-jsearch={}'.format(jsearch))
    #!return JsonResponse(formdict)
    c = Client()
    return c.post('/natica/search/',
                      content_type='application/json',
                      data=json.dumps(wrap(jsearch)))


#curl -H "Content-Type: application/json" -X POST -d @natica/fixtures/request-search-1.json http://localhost:8000/natica/search/ | python -m json.tool
@api_view(['POST'])
def search(request):
    """
    Search Archive, returns FITS metadata (header field/values).
    """
    if request.method != 'POST':
        raise Exception('Only accepts POST http method')
    if request.content_type != "application/json" :
        raise Exception("Only accepts content_type = application/json. Got '{}'"
                        .format(request.content_type))

    page_limit = int(request.GET.get('limit','100')) # num of records per page
    page = int(request.GET.get('page','1'))
    offset = (page-1) * page_limit
    # order:: comma delimitied, leading +/-  (ascending/descending)
    order_fields = request.GET.get('order','original_filename')

    
    body = json.loads(request.body.decode('utf-8'))
    jsearch = body['search']
    logging.debug('search-jsearch={}'.format(jsearch))

    #!!! add validation against schema

    used_fields = set(jsearch.keys())
    if not (search_fields >= used_fields):
        unavail = used_fields - search_fields
        raise nex.ExtraSearchFieldError('Extra fields ({}) in search'
                                     .format(unavail))
    assert(search_fields >= used_fields)

    # Construct query (anchored on FitsFile)
    slop = jsearch.get('search_box_min', .001)
    q = (sf.coordinates(jsearch.get('coordinates', None), slop)
         & sf.exposure_time(jsearch.get('exposure_time', None))
         & sf.filename(jsearch.get('filename', None))
         & sf.image_filter(jsearch.get('image_filter', None))
         & sf.obs_date(jsearch.get('obs_date', None))
         & sf.original_filename(jsearch.get('original_filename', None))
         & sf.pi(jsearch.get('pi', None))
         & sf.prop_id(jsearch.get('propid', None))
         & sf.release_date(jsearch.get('release_date', None))
         & sf.telescope_instrument(jsearch.get('telescope_instrument', None))
         #& sf.xtension(jsearch.get('xtension', None))

         & sf.extras(jsearch.get('extras', None))
         )
    #logging.debug('DBG: q={}'.format(str(q)))
    #fullqs = FitsFile.objects.filter(q).distinct().order_by(order_fields)
    fullqs = FitsFile.objects.filter(q).order_by(order_fields)
    query = str(fullqs.query)
    total_count = len(fullqs) #.count()   tot seconds: 2.8
    #total_count = fullqs.count() #       tot seconds: 4.9
    qs = fullqs[offset:page_limit]
    results = [dict(
        ra=fobj.ra,
        dec=fobj.dec,
        #depth,
        exposure=fobj.extras.get('EXPTIME'),
        filename=fobj.archive_filename,
        filesize=fobj.filesize,
        filter=fobj.extras.get('FILTER'), # FILTER, FILTERS, FILTER1, FILTER2
        image_type=fobj.extras.get('IMAGETYP'), 
        instrument=fobj.instrument,
        md5sum=fobj.md5sum,
        obs_date=fobj.date_obs,
        observation_mode=fobj.extras.get('OBSMODE'),
        observation_type=fobj.extras.get('OBSTYPE'), 
        original_filename=fobj.original_filename,
        pi=fobj.extras.get('PROPOSER'),
        product=fobj.extras.get('PRODTYPE'),
        prop_id=fobj.extras.get('DTPROPID'),
        release_date=fobj.release_date,
        seeing=fobj.extras.get('SEEING'),
        #survey_id
        telescope=fobj.telescope,
    ) for fobj in qs]
        
  
    meta = OrderedDict.fromkeys(['total_count',
                                 'page_result_count',
                                 'to_here_count',
                                 'api_version',
                                 'timestamp',
                                 'comment',
                                 'query', ])
    meta.update(
        api_version = api_version,
        timestamp = datetime.datetime.now(),
        comment = ('WARNING: RESULTS missing values: surve_id, depth.'
                   '  (Where do they come from???)'
                   ),
        query = query,
        page_result_count = len(results),
        to_here_count = offset + len(results),
        total_count = total_count,
    )
    #logging.debug('DBG: query={}'.format(qs.query))
    return JsonResponse(OrderedDict(meta=meta, results=results))
                        
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
    
def query(request):
   # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()

    return render(request, 'search.html', {'form': form})    
