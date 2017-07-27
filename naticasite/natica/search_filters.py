from django.db.models import Q

proc_LUT = dict(raw = 'raw',
                calibrated = 'InstCal',
                reprojected = 'projected',
                stacked = 'stacked',
                master_calibration = 'mastercal',
                image_tiles = 'tiled',
                sky_subtracted = 'skysub')

def coordinates(val, slop):
    if val == None: return Q()
    ra = val['ra']
    dec = val['dec']
    return (
        Q(dec__lte=(dec + slop))
        & Q(dec__gte=(dec - slop))
        & Q(ra__lte=(ra + slop))
        & Q(ra__gte=(ra - slop))
        )

def pi(val):
    if val == None: return Q()
    #return Q(pi=val)
    return Q(hdu__extras__PROPOSER=val)

def prop_id(val):
    return Q() # !!! DISABLED
    if val == None: return Q()
    return Q(propid=val)

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def dateobs(val):
    if val == None: return Q()
    if isinstance(val, list):
        mindate,maxdate,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(date_obs__range=(mindate, maxdate))
    else:
        return Q(date_obs=val)
obs_date = dateobs

def archive_filename(val):
    if val == None: return Q()
    return Q(archive_filename=val)
filename=archive_filename


def original_filename(val):
    if val == None: return Q()
    return Q(original_filename=val)

def telescope_instrument(val):
    if val == None: return Q()
    tele_list,inst_list = zip(*val)
    return (Q(telescope__in=tele_list)
            & Q(instrument__in=inst_list) )

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def release_date(val):
    if val == None: return Q()
    if isinstance(val, list):
        mindate,maxdate,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(release_date__range=(mindate, maxdate))
    else:
        return Q(release_date=val)
    
def flag_raw(val):
    if val == None: return Q()
    return Q(hdu__extras__PROCTYPE='raw')

def image_filter(val):
    if val == None: return Q()
    # Case insensitive match against extras['PRODTYPE'] (json field)
    return Q(hdu__extras__PRODTYPE__iexact='image')

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def exposure_time(val):
    if val == None: return Q()
    if isinstance(val, list):
        minval,maxval,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(hdu__extras__EXPTIME__range=(minval, maxval))
    else:
        return Q(hdu__extras__EXPTIME=val)
    
def extras(val):
    if val == None: return Q()
    return Q(**val) 

# All PROCTYPE values
# [e['extras']['PROCTYPE'] for e in Hdu.objects.filter(extras__has_key='PROCTYPE').values('extras')]
