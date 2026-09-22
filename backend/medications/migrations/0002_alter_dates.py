import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('medications', '0001_initial')]
    operations = [
        migrations.AlterField(model_name='prescription', name='start_at', field=models.DateTimeField(default=django.utils.timezone.now)),
        migrations.AlterField(model_name='medicationadministrationrecord', name='administered_at', field=models.DateTimeField(default=django.utils.timezone.now)),
    ]
