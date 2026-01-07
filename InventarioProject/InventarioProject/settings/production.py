from .base import *

import environ

load_dotenv()

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define a base directory for logs (adjust as necessary)
# LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
# os.makedirs(LOG_DIR, exist_ok=True) # Ensure the log directory exists

DEBUG = False
print('BASE_DIR is', BASE_DIR)
#print('BASE_DIR_ is', BASE_DIR_)
USE_X_FORWARDED_HOST=True

# Security Settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
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

# Database
# DATABASES = {
#     'default': os.getenv("DATABASE_URL"),  # Reads DATABASE_URL
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'URL': os.getenv('DATABASE_URL'),
        'NAME': 'filsadb',
        'USER': 'filsa',
        'HOST': 'localhost',
        'PASSWORD': 'Filsa.2024',
        'PORT': '5432'

    }
}

# # Logging
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     },
# }