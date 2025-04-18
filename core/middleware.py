# core/middleware.py
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from core.tenant_context import set_current_tenant_db_config, clear_current_tenant
from django.db import connections
from SimpleNote.settings.base import POSTGRES_USER, POSTGRES_PASSWORD


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.headers.get('x-api-key')
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                db_config = {
                    'db_name': payload['db_name'],
                    'db_host': payload['db_host'],
                    'db_port': payload['db_port'],
                }

                db_key = payload['db_name']

                connections.databases[db_key] = {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': db_config['db_name'],
                    'USER': POSTGRES_USER,
                    'PASSWORD': POSTGRES_PASSWORD,
                    'HOST': db_config['db_host'],
                    'PORT': db_config['db_port'],
                    'TIME_ZONE': settings.TIME_ZONE,
                    'CONN_HEALTH_CHECKS': settings.DATABASES['default'].get('CONN_HEALTH_CHECKS', False),
                    'CONN_MAX_AGE': settings.DATABASES['default'].get('CONN_MAX_AGE', 0),
                    'AUTOCOMMIT': settings.DATABASES['default'].get('AUTOCOMMIT', True),
                    'OPTIONS': settings.DATABASES['default'].get('OPTIONS', {}),
                    'ATOMIC_REQUESTS': settings.DATABASES['default'].get('ATOMIC_REQUESTS', False),
                }

                set_current_tenant_db_config(db_config)

            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'JWT has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'API Key is not provided',}, status=403)

    def process_response(self, request, response):
        clear_current_tenant()
        return response
