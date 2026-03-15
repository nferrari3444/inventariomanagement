import os
from celery import Celery

# Default to the local settings module; override via DJANGO_SETTINGS_MODULE in production.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.local')

app = Celery('InventarioProject')

# Read Celery config from Django settings, using the CELERY_ namespace.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in every INSTALLED_APP.
app.autodiscover_tasks()
