# core/db_router.py
from core.tenant_context import get_current_tenant_db_config


class TenantRouter:
    def db_for_read(self, model, **hints):
        cfg = get_current_tenant_db_config()
        return f"{cfg['db_name']}" if cfg else None

    def db_for_write(self, model, **hints):
        cfg = get_current_tenant_db_config()
        return f"{cfg['db_name']}" if cfg else None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
