
import json
from os import path
import coreapi
import jsonschema
from django.db import connections
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework import response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from tada.models import FilePrefix
from astropy.coordinates import SkyCoord

from . import exceptions as dex
from . import utils
from .serializers import FilePrefixSerializer

dal_version = '0.1.7' # MVP. mostly untested

utils.dal_version = dal_version

#    object as object_name,          -- object_name
COMMENTED_response_fields = '''
    reference,
    ra,
    dec,
    prop_id,
    surveyid as survey_id,          -- survey_id
    date_obs as obs_date,           -- obs_date
    dtpi as pi,                     -- pi
    telescope,
    instrument,
    release_date,
    rawfile as flag_raw,            -- flag_raw ???
    proctype,
    filter,
    filesize,
    filename,
    dtacqnam as original_filename,  -- original_filename
    md5sum,
    exposure,
    obstype as observation_type,    -- observation_type
    obsmode as observation_mode,    -- observation_mode
    prodtype as product,            -- product ???
    proctype,
    seeing,
    depth
'''


def fake_error_response(request, error_type):
    fake_err_types = ['bad_numeric',
                      'bad_search_json',
    ]
    if error_type == 'bad_numeric':
        raise dex.BadNumeric('Bad numeric value')
    elif error_type == 'bad_search_json':
        raise dex.BadSearchSyntax('Invalid JSON for search. Bad syntax.')
    else:
        raise dex.BadFakeError(
            'Unknown value ({}) for URL ERROR parameter. Allowed: {}'
            .format(error_type, ','.join(fake_err_types)))



## Under PSQL, copy SELECTed results to CSV using:
#
# \copy (SELECT * from voi.siap WHERE (ra <= 186.368791666667) AND (ra >= 176.368791666667) AND (dec <= -40.5396111111111) AND (dec >= -50.5396111111111) AND (dtpi = 'Cypriano') AND (dtpropid = 'noao') AND ('[2009-04-01,2009-04-03]'::tsrange @> date_obs::timestamp) AND (dtacqnam = '/ua84/mosaic/tflagana/3103/stdr1_012.fits') AND ((telescope = 'ct4m') OR (telescope = 'foobar')) AND ((instrument = 'mosaic_2')) AND (release_date = '2010-10-01T00:00:00') AND ((proctype = 'raw') OR (proctype = 'InstCal')) AND (exposure = '15')) TO '~/data/metadata-dal-2.csv'

# curl -H "Content-Type: application/json" -X POST -d @fixtures/search-sample.json http://localhost:8000/dal/search/ > ~/response.json
# curl -H "Content-Type: application/json" -X POST -d @request.json http://localhost:8000/dal/search/ | python -m json.tool

@api_view(['POST'])
@require_http_methods(["POST"])
def search_by_json(request, query=None): # @Portal
    """
    Search the NOAO Archive, returns a list of image resource metadata  (header field/values).

    **Context**

    ``query``
        Payload satisfying /etc/mars/search-schema.json .
    """
    if request.content_type != "application/json" :
        raise Exception("Only accepts content_type = application/json. Got '{}'"
                        .format(request.content_type))
    logging.debug('DBG-1 search.request.body={}'.format(request.body))
    page_limit = int(request.GET.get('limit','100')) # num of records per page
    page = int(request.GET.get('page','1'))
    offset = (page-1) * page_limit
    # order:: comma delimitied, leading +/-  (ascending/descending)
    order_fields = request.GET.get('order','original_filename')
    jsearch = json.loads(request.body.decode('utf-8'))
    logging.debug('DBG jsearch={}'.format(jsearch))

    # Validate against schema
    try:
        schemafile = '/etc/natica/search-schema.json'
        with open(schemafile) as f:
            schema = json.load(f)
            jsonschema.validate(jsearch, schema)
    except Exception as err:
        raise nex.SearchSyntaxError('JSON did not validate against'
                                    ' {}; {}'.format(schemafile, err))


    used_fields = set(jsearch.keys())
    if not (search_fields >= used_fields):
        unavail = used_fields - search_fields
        raise nex.ExtraSearchFieldError('Extra fields ({}) in search'
                                     .format(unavail))
    assert(search_fields >= used_fields)

    q = make_qobj(jsearch)

    #fullqs = FitsFile.objects.filter(q).distinct().order_by(order_fields)
    fullqs = FitsFile.objects.filter(q)
    #total_count = len(fullqs) #.count()   tot seconds: 2.8
    total_count = fullqs.count() #       tot seconds: 4.9
    logging.debug('DBG: do query')
    try:
        qs = fullqs.order_by(order_fields)[offset:page_limit]
    except Exception as err:
        return JsonResponse(dict(error='query failed: {}'.format(err)))
    query = str(qs.query)
    logging.debug('DBG: query={}'.format(query))

    results = list()
    #!for fobj in qs.iterator():
    for fobj in qs:
        logging.debug('DBG: fobj.md5sum={}, instrum={}'.format(fobj.md5sum, fobj.instrument))
        ra = [fobj.ra.lower, fobj.ra.upper] if fobj.ra != None else None
        dec = [fobj.dec.lower, fobj.dec.upper] if fobj.dec != None else None
        exposure = [fobj.exposure.lower, fobj.exposure.upper] if fobj.exposure != None else None
        obsdate = [fobj.date_obs.lower, fobj.date_obs.upper] if fobj.date_obs != None else None
        results.append(
            dict(
                id=fobj.id,
                ra=ra,
                dec=dec,
                #depth,
                exposure=exposure,
                filename=fobj.archive_filename,
                filesize=fobj.filesize,
                filter=fobj.extras.get('FILTER'), # FILTER, FILTERS, FILTER1, FILTER2
                image_type=fobj.extras.get('IMAGETYP'), 
                instrument=fobj.instrument.name,
                md5sum=fobj.md5sum,
                obs_date=obsdate,
                observation_mode=fobj.extras.get('OBSMODE'),
                observation_type=fobj.extras.get('OBSTYPE'), 
                original_filename=fobj.original_filename,
                pi=fobj.extras.get('PROPOSER'),
                product=fobj.extras.get('PRODTYPE'),
                prop_id=fobj.extras.get('DTPROPID'),
                release_date=fobj.release_date,
                seeing=fobj.extras.get('SEEING'),
                #survey_id
                telescope=fobj.telescope.name,
            ))
    logging.debug('DBG: results={}'.format(results))
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
        comment = ('WARNING: RESULTS missing values: surver_id, depth.'
                   '  (Where do they come from???)'
                   ),
        query = query,
        page_result_count = len(results),
        to_here_count = offset + len(results),
        total_count = total_count,
        offset = offset,
        page_limit = page_limit,
        debug=1
    )
    #logging.debug('DBG: query={}'.format(qs.query))
    jresponse = OrderedDict(meta=meta, resultset=results)
    #!logging.debug('DBG: jresponse={}'.format(jresponse)) # BIG
    return JsonResponse(jresponse)
                        


