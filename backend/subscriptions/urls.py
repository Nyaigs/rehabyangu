from django.urls import path
from .views import RecordPaymentView, NotificationListView, MarkNotificationReadView

urlpatterns = [
    path('record-payment/', RecordPaymentView.as_view(), name='record-payment'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]
