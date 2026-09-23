from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tenants', '0010_tenant_archived_at')]

    operations = [
        migrations.AddField(model_name='tenantconfig', name='mpesa_shortcode', field=models.CharField(blank=True, max_length=50)),
        migrations.AddField(model_name='tenantconfig', name='mpesa_shortcode_type', field=models.CharField(choices=[('paybill', 'Paybill'), ('till', 'Till')], default='paybill', max_length=10)),
        migrations.AddField(model_name='tenantconfig', name='mpesa_consumer_key', field=models.TextField(blank=True)),
        migrations.AddField(model_name='tenantconfig', name='mpesa_consumer_secret', field=models.TextField(blank=True)),
        migrations.AddField(model_name='tenantconfig', name='mpesa_passkey', field=models.TextField(blank=True)),
        migrations.AddField(model_name='tenantconfig', name='mpesa_account_prefix', field=models.CharField(default='INV', max_length=20)),
        migrations.AddField(model_name='tenantconfig', name='kra_pin', field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name='tenantconfig', name='vat_registered', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='tenantconfig', name='vat_number', field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name='tenantconfig', name='bank_name', field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name='tenantconfig', name='bank_account_name', field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name='tenantconfig', name='bank_account_number', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='tenantconfig', name='bank_branch', field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name='tenantconfig', name='invoice_prefix', field=models.CharField(default='INV', max_length=20)),
        migrations.AddField(model_name='tenantconfig', name='next_invoice_number', field=models.PositiveIntegerField(default=1)),
        migrations.AddField(model_name='tenantconfig', name='invoice_terms', field=models.TextField(blank=True)),
        migrations.AddField(model_name='tenantconfig', name='invoice_footer_text', field=models.TextField(blank=True)),
    ]
