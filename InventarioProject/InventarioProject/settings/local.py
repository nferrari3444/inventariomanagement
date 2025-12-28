from dotenv import load_dotenv
import os

load_dotenv()

from .base import *



INSTALLED_APPS = INSTALLED_APPS + [

    "debug_toolbar",
]

MIDDLEWARE = MIDDLEWARE + [
    # ...
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # ...
]

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1")

STATIC_ROOT =  os.path.join(BASE_DIR, 'static/')    
#print('STATIC_ROOT is {}'.format(STATIC_ROOT))

COMPRESS_URL = '/static/'
COMPRESS_ROOT = BASE_DIR / 'static'

COMPRESS_ENABLED = True

STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',
                       'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder')

STATIC_URL = 'static/'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DEV_DATABASE"), # Name of the database you created
        'USER': os.getenv("DEV_USER"),      # Name of the user you created
        'PASSWORD': os.getenv("DEV_PASSWORD"), # Password for the user
        'HOST': os.getenv("DEV_HOST"),   # Use this for Docker Desktop on Windows
        'PORT': os.getenv("DEV_PORT"),            # Empty string for default port (5432)
    }
}

# if 'test' in sys.argv:
#     DATABASES = {
#          "default": {
#              "ENGINE": "django.db.backends.sqlite3",
#              "NAME": ":memory:",
#          }
#     }

# DATABASES = {
#          "default": {
#              "ENGINE": "django.db.backends.sqlite3",
#              "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
#          }
# }
