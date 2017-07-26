#! /usr/bin/env python
# EXAMPLES:
# find /data/tada-test-data \( -name "*.fits" -o -name "*.fits.fz" \) -print0 | xargs -0 python3 natica/scrape_fits.py -r /data/tada-test-data/ -d /data/json

import sys
import argparse
import logging
import json
from pathlib import Path,PurePath

import astropy.io.fits as pyfits

def hdudictlist(hdulist):
    return [dict(hdu.header.items()) for hdu in hdulist]

def scrape_file(fitsfile, outdir, rootdir):
    """The work-horse function."""
    fitspath = Path.expanduser(Path(fitsfile))
    if rootdir == None:
        rootdir = fitspath.parent
    hdulist = pyfits.open(fitsfile)
    hdudict_list = hdudictlist(hdulist)
    hdulist.close()
    fitsjson = list()
    for idx,hdudict in enumerate(hdudict_list):
        hdudict['hduidx']=idx
        fitsjson.append(hdudict)

    tgtfile = Path(outdir, fitspath.relative_to(rootdir).with_suffix('.json'))
    tgtfile.parent.mkdir(parents=True, exist_ok=True)
    with open(str(tgtfile), 'w') as fout:
        json.dump(fitsjson, fout, indent=4)
    print('Created {}'.format(str(tgtfile)))
    
##############################################################################

def user_path(string):
    return Path.expanduser(Path(string))

def main():
    "Parse command line arguments and do the work."
    default_dest_dir = '~/scrape-data/'
    parser = argparse.ArgumentParser(
        description='My shiny new python program',
        epilog='EXAMPLE: %(prog)s a b"'
        )
    parser.add_argument('--version', action='version', version='1.0.1')
    parser.add_argument('fits', nargs='+',
                        help='Path to FITS file to scrape header from' )

    parser.add_argument('-d', '--dest_dir', type=user_path,
                        default=default_dest_dir,
                        help='Directory to write files to. [dft {}]'
                        .format(default_dest_dir))
    parser.add_argument('-r', '--root_dir', type=user_path,
                        help='Source dir to treat as root when duplicating tree'
                        )
    parser.add_argument('--loglevel',
                        help='Kind of diagnostic output',
                        choices=['CRTICAL', 'ERROR', 'WARNING',
                                 'INFO', 'DEBUG'],
                        default='WARNING')
    args = parser.parse_args()

    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        parser.error('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=log_level,
                        format='%(levelname)s %(message)s',
                        datefmt='%m-%d %H:%M')
    logging.debug('Debug output is enabled in %s !!!', sys.argv[0])

    for fits in args.fits:
        scrape_file(fits, args.dest_dir, args.root_dir)

if __name__ == '__main__':
    main()

