from .base import *

DEBUG = True

ALLOWED_HOSTS = []

# Local SQLite database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tenant_manager',  # Same name as the DB we created in Docker
        'USER': 'admin',         # Same user as the one we created in Docker
        'PASSWORD': 'complexpassword',  # Same password as in the Docker command
        'HOST': 'localhost',        # Using localhost for local setup
        'PORT': '5432',             # Default PostgreSQL port
    }
}
