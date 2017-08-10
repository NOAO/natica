import traceback
import json
import os.path
from django.core.management.base import BaseCommand, CommandError
from natica.views import store_metadata, validate_header, md5
import natica.exceptions

# EXAMPLES:
#   python3 manage.py stuff_hdus /data/json/basic/kp109391.fits.json /data/json/drop-test/20160314/kp4m-mosaic3/mos3.75870.fits.json
#
#  find /data/json-scrape -name "*.json" -print0 | xargs -0 python3 manage.py stuff_hdus 
# ./manage.py shell -c "from natica.models import FitsFile; FitsFile.objects.all().delete()"
# find /data/json-scrape -name "*.json" -print0 | xargs -0 python3 manage.py stuff_hdus 
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
        defaults = dict(INSTRUME='NA',
                        )

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
                for k in defaults:
                    if k not in allkeys:
                        self.stdout.write(self.style.WARNING(
                            'Using default for {}. '.format(k)),
                                          ending='')
                        hdudict_list[0].setdefault(k,defaults[k])
                #!self.stdout.write('loaded ', ending='')
                #valdict.update(validate_header(hdudict_list))
                #!self.stdout.write('validated ', ending='')
                store_metadata(hdudict_list,valdict)
                #!self.stdout.write('stored ', ending='')
            except natica.exceptions.BaseNaticaException as bna:
                self.stdout.write(self.style.ERROR(bna.error_message))
                error = True
                badjfits.add(jfits)
                #! raise CommandError('Failed ingest of "{}";{}'
                #!                    .format(jfits, err))
                continue
            except Exception as err:
                self.stdout.write(self.style.ERROR('Not stored: {}'
                                                   .format(err)))
                error = True
                badjfits.add(jfits)
                traceback.print_exc()
                #! raise CommandError('Failed ingest of "{}";{}'
                #!                    .format(jfits, err))
                continue
            goodjfits.add(jfits)
            self.stdout.write(self.style.SUCCESS('OK'))

        total = len(options['jfits'])
        if len(goodjfits) > 0:
            self.stdout.write(self.style.SUCCESS(
                'Successfully ingested {}/{} files: {}'
                .format(len(goodjfits), total, ' '.join(goodjfits))))
        if error:
            raise CommandError('Failed ingest of {}/{} files: "{}"'
                               .format(len(badjfits),total, ' '.join(badjfits)))




