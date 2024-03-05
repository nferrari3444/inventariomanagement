from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent

USE_X_FORWARDED_HOST=True

COMPRESS_URL = '/static/'
COMPRESS_ROOT = BASE_DIR / 'static'

COMPRESS_ENABLED = True


STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',)

AWS_S3_OBJECT_PARAMETERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'CacheControl': 'max-age=94608000',
}

AWS_STORAGE_BUCKET_NAME= 'filsa'
AWS_S3_REGION_NAME= 'us-east-1'
AWS_ACCESS_KEY_ID= os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY')

# Tell django-storages the domain to use to refer to static files.
AWS_S3_CUSTOM_DOMAIN= '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_DEFAULT_ACL=None

# Tell the staticfiles app to use S3Boto3 storage when writing the collected static files (when
# you run `collectstatic`).
#STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATICFILES_DIRS =  [os.path.join(BASE_DIR, "static")]

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'

MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
#STATIC_ROOT =  os.path.join(BASE_DIR, "staticfiles_build","static")

#STATICFILES_STORAGE= 'whitenoise.storage.CompressedManifestStaticFilesStorage'


#STATICFILES_STORAGE='custom_storages.StaticStorage'

#STATIC_URL= "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)


AWS_S3_SECURE_URLS= True

STATIC_ROOT = 'static'
STATIC_URL = '/static/'
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'

# STATIC_URL= "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

# STATIC_ROOT= os.path.join(BASE_DIR,'static')

# MEDIA_URL = '/media/'
# MEDIA_ROOT=  BASE_DIR

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
