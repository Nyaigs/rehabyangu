from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('users', '0009_audit_immutability')]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='action',
            field=models.CharField(
                choices=[
                    ('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'),
                    ('READ', 'Read'), ('LOGIN', 'Login'), ('LOGOUT', 'Logout'),
                    ('SUSPEND', 'Suspend'), ('REACTIVATE', 'Reactivate'),
                ],
                max_length=20,
            ),
        ),
    ]
