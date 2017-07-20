from django.contrib import admin
from .models import FitsFile, PrimaryHDU, ExtensionHDU

@admin.register(FitsFile)
class FitsFileAdmin(admin.ModelAdmin):
    pass

@admin.register(PrimaryHDU)
class PrimaryHDUAdmin(admin.ModelAdmin):
    pass

@admin.register(ExtensionHDU)
class ExtensionHDUAdmin(admin.ModelAdmin):
    pass