@csrf_exempt
@api_view(['GET'])
def tele_inst_pairs(request):  # # @Portal
    """
    Retrieve all valid telescope/instrument pairs.
    Determined by TADA file prefix table.

    Response will be an array of **telescope**, **instrument** pairs

    `[ [\"telescope1\", \"instrument1\"], [\"telescope2\", \"instrument2\"] ]`
    """
    qs = FilePrefix.objects.all().order_by('pk').values('telescope',
                                                        'instrument')
    serialized = FilePrefixSerializer(qs, many=True)
    return JsonResponse([(d['telescope'],d['instrument']) for d in list(serialized.data)],
                         safe=False)


@csrf_exempt
def get_categories_for_query(request):  # @Portal
    """
    Get a list of unique values for the following columns:
    Proposal Id, Survey Id, PI, Telescope, instrument, filter, observation type,
    observation mode, processing, product
    """
    # get uniques for filters
    query = json.loads(request.body.decode('utf-8'))
    cursor = connections['archive'].cursor()
    category_fields = [
        "prop_id",
        "surveyid as survey_id",
        "dtpi as pi",
        "concat(telescope, ',', instrument) as telescope_instrument",
        "filter",
        "obstype as observation_type",
        "obsmode as observation_mode",
        "prodtype as product",
        "proctype as processing"
    ]

    where_clause = utils.process_query(jsearch=query, page=1, page_limit=50000, order_fields='', return_where_clause=True)
    categories = {}
    for category in category_fields:
        indx = category.split(" as ").pop()
        sql1 = ('SELECT {}, count(*) as total  FROM voi.siap {} group by {}'.format(category, where_clause, indx))
        cursor.execute(sql1)
        categories[indx] = utils.dictfetchall(cursor)

    resp = {"status":"success", "categories":categories}
    return JsonResponse(resp, safe=False)


@csrf_exempt
@api_view(['GET'])
def object_lookup(request): # @Portal
    """
    Retrieve the RA,DEC coordinates for a given object by name.
    """
    obj_name = request.GET.get("object_name", "")
    obj_coord = SkyCoord.from_name(obj_name)
    return JsonResponse({'ra':obj_coord.ra.degree, 'dec':obj_coord.dec.degree})


###
# API Schema Metadata
schema = coreapi.Document(
    title="Search API",
    url="http://localhost:8000",

    content={
        "search": coreapi.Link(
            url="/dal/search/",
            action = "post",
            fields = [
                coreapi.Field(
                    name="obs_date",
                    required=False,
                    location="form",
                    description="Single date or date range"
                ),
                coreapi.Field(
                    name="prop_id",
                    required=False,
                    location="form",
                    description="Prop ID to search for"
                ),
                coreapi.Field(
                    name="pi",
                    required=False,
                    location="form",
                    description="Principle Investigator"
                ),
                coreapi.Field(
                    name="filename",
                    required="false",
                    location="form",
                    description="Ingested archival filename"
                )
            ],
            description='''
            NOAO Search API

Requests need to be wrapped in a root `search` paramater

            {
              \"search\":{
                 \"obs_date\":\"2015-09-06\"
              }
            }
            '''
        )
    }
)

@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer])
def schema_view(request):
    '''
      Search API
    '''
    return response.Response(schema)
