from django.db.models import Q

def coordinates(val, slop):
    if val == None: return Q()
    ra = val['ra']
    dec = val['dec']
    return (
        Q(primaryhdu__dec__lte=(dec + slop))
        & Q(primaryhdu__dec__gte=(dec - slop))
        & Q(primaryhdu__ra__lte=(ra + slop))
        & Q(primaryhdu__ra__gte=(ra - slop))
        )

def pi(val):
    return Q() # !!! DISABLED
    if val == None: return Q()
    return Q(pi=val)

def propid(val):
    return Q() # !!! DISABLED
    if val == None: return Q()
    return Q(propid=val)

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def dateobs(val):
    if val == None: return Q()
    if isinstance(val, list):
        mindate,maxdate,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(primaryhdu__date_obs__range=(mindate, maxdate))
    else:
        return Q(primaryhdu__date_obs=val)

def archive_filename(val):
    if val == None: return Q()
    return Q(archive_filename=val)

def original_filename(val):
    if val == None: return Q()
    return Q(original_filename=val)

def telescope_instrument(val):
    if val == None: return Q()
    tele_list,inst_list = zip(*val)
    return (Q(primaryhdu__telescope__in=tele_list)
            & Q(primaryhdu__instrument__in=inst_list) )

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def release_date(val):
    return Q() # !!! DISABLED
    if val == None: return Q()
    if isinstance(val, list):
        mindate,maxdate,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(release_date__range=(mindate, maxdate))
    else:
        return Q(release_date=val)
    
def flag_raw(val):
    return Q() # !!! DISABLED
    if val == None: return Q()
    return Q(rawfile=val)

def image_filter(val):
    return Q() # !!! DISABLED
    if val == None: return Q()
    proc_LUT = dict(raw = 'raw',
                    calibrated = 'InstCal',
                    reprojected = 'projected',
                    stacked = 'stacked',
                    master_calibration = 'mastercal',
                    image_tiles = 'tiled',
                    sky_subtracted = 'skysub')
    return Q(proctype__in=[proc_LUT[p] for p in val])

#!!! WARNING: this is Inclusive only (ignores the BOUNDS part of tuple)
def exposure_time(val):
    return Q() # !!! DISABLED
    if val == None: return Q()
    if isinstance(val, list):
        minval,maxval,*xtra = val
        # bounds = xtra[0] if (len(xtra) > 0) else '[)'  
        return Q(exposure__range=(minval, maxval))
    else:
        return Q(exposure=val)
    
