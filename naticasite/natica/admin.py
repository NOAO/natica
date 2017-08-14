from django.contrib import admin
from .models import FitsFile, Hdu, Proposal
from pathlib import PurePath



class HduInline(admin.TabularInline):
    model = Hdu

class InstrumFilter(admin.SimpleListFilter):
    title = 'instrument'
    parameter_name = 'instrument'
    
    def lookups(self, request, model_admin):
        qs = FitsFile.objects.order_by('instrument').distinct('instrument')
        return [(rec.instrument, rec.instrument) for rec in qs]

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        else:
            return queryset.filter(instrument=self.value())
    
@admin.register(Hdu)
class HduAdmin(admin.ModelAdmin):
    list_display = ('hdu_idx', 'fitsfile_archive_filename', 'xtension',
                    #'date_obs',     'ra', 'dec',
                    'extras')

    def fitsfile_archive_filename(self, obj):
        return PurePath(obj.fitsfile.archive_filename).name
    


@admin.register(FitsFile)
class FitsFileAdmin(admin.ModelAdmin):
    #!inlines = [HduInline,]  # allow HDU edit within FitsFile obj
    list_filter = (InstrumFilter,
                   #'date_obs',
    )

    list_display = (
        'id',
        'instrument',
        'telescope',
        'date_obs',
        'release_date',
        'original_filename',
        'archive_filename',
        #'extras',
        'ra', 'dec',
        'exposure',
    )


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    pass
