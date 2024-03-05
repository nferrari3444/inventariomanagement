from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent

USE_X_FORWARDED_HOST=True

COMPRESS_URL = '/static/'
COMPRESS_ROOT = BASE_DIR / 'static'

COMPRESS_ENABLED = True



STATICFILES_DIRS =  [os.path.join(BASE_DIR, "static")]

STATIC_ROOT =  os.path.join(BASE_DIR, "staticfiles_build","static")

STATICFILES_STORAGE= 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',
                       )


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'URL': os.getenv('DATABASE_URL'),
        'NAME': os.getenv('PGDATABASE'),
        'USER': 'postgres',
        'PASSWORD': os.getenv('PGPASSWORD'),
        'HOST': os.getenv('PGHOST'),
        'PORT':  39239
    }
}
