# Generated manually to preserve the existing migration history.
from django.db import migrations, models


def create_standard_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    defaults = {
        'starter': ('Starter', 'Essential care operations for small facilities.', '5000.00', 5),
        'professional': ('Professional', 'Operational tools for growing rehabilitation centres.', '20000.00', 25),
        'enterprise': ('Enterprise', 'Full platform capability for multi-facility operations.', '50000.00', None),
    }
    for code, (name, description, price, maximum) in defaults.items():
        SubscriptionPlan.objects.get_or_create(code=code, defaults={
            'name': name, 'description': description, 'price_monthly': price,
            'max_users': maximum, 'feature_flags': {}, 'is_active': True,
        })


class Migration(migrations.Migration):
    dependencies = [('subscriptions', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('price_monthly', models.DecimalField(decimal_places=2, max_digits=12)),
                ('max_users', models.PositiveIntegerField(blank=True, null=True)),
                ('feature_flags', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['price_monthly', 'name']},
        ),
        migrations.AddField(
            model_name='notification', name='event_key',
            field=models.CharField(blank=True, max_length=160, null=True, unique=True),
        ),
        migrations.RunPython(create_standard_plans, migrations.RunPython.noop),
    ]
