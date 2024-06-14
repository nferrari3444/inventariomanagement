from .base import *

#BASE_DIR = Path(__file__).resolve().parent.parent

BASE_DIR = Path(__file__).resolve().parent.parent.parent

print('BASE_DIR is', BASE_DIR)
#print('BASE_DIR_ is', BASE_DIR_)
USE_X_FORWARDED_HOST=True


# AWS_S3_OBJECT_PARAMETERS = {
#     'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
#     'CacheControl': 'max-age=94608000',
# }

# AWS_STORAGE_BUCKET_NAME= 'filsa'
# AWS_S3_REGION_NAME= 'us-east-1'
# AWS_ACCESS_KEY_ID= os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY')

# # Tell django-storages the domain to use to refer to static files.
# AWS_S3_CUSTOM_DOMAIN= '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# AWS_DEFAULT_ACL=None

# Tell the staticfiles app to use S3Boto3 storage when writing the collected static files (when
# you run `collectstatic`).
#STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'



# STATICFILES_LOCATION = 'static'
# STATICFILES_STORAGE = 'custom_storages.StaticStorage'

# MEDIAFILES_LOCATION = 'media'
# DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
#STATIC_ROOT =  os.path.join(BASE_DIR, "staticfiles_build","static")

#STATICFILES_STORAGE= 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
#STATICFILES_STORAGE='custom_storages.StaticStorage'

#STATIC_URL= "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)


# AWS_S3_SECURE_URLS= True
#STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',)

#STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles', 'static')
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

# STATIC_ROOT = 'static'
# STATIC_URL = '/static/'
# MEDIA_ROOT = 'media'
# MEDIA_URL = '/media/'

# STATIC_URL= "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

# STATIC_ROOT= os.path.join(BASE_DIR,'static')

# MEDIA_URL = '/media/'
# MEDIA_ROOT=  BASE_DIR


# COMPRESS_URL =   STATIC_URL      #'/static/'
# COMPRESS_ROOT =  '/static/'              #STATIC_URL               #BASE_DIR / 'static'

# COMPRESS_ENABLED = True


SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'URL': os.getenv('DATABASE_URL'),
        'NAME': os.getenv('DATABASE'),
        'USER': 'filsa',
        'PASSWORD': os.getenv('PASSWORD'),
        'HOST': 'localhost',
        'PORT': ''
    }
}
