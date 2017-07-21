from django.core.management.base import BaseCommand, CommandError
from natica.models import FitsFile, PrimaryHDU, ExtensionHDU
from natica.views import submit_fits_file

# EXAMPLES:
#   python3 manage.py ingest_fits /data/tada-test-data/basic/kp109391.fits.fz /data/tada-test-data/drop-test/20160314/kp4m-mosaic3/mos3.75870.fits.fz
#
# 53 files
#   find /data/tada-test-data \( -name "*.fits" -o -name "*.fits.fz" \) -print0 | xargs -0 python3 manage.py ingest_fits

class Command(BaseCommand):
    help = 'Uploads a FITS file and adds all its metadata to the DB.'

    def add_arguments(self, parser):
        parser.add_argument('fits', nargs='+',
                            help='Path to FITS file to ingest into NATICA' )


    def handle(self, *args, **options):
        for fits in options['fits']:
            try:
                submit_fits_file(fits)
            except Exception:
                raise CommandError('Could not submit "%s"' % fits)

            self.stdout.write(self.style.SUCCESS(
                'Successfully ingested file "%s"' % fits))
