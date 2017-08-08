# Loads DB from FITS files headers (extracted on the fly).
from django.core.management.base import BaseCommand, CommandError
from natica.views import submit_fits_file

# EXAMPLES:
#   python3 manage.py ingest_fits /data/tada-test-data/basic/kp109391.fits.fz /data/tada-test-data/drop-test/20160314/kp4m-mosaic3/mos3.75870.fits.fz
#
# pass 47/53 files:
#   find /data/tada-test-data \( -name "*.fits" -o -name "*.fits.fz" \) -print0 | xargs -0 python3 manage.py ingest_fits
#
# Failed files (17):
# python3 manage.py ingest_fits /data/tada-test-data/drop-test/20160314/kp4m-mosaic3/mos3.75756.fits /data/tada-test-data/basic/cleaned-bok.fits.fz /data/tada-test-data/scrape/20151007/ct4m-decam/DECam_00482540.fits.fz /data/tada-test-data/basic/obj_355.fits.fz /data/tada-test-data/short-drop/bad-date/wiyn-whirc/obj_355a.fits.fz /data/tada-test-data/scrape/20141224/kp09m-hdi/c7015t0267b00.fits.fz /data/tada-test-data/drop-test/20160314/kp4m-mosaic3/mos3.75763.fits /data/tada-test-data/basic/c4d_130901_031805_oow_g_d2.fits.fz /data/tada-test-data/drop-test/20160314/kp4m-mosaic3/mos3.75675.fits /data/tada-test-data/fitsverify/fail-fail.fits.fz /data/tada-test-data/fitsverify/pass-pass.fits.fz /data/tada-test-data/short-drop/20160909/bad-instrum/obj_355b.fits.fz /data/tada-test-data/drop-test/20160314/kp4m-mosaic3/mos3.75870.fits.fz /data/tada-test-data/short-drop/20141220/wiyn-whirc/obj_355.fits.fz /data/tada-test-data/scrape/20150709/bok23m-90prime/d7212.0062.fits.fz /data/tada-test-data/fitsverify/fail-pass.fits.fz /data/tada-test-data/basic/obj_355_VR_v1_TADAPIPE.fits.fz

class Command(BaseCommand):
    help = 'Uploads a FITS file and adds all its metadata to the DB.'

    def add_arguments(self, parser):
        parser.add_argument('fits', nargs='+',
                            help='Path to FITS file to ingest into NATICA' )


    def handle(self, *args, **options):
        error = False
        badfits = set()
        goodfits = set()
        for fits in options['fits']:
            self.stdout.write('Ingest {}: '.format(fits), ending='')
            try:
                submit_fits_file(fits)
            except Exception as err:
                self.stdout.write(self.style.ERROR(err))
                error = True
                badfits.add(fits)
                #raise CommandError('Failed ingest of "{}"'.format(fits))
                continue
            goodfits.add(fits)
            self.stdout.write(self.style.SUCCESS('OK'))

        total = len(options['fits'])
        if len(goodfits) > 0:
            self.stdout.write(self.style.SUCCESS(
                'Successfully ingested {}/{} files: {}'
                .format(len(goodfits), total, ' '.join(goodfits))))
        if error:
            raise CommandError('Failed ingest of {}/{} files: "{}"'
                               .format(len(badfits),total, ' '.join(badfits)))




