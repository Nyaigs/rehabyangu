from rest_framework import status
from rest_framework.exceptions import APIException


class FeatureNotInPlan(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_code = 'feature_not_in_plan'

    def __init__(self, feature):
        self.detail = {
            'error': 'This feature is not available on your plan.',
            'upgrade_required': True,
            'feature': feature,
        }
