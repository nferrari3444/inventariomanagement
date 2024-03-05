"""
WSGI config for InventarioProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
from InventarioProject.settings import base

   
if base.DEBUG == True:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.local')
    
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.production')


application = get_wsgi_application()

app = application

