from .base import *


BASE_DIR = Path(__file__).resolve().parent.parent.parent

print('BASE_DIR is', BASE_DIR)
#print('BASE_DIR_ is', BASE_DIR_)
USE_X_FORWARDED_HOST=True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS =  [os.path.join(BASE_DIR, "static")]

print('STATICFILES_DIRS is ', STATICFILES_DIRS )

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    #"staticfiles.finders.FileSystemFinder",
    #"staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


MEDIA_URLS ='/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'URL': os.getenv('DATABASE_URL'),
        'NAME': 'filsadb',
        'USER': 'filsa',
        'PASSWORD': 'Filsa.2024',
	'PORT': 5432

    }
}
