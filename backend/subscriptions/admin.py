from django.contrib import admin
from .models import Subscription, PaymentRecord, Notification, SubscriptionPlan

admin.site.register(Subscription)
admin.site.register(PaymentRecord)
admin.site.register(Notification)
admin.site.register(SubscriptionPlan)
