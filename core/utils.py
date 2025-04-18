# core/utils.py
from datetime import datetime, timedelta
from time import sleep

import jwt
import psycopg2
from django.core.management import call_command
from django.conf import settings
from core.models import Tenant
from cryptography.fernet import Fernet
from psycopg2 import sql
from django.db import connections


def generate_secure_key() -> str:
    """Generate a secure API key using the cryptography library."""
    api_key = Fernet.generate_key()
    return api_key.decode()


def create_tenant(student_id, host='localhost', port='5432'):
    """
    Automates the process of creating a new tenant database, running migrations,
    and registering the tenant in the `Tenant` model.
    """
    db_name = f'tenant_{student_id}'
    user = f'user_{student_id}'
    password = generate_secure_key()
    # Step 1: Create the new tenant database
    try:
        # Connect to the default PostgreSQL database to create the new tenant DB
        conn = psycopg2.connect(
            dbname='postgres', user='admin', password='complexpassword', host=host, port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cursor.fetchone():
            print(f"Database '{db_name}' already exists. Dropping it.")
            # Terminate all connections to the existing database
            cursor.execute(sql.SQL("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid();
            """), [db_name])
            # Drop the existing database
            cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Database '{db_name}' dropped successfully.")

        cursor.execute(f'CREATE DATABASE "{db_name}"')
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (user,))
        if cursor.fetchone():
            print(f"Role '{user}' already exists. Dropping it.")
            cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(user)))

        connections.databases[f'{db_name}_admin'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': 'admin',  # TODO fix
            'PASSWORD': 'complexpassword',  # TODO fix
            'HOST': host,
            'PORT': port,
            'TIME_ZONE': settings.TIME_ZONE,
            'CONN_HEALTH_CHECKS': settings.DATABASES['default'].get('CONN_HEALTH_CHECKS', False),  # ✅ Add this line
            'CONN_MAX_AGE': settings.DATABASES['default'].get('CONN_MAX_AGE', 0),  # ✅ Add this
            'AUTOCOMMIT': settings.DATABASES['default'].get('AUTOCOMMIT', True),
            'OPTIONS': settings.DATABASES['default'].get('OPTIONS', {}),
        }

        call_command('migrate', database=f'{db_name}_admin')
        sleep(1)
        print(f"Migrations applied successfully for tenant '{student_id}'.")

        cursor.execute(f"CREATE USER {user} WITH PASSWORD '{password}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {user};")
        cursor.close()
        conn.close()

        print(f"Database '{db_name}' created successfully!")

    except Exception as e:
        print(f"Error creating database {db_name}: {e}")
        return None

    jwt_payload = {
        'student_id': student_id,
        'db_name': db_name,
        'db_host': host,
        'db_port': port,
        'exp': datetime.now() + timedelta(days=120),  # Token expires in 4 month
    }

    # Encode the JWT using the secret key (ensure SECRET_KEY is set in settings)
    jwt_token = jwt.encode(jwt_payload, settings.SECRET_KEY, algorithm='HS256')

    return jwt_token
