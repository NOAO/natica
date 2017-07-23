from django.contrib import admin
from .models import FitsFile, PrimaryHDU, ExtensionHDU


@admin.register(FitsFile)
class FitsFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_filename', 'archive_filename')

@admin.register(PrimaryHDU)
class PrimaryHDUAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'telescope', 'date_obs', 'extras')


@admin.register(ExtensionHDU)
class ExtensionHDUAdmin(admin.ModelAdmin):
    list_display = ('extension_idx', 'xtension', 'date_obs', 'extras')


