from django.contrib import admin
from .models import Subscription, PaymentRecord, Notification

admin.site.register(Subscription)
admin.site.register(PaymentRecord)
admin.site.register(Notification)
