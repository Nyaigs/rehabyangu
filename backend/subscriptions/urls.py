from django.urls import path
from .views import RecordPaymentView, NotificationListView, MarkNotificationReadView

urlpatterns = [
    path('api/record-payment/', RecordPaymentView.as_view(), name='record-payment'),
    path('api/notifications/', NotificationListView.as_view(), name='notifications'),
    path('api/notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]
