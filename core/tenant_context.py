# core/tenant_context.py
import threading

_thread_locals = threading.local()


def set_current_tenant_db_config(db_config):
    _thread_locals.tenant_db_config = db_config


def get_current_tenant_db_config():
    return getattr(_thread_locals, 'tenant_db_config', None)


def clear_current_tenant():
    if hasattr(_thread_locals, 'tenant_db_config'):
        del _thread_locals.tenant_db_config
