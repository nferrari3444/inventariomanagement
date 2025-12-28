#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from InventarioProject.settings import base


def main():
    """Run administrative tasks."""

    if base.DEBUG == True:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.local')
    
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.production')
    #os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    print('Using settings module:', os.getenv('DJANGO_SETTINGS_MODULE'))
    print("sys.path", sys.path)
    print("sys argv", sys.argv)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
