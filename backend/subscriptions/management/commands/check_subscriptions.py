from django.core.management.base import BaseCommand
from subscriptions.services import process_all_subscriptions

class Command(BaseCommand):
    help = 'Check subscription statuses and update tenant statuses, send notifications'

    def handle(self, *args, **options):
        changes = process_all_subscriptions()
        self.stdout.write(self.style.SUCCESS(f'Subscription check completed ({changes} status changes).'))
