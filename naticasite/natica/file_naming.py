import datetime as dt
from pathlib import PurePath 
from . import settings

def fits_extension(fname):
    '''Return extension of any file matching <basename>.fits.*, basename.fits
Extension may be: ".fits.fz", ".fits", ".fits.gz", etc'''
    _, ext = os.path.splitext(fname)
    if ext != '.fits':
        _, e2  = os.path.splitext(_)
        ext = e2 + ext
    return ext[1:]

def generate_archive_path(hdr, ext='.fits.fz', tag=None):
    site = hdr.get('DTSITE','nota').lower()
    telescope = hdr.get('DTTELESC','nota').lower()
    instrument = hdr.get('DTINSTRU','nota').lower()
    obstype = hdr.get('OBSTYPE', 'nota').lower()
    proctype = hdr.get('PROCTYPE', 'nota').lower()
    prodtype = hdr.get('PRODTYPE', 'nota').lower()
    serno = hdr.get('DTSERNO')
    # e.g. DATEOBS='2002-12-25T00:00:00.000001'
    obsdt = dt.datetime.strptime(hdr.get('DATE-OBS','NA'),
                                 '%Y-%m-%dT%H:%M:%S.%f')
    date = obsdt.date().strftime('%y%m%d')
    time = obsdt.time().strftime('%H%M%S')

    flavor = ''
    if serno != None:
        flavor += '_s{serno}'
    if (tag != None) and (tag != ''):
        flavor += '_t{tag}'


    fnfields = dict(
        prefix=settings.stiLUT.get((site, telescope, instrument), 'uuuu'),
        date=date,
        time=time,
        obstype=settings.obsLUT.get(obstype, 'u'),  # if not in LUT, use "u"!!!
        proctype=settings.procLUT.get(proctype,'u'),
        prodtype=settings.prodLUT.get(prodtype,'u'),
        flavor=flavor, # optional (may be null string)
        ext=ext,
        )

    std='{prefix}_{date}_{time}_{obstype}{proctype}{prodtype}{flavor}{ext}'
    basename=std.format(**fnfields)
    archive_path = PurePath(settings.archive_root,
                            hdr['DTCALDAT'].replace('-',''),
                            hdr['DTTELESC'],
                            hdr['DTPROPID'],
                            basename)
    return archive_path
             
