archive_root = '/data/natica-archive'
natica_ingest_url = 'http://0.0.0.0:8000/natica/ingest/'

# !!! REPLACE LUTs with read of files in /etc/natica. Populate those from DB.
stiLUT = {
    # (site, telescope,instrument): Prefix 
    ('cp', 'soar', 'goodman'):   'psg',  
    ('cp', 'soar', 'goodman spectrograph'):   'psg',  # added
    ('cp', 'soar', 'osiris'):    'pso',  
    ('cp', 'soar', 'soi'):       'psi',  
    ('cp', 'soar', 'spartan'):   'pss',  
    ('cp', 'soar', 'spartan ir camera'):   'pss',   # added
    ('cp', 'soar', 'sami'):      'psa',  
    ('ct', 'ct4m', 'decam'):     'c4d',  
    ('ct', 'ct4m', 'cosmos'):    'c4c', 
    ('ct', 'ct4m', 'ispi'):      'c4i',  
   #('ct', 'ct4m', 'arcon'):     'c4a',   # removed <2016-03-17 Thu>
    ('ct', 'ct4m', 'mosaic'):    'c4m',  
    ('ct', 'ct4m', 'newfirm'):   'c4n',  
   #('ct', 'ct4m', 'triplespec'):'c4t', 
    ('ct', 'ct4m', 'arcoiris'):  'c4ai',  # added <2016-03-17 Thu>
    ('ct', 'ct15m', 'chiron'):   'c15e',  
    ('ct', 'ct15m', 'echelle'):  'c15e',  # added
    ('ct', 'ct15m', 'arcon'):    'c15s',  
    ('ct', 'ct13m', 'andicam'):  'c13a',  
    ('ct', 'ct1m', 'y4kcam'):    'c1i',  
    #('ct', 'ct09m', 'arcon'):    'c09i',  
    ('ct', 'ct09m', 'ccd_imager'): 'c09i', # renamed from arcon
    ('ct', 'ctlab', 'cosmos'):   'clc',  
    ('kp', 'kp4m', 'mosaic'):    'k4m',  
    ('kp', 'kp4m', 'mosaic3'):   'k4m',  # added
    ('kp', 'kp4m', 'newfirm'):   'k4n',  
    ('kp', 'kp4m', 'kosmos'):    'k4k',  
    ('kp', 'kp4m', 'cosmos'):    'k4k',  
    ('kp', 'kp4m', 'ice'):       'k4i',  
    ('kp', 'kp4m', 'wildfire'):  'k4w',  
    ('kp', 'kp4m', 'flamingos'): 'k4f',  
    ('kp', 'kp35m', 'whirc'):    'kww',  
    ('kp', 'wiyn', 'whirc'):     'kww',  # added
    ('kp', 'wiyn', 'bench'):     'kwb',  # changed tele (kp35m) <2016-06-17 Fri>
    ('kp', 'kp35m', 'minimo/ice'):'kwi',  
    ('kp', 'kp35m', '(p)odi'):    'kwo',  
    ('kp', 'kp21m', 'mop/ice'):   'k21i',  
    ('kp', 'kp21m', 'wildfire'):  'k21w',  
    ('kp', 'kp21m', 'falmingos'): 'k21f',  
    ('kp', 'kp21m', 'gtcam'):     'k21g',  
    ('kp', 'kpcf', 'mop/ice'):   'kcfs',  
    ('kp', 'kp09m', 'hdi'):       'k09h',  
    ('kp', 'kp09m', 'mosaic'):    'k09m',  
    ('kp', 'kp09m', 'ice'):       'k09i',
    ('kp', 'bok23m','90prime'):   'ksb',  # BOK
    ('ct', 'bok23m','kosmos'):   'ksb',  # fake, for testing
    #'NOTA':      'uuuu',  
}

obsLUT = {
    #Observation-type:           code  
    'object':                    'o',  
    'photometric standard':      'p',
    'bias':                      'z',
    'zero':                      'z', # added 5/8/15 for bok
    'dome or projector flat':    'f',
    'dome flat':                 'f', # added 1/8/16 for mosaic3
    'dflat':                     'f', # added 10/23/15 (per dsid.c)
    'flat':                      'f',
    'projector':                 'f', # added 10/23/15 (per dsid.c)
    'sky':                       's',
    'skyflat':                   's', # added 10/23/15 (per dsid.c)
    'dark':                      'd',
    'calibration':               'c', # added 2/1/16 for ct15m-echelle
    'calibration or comparison': 'c',
    'comp':                      'c', # added 10/23/15 (per dsid.c)
    'comparison':                'c', # added 10/23/15 (per dsid.c)
    'illumination calibration':  'i',
    'focus':                     'g',
    'fringe':                    'h',
    'pupil':                     'r',
    'nota':                      'u',
}

procLUT = {
    #Processing-type: code   
    'raw': 'r',
    'instcal': 'o',
    'mastercal': 'c',
    'projected': 'p',
    'stacked': 's',
    'skysub': 'k',
    'nota': 'u',
}

prodLUT = {
    #Product-type:         code    
    'image':               'i',   
    'image 2nd version 1': 'j',   
    'dqmask':              'd',   
    'expmap':              'e',   
    'graphics (size)':     'gn',   
    'weight':              'w',   
    'nota':                'u',
    'wtmap':               '-',  # Found in pipeline, not used for name
    'resampled':           '-',  # Found in pipeline, not used for name
    }
