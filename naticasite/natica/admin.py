from django.contrib import admin
from .models import FitsFile, Hdu


@admin.register(FitsFile)
class FitsFileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'instrument', 'telescope', 'date_obs',
        'release_date',
        'original_filename',
        'archive_filename',
        #'ra', 'dec',
    )

@admin.register(Hdu)
class HduAdmin(admin.ModelAdmin):
    list_display = ('hdu_idx', 'xtension', 'date_obs', 'extras')


