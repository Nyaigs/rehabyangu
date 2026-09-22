from django.db import transaction

from .rls import set_rls_context


class TenantRLSMiddleware:
    """Keep each request in one transaction so `SET LOCAL` cannot leak pools."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with transaction.atomic():
            # Deny tenant rows until authentication or a public workspace flow
            # deliberately establishes its tenant context.
            set_rls_context()
            response = self.get_response(request)
            if hasattr(response, 'render') and not response.is_rendered:
                response.render()
            return response
