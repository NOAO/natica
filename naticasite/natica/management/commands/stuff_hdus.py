import traceback
import json
import os.path
from django.core.management.base import BaseCommand, CommandError
from natica.views import protected_store_metadata, validate_header, md5
import natica.exceptions as nex

# EXAMPLES:
#   python3 manage.py stuff_hdus /data/json/basic/kp109391.fits.json /data/json/drop-test/20160314/kp4m-mosaic3/mos3.75870.fits.json
#
#  find /data/json-scrape -name "*.json" -print0 | xargs -0 python3 manage.py stuff_hdus 
# ./manage.py shell -c "from natica.models import FitsFile; FitsFile.objects.all().delete()"
# find /data/small-json-scrape -name "*.json" -print0 | xargs -0 python3 manage.py stuff_hdus 
#
# FitsFile.objects.all().delete()
# psql
# SELECT pg_size_pretty(pg_database_size('archive'));

class Command(BaseCommand):
    help = 'Loads tables from JSON files that contain FITS HDUs as dicts.'

    def add_arguments(self, parser):
        parser.add_argument('jfits', nargs='+',
                            help='Path to json file to load into DB' )


    def handle(self, *args, **options):
        error = False
        badjfits = set()
        goodjfits = set()
        valdict= dict()

        for jfits in options['jfits']:
            valdict = dict(src_fname = jfits,
                           arch_fname = jfits,
                           md5sum = md5(jfits), # WRONG (don't have FITS)
                           size = os.path.getsize(jfits)
            )

            self.stdout.write('Stuff {}: '.format(jfits), ending='')
            try:
                with open(jfits) as f:  hdudict_list = json.load(f)
                allkeys = set().union(*[hd.keys() for hd in hdudict_list])

                protected_store_metadata(hdudict_list,valdict)
            except nex.BaseNaticaException as bna:
                self.stdout.write(self.style.ERROR(bna.error_message))
                self.stdout.write(traceback.format_exc())
                error = True
                badjfits.add(jfits)
                continue
            except Exception as err:
                self.stdout.write(self.style.ERROR('Not stored: {}'
                                                   .format(err)))
                self.stdout.write(traceback.format_exc())
                error = True
                badjfits.add(jfits)
                continue
            goodjfits.add(jfits)
            self.stdout.write(self.style.SUCCESS('OK'))

        total = len(options['jfits'])
        if len(goodjfits) > 0:
            self.stdout.write(self.style.SUCCESS(
                'Successfully ingested {}/{} files.'
                .format(len(goodjfits), total)))
        if error:
            raise CommandError('Failed ingest of {}/{} files: "{}"'
                               .format(len(badjfits),total, ' '.join(badjfits)))




