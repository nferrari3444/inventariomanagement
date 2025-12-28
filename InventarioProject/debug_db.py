import os
from django.conf import settings
import django
import sys


# Add your project to Python path
sys.path.append('.')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InventarioProject.settings.local')
django.setup()

print("Django Database Configuration")

db_settings = settings.DATABASES['default']

for key, value in db_settings.items():
    if key == 'PASSWORD':
        print(f"{key}: {'*' * len(str(value))}") # Hide password
    else:
        print(f"{key}: {value}")