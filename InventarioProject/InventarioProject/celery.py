import os
from celery import Celery

# Use DJANGO_SETTINGS_MODULE if already set (e.g. by the systemd service in production).
# Fall back to local settings for development.
_settings_module = os.getenv(
    'DJANGO_SETTINGS_MODULE',
    'InventarioProject.settings.production' if os.getenv('DJANGO_ENV') == 'production'
    else 'InventarioProject.settings.local',
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', _settings_module)

app = Celery('InventarioProject')

# Read Celery config from Django settings, using the CELERY_ namespace.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in every INSTALLED_APP.
app.autodiscover_tasks()
