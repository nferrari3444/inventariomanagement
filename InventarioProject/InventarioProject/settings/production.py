from .base import *

BASE_DIR = Path(__file__).resolve().parent

USE_X_FORWARDED_HOST=True


STATICFILES_STORAGE= 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS =  [os.path.join(BASE_DIR, "static")]

STATIC_ROOT =  os.path.join(BASE_DIR, "staticfiles_build")


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
