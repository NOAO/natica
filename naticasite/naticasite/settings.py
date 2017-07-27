"""
Django settings for naticassite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
#!import warnings
#!
#!warnings.filterwarnings(
#!    'error', r"DateTimeField .* received a naive datetime",
#!    RuntimeWarning, r'django\.db\.models\.fields',
#!)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

LOGIN_URL = "/admin/login/"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#MEDIA_ROOT = '/var/mars/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
#    os.path.join(BASE_DIR, 'bower_components'),
#    os.path.join(BASE_DIR, 'theme'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_ROOT = '/var/www/natica/static/'


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'natica', # replace LSA
    'rest_framework',
    'rest_framework_swagger',
    'debug_toolbar',
)

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'middleware.RequestExceptionHandler',
    ]

ROOT_URLCONF = 'naticasite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #'django.core.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'naticasite.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'MST'
USE_I18N = True
USE_L10N = True
USE_TZ = True

INTERNAL_IPS = ['127.0.0.1',  '10.0.2.2'] # '0.0.0.0', '192.168.1.45',

SWAGGER_SETTINGS = {
    'enabled_methods': [
        'get',
        'post',
    ],
    'info': {
        'title': 'NATICA Prototype API Documentation',
        'description': (
            'This is documentation for '
            'NATICA (National Astronomy Telescope Image & Catalog Archive) '
            'web services.  '
        ),
    },
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    #!'DEFAULT_PERMISSION_CLASSES': [
    #!    'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    #!]
}


CONN_MAX_AGE = 7200 # keep DB connections for 2 hours


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    #!'formatters': {
    #!    'django.server': {
    #!        '()': 'django.utils.log.ServerFormatter',
    #!        'format': '[%(server_time)s] %(message)s',
    #!    }
    #!},
    'formatters': {
        'brief': {
            'format': '%(levelname)-8s: %(filename)-17s: %(message)s',
        },
        'precise': {
            'format': '%(asctime)s %(filename)-17s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class' : 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'precise',
            'filename': '/var/log/natica/natica.log',
            #! 'maxBytes': 10000000,
            #! 'backupCount': 5,
        },
        'debugfile': {
            'class' : 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'precise',
            'filename': '/var/log/natica/natica-detail.log',
            #! 'maxBytes': 10000000,
            #! 'backupCount': 5,
        },
        #!'django.server': {
        #!    'level': 'INFO',
        #!    'class': 'logging.StreamHandler',
        #!    'formatter': 'django.server',
        #!},
    },
    'root': {
        'handlers': ['file', 'debugfile'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'debugfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # Hide annoying admin "DEBUG, Exception":
        #  e.g "Exception while resolving variable 'errors' in template 'admin/change_list.html'."
        'django.template': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        #!'django.server': {
        #!    'handlers': ['django.server'],
        #!    'level': 'INFO',
        #!    'propagate': False,
        #!}
    },
}

exec(open('/etc/natica/django_local_settings.py').read())

