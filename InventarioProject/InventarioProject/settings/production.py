from .base import *



USE_X_FORWARDED_HOST=True

STATICFILES_STORAGE= 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS =  'static',
STATIC_ROOT =  'staticfiles_build'


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
