"""
Django settings for src project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _
from google.oauth2 import service_account
from dotenv import load_dotenv
import json
load_dotenv()
import mimetypes
import sys
from logging.handlers import SysLogHandler
mimetypes.add_type("text/css", ".css", True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv("environment") == 'development' else False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'azizlioua111.pythonanywhere.com', 'www.raykomfi.com', 'logs4.papertrailapp.com']

# Application definition

INSTALLED_APPS = [
    'cloudinary',
    'materializecssform',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'debug_toolbar',
    'django.contrib.humanize',
    'raykomfi',
    'api',
    'django_countries',
    'sorl.thumbnail', 
    'rest_framework',
    'corsheaders',
    'parsley',
    'admin_auto_filters',
    'django_filters',
    'background_task',
    'django_extensions',
    "compressor",
    'notifications',
    'hitcount',
    'admin_honeypot',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'csp.middleware.CSPMiddleware',
    'raykomfi.custom_middlewares.AutoLogout',
    'ratelimit.middleware.RatelimitMiddleware',
    'raykomfi.custom_middlewares.ActiveUserMiddleware'
    ]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'raykomfi.context_processors.not_opened_messages',
            ],
        },
    },
]

# Check new messages
TEMPLATE_CONTEXT_PROCESSORS = (
    'raykomfi.context_processors.not_opened_messages',
)

WSGI_APPLICATION = 'src.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASS"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
    },
    'OPTIONS': { "init_command": "SET storage_engine=innoDB" }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ar-ae'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

def show_toolbar(request):
    return True

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}

STATIC_URL = '/static/'
COMPRESS_ENABLED = True
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [
    BASE_DIR / "src/static",
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',  'compressor.filters.cssmin.CSSMinFilter']


# Custom User Model Settings
AUTH_USER_MODEL = 'raykomfi.User'
AUTHENTICATION_BACKENDS = ['raykomfi.backends.EmailBackend']

# Media settings.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


LOGIN_URL = 'raykomfi:user-signin'
LOGIN_REDIRECT_URL = 'raykomf:raykomfi-home'

# Language settings
LOCAL_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
LANGUAGES = (
    ('ar', _('Arabic')),
)
MULTILINGUAL_LANGUAGES = (
    "ar-ae",
)

#DataFlair #Local Memory Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'DataFlair',
    }
}

EMAIL_USE_SSL = True
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

#Handle session is not Json Serializable
# SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Auto logout delay in minutes
AUTO_LOGOUT_DELAY = 5 #equivalent to 5 minutes



# Rest framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated' 
    ],
}

# Cors settings
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "https://azizlioua111.pythonanywhere.com",
    "https://www.raykomfi.com"
]


DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME")
GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
    json.loads(os.getenv("GS_CREDENTIALS"))
)

# Image resize
DJANGORESIZED_DEFAULT_SIZE = [900, 600]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True

# Ratelimit

RATELIMIT_VIEW='raykomfi.views.suspicious_limit'

# Content Security Policy
if os.getenv('environment') == 'prod':
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    CSP_DEFAULT_SRC = ("'none'", )
    CSP_STYLE_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'",)
    CSP_IMG_SRC = ("'self'", "data:",)
    CSP_FONT_SRC = ("'self'",)
    CSP_CONNECT_SRC = ("'self'", )
    CSP_OBJECT_SRC = ("'none'", )
    CSP_BASE_URI = ("'none'", )
    CSP_FRAME_ANCESTORS = ("'none'", )
    CSP_FORM_ACTION = ("'self'", )
    CSP_INCLUDE_NONCE_IN = ('script-src',)


# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 300

# Number of seconds that we will keep track of inactive users for before 
# their last seen is removed from the cache
USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7

SITE_ID=os.getenv('SITE_ID')

if DEBUG == False:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,                                                                    
        'handlers': {                                                                                         
            'syslog': {
                'level': 'DEBUG',
                'class': 'logging.handlers.SysLogHandler',                                                    
                'formatter': 'verbose',
                'address': (os.getenv('log_host'), int(os.getenv('log_port'))),                                         
            },                                                                                            
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s|%(asctime)s|%(module)s|%(process)d|%(thread)d|%(message)s',
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s|%(message)s'
            },
        },
        'loggers': {
            'django': {
            'handlers': ['syslog'],
            'level': 'INFO',
            'propagate': True,
        } 
        }
    }