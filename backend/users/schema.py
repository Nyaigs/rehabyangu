"""drf-spectacular: expose TenantJWTAuthentication as Bearer in the schema."""
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class TenantJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'users.authentication.TenantJWTAuthentication'
    name = 'TenantJWTAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
