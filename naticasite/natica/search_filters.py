from django.db.models import Q
from psycopg2.extras import NumericRange, DateRange

##############################################################################
### for LSA API
### These are ALL the fields that can be queried against using the Portal
def coordinates(val, slop):
    if val == None: return Q()
    ra = val['ra']
    dec = val['dec']
    #!return ( Q(dec__lte=(dec + slop)) & Q(dec__gte=(dec - slop))
    #!    & Q(ra__lte=(ra + slop)) & Q(ra__gte=(ra - slop))       )
    qq = Q(dec__overlap=NumericRange(dec-slop, dec+slop)) \
         & Q(ra__overlap=NumericRange(ra-slop, ra+slop))
    return qq
            
              

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def exposure_time(val):
    if val == None: return Q()
    if isinstance(val, list):
        minval,maxval,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(exposure__overlap=NumericRange(minval, maxval, bounds='[]'))
    else:
        return Q(exposure__overlap=NumericRange(val, val, bounds='[]'))

def archive_filename(val):
    if val == None: return Q()
    return Q(archive_filename=val)
filename=archive_filename

def image_filter(val):  
    if val == None: return Q()
    # Case insensitive match against extras['PRODTYPE'] (json field)
    return Q(extras__PRODTYPE__iexact='image') #!!!

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def dateobs(val):
    if val == None: return Q()
    if isinstance(val, list):
        mindate,maxdate,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(date_obs__overlap=DateRange(mindate, maxdate))
    else:
        return Q(date_obs__overlap=DateRange(val,val))
obs_date = dateobs     

def original_filename(val):
    if val == None: return Q()
    return Q(original_filename=val)

def pi(val):
    if val == None: return Q()
    #return Q(extras__PROPOSER=val)
    return Q(proposal__pi=val)

def prop_id(val):
    if val == None: return Q()
    #return Q(extras__DTPROPID=val)
    return Q(proposal__prop_id=val)

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def release_date(val):
    if val == None: return Q()
    if isinstance(val, list):
        mindate,maxdate,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(release_date__range=(mindate, maxdate))
    else:
        return Q(release_date=val)

def telescope_instrument(val):
    if val == None: return Q()
    tele_list,inst_list = zip(*val)
    return (Q(telescope__in=tele_list) & Q(instrument__in=inst_list) )

##############################################################################
    

#!def xtension(val):
#!    if val == None: return Q()
#!    return Q(xtension=val)

def extras(val):
    if val == None: return Q()
    return Q(**val) 

# All PROCTYPE values
# [e['extras']['PROCTYPE'] for e in Hdu.objects.filter(extras__has_key='PROCTYPE').values('extras')]

proc_LUT = dict(raw = 'raw',
                calibrated = 'InstCal',
                reprojected = 'projected',
                stacked = 'stacked',
                master_calibration = 'mastercal',
                image_tiles = 'tiled',
                sky_subtracted = 'skysub')
