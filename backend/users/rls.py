from django.db import connection


def set_rls_context(tenant_id=None, *, is_platform_admin=False, local=True):
    """Set RLS context; requests use transaction-local scope, commands may opt out."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('app.tenant_id', %s, %s), set_config('app.is_platform_admin', %s, %s)",
            [str(tenant_id) if tenant_id else '', local, 'true' if is_platform_admin else 'false', local],
        )
