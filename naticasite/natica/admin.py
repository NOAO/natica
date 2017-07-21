from django.contrib import admin
from .models import FitsFile, PrimaryHDU, ExtensionHDU


@admin.register(FitsFile)
class FitsFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_filename', 'archive_filename')
    #inlines = [PrimaryHDUAdmin]

@admin.register(PrimaryHDU)
class PrimaryHDUAdmin(admin.ModelAdmin):
    list_display = ('fitsfile', 'instrument', 'telescope', 'date_obs', 'extras')


@admin.register(ExtensionHDU)
class ExtensionHDUAdmin(admin.ModelAdmin):
    list_display = ('fitsfile',
                    'extension_idx', 'xtension', 'date_obs','extras')

