"""
WSGI config for InventarioProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application



#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.local')
# settings_module = 'InventarioProject.settings.local' if 'runserver' in sys.argv else 'InventarioProject.settings.production'
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.production')


application = get_wsgi_application()

app = application

