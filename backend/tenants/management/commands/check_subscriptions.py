from django.core.management.base import BaseCommand
from subscriptions.services import process_all_subscriptions

class Command(BaseCommand):
    help = 'Update tenant subscription statuses based on billing dates.'

    def handle(self, *args, **options):
        changes = process_all_subscriptions()
        self.stdout.write(self.style.SUCCESS(f'Subscription check complete ({changes} status changes).'))
