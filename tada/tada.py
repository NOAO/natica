"""New TADA to use within NATICA prototype. Uses new Ingest service.
Validate input FITS (valid per TADA pre-personality). 
Copy valid FITS to cache. 
Apply personality to FITS in cache.
Ingest into Archive via web-service.
Remove cache FITS on success, else move to anticache.
"""

import sys
import argparse
import logging
import shutil
import os
import magic
import yaml
import hashlib
from pathlib import PurePath
import astropy.io.fits as pyfits
import requests
import settings
import errno

import exceptions as tex

##############################################################################

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: 
        if e.errno != errno.ENOENT: 
            raise # re-raise exception if a different error occurred

def force_move(src_file, dest_dir):
    dest_file = str(PurePath(dest_dir,PurePath(src_file).name))
    silentremove(dest_file)
    shutil.move(src_file, dest_file)

def force_copy(src_file, dest_dir):
    dest_file = str(PurePath(dest_dir,PurePath(src_file).name))
    silentremove(dest_file)
    shutil.copyfile(src_file, dest_file)
        
# +++ Add code here if TADA needs to handle additional types of files!!!
def file_type(filename):
    """Return an abstracted file type string.  MIME isn't always good enough."""
    type = 'UNKNOWN'
    if magic.from_file(filename).find('FITS image data') >= 0:
        type = 'FITS'
    elif magic.from_file(filename).find('JPEG image data') >= 0:
        type = 'JPEG'
    elif magic.from_file(filename).find('script text executable') >= 0:
        type = 'shell script'
    return type


def hdudictlist(fitsfile):
    hdulist = pyfits.open(fitsfile)
    for hdu in hdulist:
        hdu.verify('fix')
    return [collections.OrderedDict(hdu.header.items()) for hdu in hdulist]

##############################################################################

def validate_original_fits(fitsfilepath):
    """Raise exception if we can tell that FITSFILEPATH does not represent a 
FITS file that is valid to ingest into Archive."""
    assert 'FITS' == file_type(fitsfilepath)

def apply_personality(srcfits, destfits, pers_file):
    """Use personality file in FITS dir to modify FITS hdr in place."""
    # get Personality DICT
    # validate personality file (wrt JSON schema), raise if invalid
    with open(pers_file) as yy:
        # raise if yaml doesn't exist
        yd = yaml.safe_load(yy)

    #origfname = yd['params']['filename']
    # Apply personality changes
    hdulist = pyfits.open(srcfits)
    newhdr = hdulist[0].header
    changed = set()
    for k,v in yd['options'].items():
        logging.debug('apply_personality {}={}'.format(k,v))
        newhdr[k] = v  # overwrite with explicit fields from personality
        changed.add(k)
    #!hdulist.close(output_verify='fix')
    silentremove(destfits)
    hdulist.writeto(destfits, output_verify='fix')
    logging.debug('Applied personality file ({}) to {}'
                  .format(pers_file, destfits))
    return changed

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

        
def http_archive_ingest(modifiedfits, overwrite=False):
    """Deliver FITS to NATICA webservice for ingest."""
    f = open(modifiedfits, 'rb')
    #urls = 'http://0.0.0.0:8000/natica/store/'
    urls = settings.natica_ingest_url
    r = requests.post(urls,
                      params=dict(overwrite=13) if overwrite else dict(),
                      data=dict(md5sum=md5(modifiedfits)),
                      files={'file':f})
    logging.debug('http_archive_ingest: {}, {}'.format(r.status_code,r.json()))
    return (r.status_code, r.json())




