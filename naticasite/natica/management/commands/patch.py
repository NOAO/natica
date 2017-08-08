from django.core.management.base import BaseCommand, CommandError
from natica.views import PATCH

# EXAMPLES:
#   python3 manage.py patch
#

class Command(BaseCommand):
    help = 'Uploads a FITS file and adds all its metadata to the DB.'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--progress',
                            default = '1000',
                            help=('Number of objects to skip between output'
                                  ' of progress DOT'))

    def handle(self, *args, **options):
        error = False
        badfits = set()
        goodfits = set()
        prgcnt = int(options['progress'])

        cnt = PATCH(progress=prgcnt)
        
        self.stdout.write(self.style.SUCCESS(
            'Successfully PATCHed {} objects'.format(cnt)))

        if error:
            raise CommandError('Failed PATCH')




