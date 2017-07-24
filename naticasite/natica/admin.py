from django.contrib import admin
from .models import FitsFile, Hdu


@admin.register(FitsFile)
class FitsFileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'original_filename',
        'archive_filename',
        'release_date',
        'instrument', 'telescope', 'date_obs',
        'ra', 'dec',
    )

@admin.register(Hdu)
class HduAdmin(admin.ModelAdmin):
    list_display = ('hdu_idx', 'xtension', 'date_obs', 'extras')