def submit_to_archive(fitspath,
                      md5sum=None,
                      overwrite=False,
                      personality_yaml=None,
                      cachedir='/var/tada/cache',
                      anticachedir='/var/tada/anticache'):
    """Ingest a FITS file into the archive if possible.  Involves renaming to 
satisfy filename standards. 

fitspath:: full path of original fits file (in cache). There must be a 
    personality file in <fitspath>.yaml to be used to modify FITS.

md5sum:: checksum of original file from dome
    """
    validate_original_fits(fitspath) # raise on invalid
    if md5sum == None:
        md5sum = md5(fitspath)
    fitscache = str(PurePath(cachedir,
                             md5sum + ''.join(PurePath(fitspath).suffixes)))
    #!shutil.copyfile(fitspath, fitscache)

    # Apply personality to FITS in-place (roughly "prep_for_ingest")
    if personality_yaml == None:
        personality_yaml = fitspath+'.yaml'
    #!pers_file = str(PurePath(cachedir,
    #!                          md5sum
    #!                          + ''.join(PurePath(fitspath).suffixes)
    #!                          + '.yaml'))
    #!shutil.copyfile(fitspath+'.yaml', pers_file)
    #! changed = apply_personality(fitspath, pers_file)
    changed = apply_personality(fitspath, fitscache, personality_yaml)

    # ingest NATICA service
    (status,jmsg) = http_archive_ingest(fitscache, overwrite=overwrite)
    
    if status == 200:  # SUCCESS
        # Remove cache files; FITS + YAML
        os.remove(fitscache) 
        #!os.remove(pers_file)
        logging.debug('Ingest SUCCESS: {}; {}'.format(fitspath, jmsg))
    else:  # FAILURE
        logging.error('Ingest FAIL: {} ({}); {}'
                      .format(fitspath, fitscache, jmsg))

        # move FITS + YAML on failure
        force_copy(personality_yaml, anticachedir)
        force_move(fitscache, anticachedir)
        msg = ('Failed to ingest using natica/store webservice with {}; {}'
               .format(fitscache, jmsg))
        #raise tex.WebServiceException(msg)
        return msg


    # !!! update AUDIT record. At-rest in Archive(success), or Anti-cache(fail)

    return jmsg.get('archive_filename', 'NA')
    # END: submit_to_archive()
    
def submit(rec, qname):
    """ACTION against item from dataqueue"""
    ok = False
    fitsfile = rec['filename']
    md5sum = rec['checksum']
    print('settings.n_url={}'.format(settings.natica_ingest_url))
    try:
        submit_to_archive(fitsfile)
    except Exception as err:
        msg = ('ERROR: file ({}) not ingested; {}'.format(fitsfile, std(err)))
        logging.error(msg)
        ok = False
    return ok


##############################################################################

# On archive:
# cd /sandbox/natica/tada
# testfile=/data/tada-test-data/short-drop/20141220/wiyn-whirc/obj_355.fits.fz
# python3 tada.py $testfile
testfile='/data/tada-test-data/short-drop/20141220/wiyn-whirc/obj_355.fits.fz'
def main():
    "Parse command line arguments and do the work."
    #!print('EXECUTING: %s\n\n' % (' '.join(sys.argv)))
    parser = argparse.ArgumentParser(
        description='Apply personality modification to FITS. Ingest with NATICA',
        epilog='EXAMPLE: %(prog)s  --loglevel DEBUG {}'.format(testfile),
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument('--version', action='version', version='1.0.1')
    parser.add_argument('fitsfile', type=argparse.FileType('r'),
                        help='FITS file to ingest into Archive')
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='Overwrite file if it already exists in archive')

    parser.add_argument('--loglevel',
                        help='Kind of diagnostic output',
                        choices=['CRTICAL', 'ERROR', 'WARNING',
                                 'INFO', 'DEBUG'],
                        default='WARNING')
    args = parser.parse_args()
    args.fitsfile.close()
    args.fitsfile = args.fitsfile.name

    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        parser.error('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=log_level,
                        format='%(levelname)s %(message)s',
                        datefmt='%m-%d %H:%M')
    logging.debug('Debug output is enabled in %s !!!', sys.argv[0])

    print(submit_to_archive(args.fitsfile, overwrite=args.overwrite))

if __name__ == '__main__':
    main()
