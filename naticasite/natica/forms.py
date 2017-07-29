from django import forms

class SearchForm(forms.Form):
    coordinates = forms.ComboField(required=False,
                                   fields=[
        forms.FloatField(label='RA'),
        forms.FloatField(label='DEC')
    ])
    exposure_time = forms.FloatField(required=False,
                                     label='Exposure Time (secs)')
    filename =  forms.CharField(required=False, max_length=99,
                                label='archive_filename')
    original_filename =  forms.CharField(required=False, max_length=99)
    #!image_filter = forms.ChoiceField(choices=['raw',
    #!                                          'calibrated',
    #!                                          ])
    obs_date = forms.DateField(required=False, label='DATE-OBS')
    pi = forms.CharField(required=False,label='PI', max_length=20)
    prop_id = forms.CharField(required=False,label='PROP-ID', max_length=10)
    release_date = forms.DateField(required=False,label='Release Date')
    search_box_min = forms.FloatField(required=False,label='Box Min')
    tele_inst = forms.CharField(required=False,label="TELE_INST", max_length=99)
