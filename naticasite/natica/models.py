from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class FitsFile(models.Model):
    # md5sum of file as stored in MSS
    md5sum = models.CharField(max_length=32, unique=True)
    #id = models.CharField(max_length=32, primary_key=True)
    original_filename = models.CharField(max_length=256)
    archive_filename = models.CharField(max_length=256)
    filesize         = models.BigIntegerField()
    release_date     = models.DateTimeField()

    # (Possibly aggregated) from HDU(s)
    instrument = models.CharField(max_length=80, help_text = "INSTRUME")
    telescope  = models.CharField(max_length=80, help_text = "TELESCOP")
    date_obs  = models.DateTimeField(null=True, help_text = 'DATE-OBS')
    ra = models.CharField(null=True, max_length=20)
    dec = models.CharField(null=True, max_length=20)

    extras = JSONField(default={})  

class Hdu(models.Model):
    """Required header fields per FITS Std 3.0"""
    fitsfile = models.ForeignKey(FitsFile, on_delete=models.CASCADE)
    hdu_idx  = models.PositiveSmallIntegerField() # hdu_idx[0] :: Primary HDU
    # (SIMPLE = T) Required For Primary HDU
    # name of ext type; Required For Conformant Extensions HUD
    xtension = models.CharField(max_length=40, blank=True)

    # Required For Primary, Extension HDU
    bitpix = models.IntegerField()
    naxis = models.PositiveSmallIntegerField()
    naxisN = ArrayField(models.PositiveSmallIntegerField(), default=list)
    
    # Required For Conformant Extensions HDU (not Primary)
    pcount = models.PositiveIntegerField(null=True)
    gcount = models.PositiveIntegerField(null=True)

    # Others (not required by STD, but we need them in at least one HDU)
    instrument = models.CharField(max_length=80,blank=True,help_text="INSTRUME")
    telescope  = models.CharField(max_length=80,blank=True,help_text="TELESCOP")
    date_obs  = models.DateTimeField(null=True, help_text = 'DATE-OBS')
    obj  = models.CharField(max_length=80, blank=True, help_text = 'OBJECT')
    ra = models.CharField(null=True, max_length=20)
    dec = models.CharField(null=True, max_length=20)

    # Other FITS field content not stored above
    extras = JSONField() 

    

##############################################################################
### New schema (PROPOSED) to replace Legacy Science Archive 
###
#!    
#!class Hdu(models.Model):
#!    hdu_index = models.IntegerField() # Primary HDU: hdu_index=0
#!    primary_hdu_id = models.ForeignKey('self', on_delete=models.CASCADE)
#!    file = models.ForeignKey(File, on_delete=models.CASCADE)
#!    #! extra = HStoreField() # All HDR fields not otherwise stored.
#!
#!    # Approximately from VoiSiap (Legacy Science Archive)
#!    object           = models.CharField(max_length=80)
#!    survey           = models.CharField(max_length=80)
#!    survey_id        = models.CharField(max_length=80) # was "surveyid"
#!    prop_id          = models.CharField(max_length=80)
#!    start_date       = models.DateTimeField()
#!    ra               = models.FloatField()
#!    dec              = models.FloatField()
#!    equinox          = models.FloatField()
#!    naxes            = models.IntegerField()
#!    naxis_length     = models.CharField(max_length=80)
#!    mimetype         = models.CharField(max_length=80)
#!    instrument       = models.CharField(max_length=80)
#!    telescope        = models.CharField(max_length=80)
#!    pixflags         = models.CharField(max_length=80)
#!    bandpass_id      = models.CharField(max_length=80)
#!    bandpass_unit    = models.CharField(max_length=80)
#!    bandpass_lolimit = models.CharField(max_length=80)
#!    bandpass_hilimit = models.CharField(max_length=80)
#!    exposure         = models.FloatField()
#!    depth            = models.FloatField()
#!    depth_err        = models.CharField(max_length=80)
#!    magzero          = models.FloatField()
#!    magerr           = models.FloatField()
#!    seeing           = models.FloatField()
#!    airmass          = models.FloatField()
#!    astrmcat         = models.CharField(max_length=80)
#!    biasfil          = models.CharField(max_length=80)
#!    bunit            = models.CharField(max_length=80)
#!    dqmask           = models.CharField(max_length=80)
#!    darkfil          = models.CharField(max_length=80)
#!    date_obs         = models.DateTimeField()
#!    flatfil          = models.CharField(max_length=80)
#!    ds_ident         = models.CharField(max_length=80)
#!    # dtnsanam         = models.CharField(max_length=80)
#!    # dtacqnam         = models.CharField(max_length=80)
#!    # dtobserv         = models.CharField(max_length=80)
#!    # dtpi             = models.CharField(max_length=80)
#!    # dtpiaffl         = models.CharField(max_length=80)
#!    # dtpropid         = models.CharField(max_length=80)
#!    # dtsite           = models.CharField(max_length=80)
#!    # dttitle          = models.CharField(max_length=80)
#!    # dtutc            = models.DateTimeField()
#!    efftime          = models.FloatField()
#!    filter           = models.CharField(max_length=80)
#!    filtid           = models.CharField(max_length=80)
#!    frngfil          = models.CharField(max_length=80)
#!    ha               = models.FloatField()
#!    instrume         = models.CharField(max_length=80)
#!    md5sum           = models.CharField(max_length=80)
#!    mjd_obs          = models.FloatField()
#!    obs_elev         = models.FloatField()
#!    obs_lat          = models.FloatField()
#!    obs_long         = models.FloatField()
#!    photbw           = models.FloatField()
#!    photclam         = models.FloatField()
#!    photfwhm         = models.FloatField()
#!    pipeline         = models.CharField(max_length=80)
#!    plver            = models.CharField(max_length=80)
#!    proctype         = models.CharField(max_length=80)
#!    prodtype         = models.CharField(max_length=80)
#!    puplfil          = models.CharField(max_length=80)
#!    radesys          = models.CharField(max_length=80)
#!    rawfile          = models.CharField(max_length=80)
#!    sb_recno         = models.IntegerField()
#!    sflatfil         = models.CharField(max_length=80)
#!    timesys          = models.CharField(max_length=80)
#!    disper           = models.CharField(max_length=80)
#!    obsmode          = models.CharField(max_length=80)
#!    filename         = models.CharField(max_length=80)
#!    nocslit          = models.CharField(max_length=80)
#!    nocssn           = models.CharField(max_length=80)
#!    zd               = models.FloatField()
#!    # fits_data_product_id = models.BigIntegerField()
#!    # Store corners (or polygon) in single field? !!!
#!    #! corn1dec         = models.IntegerField()
#!    #! corn2dec         = models.IntegerField()
#!    #! corn3dec         = models.IntegerField()
#!    #! corn4dec         = models.IntegerField()
#!    #! corn1ra          = models.IntegerField()
#!    #! corn2ra          = models.IntegerField()
#!    #! corn3ra          = models.IntegerField()
#!    #! corn4ra          = models.IntegerField()
#!    rspgrp           = models.CharField(max_length=80)
#!    rsptgrp          = models.CharField(max_length=80)
#!    reject           = models.CharField(max_length=80)
#!    seqid            = models.CharField(max_length=80)
#!    plqname          = models.CharField(max_length=80)
#!    pldname          = models.CharField(max_length=80)
#!    # FK5 is an equatorial coordinate system (coordinate system linked
#!    # to the Earth) based on its J2000 position.
#!    fk5coords        = models.CharField(max_length=80) # geometry(Point,100000) 

    
