from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

def _get_request():
    """Try to get the current request (if available) for IP logging."""
    import inspect
    for frame_record in inspect.stack():
        frame = frame_record[0]
        request = frame.f_locals.get('request', None)
        if request:
            return request
    return None

def log_action(instance, action, user=None, tenant=None, description='', ip_address=None):
    if instance and instance.pk:
        content_type = ContentType.objects.get_for_model(instance)
        AuditLog.objects.create(
            actor=user,
            tenant=tenant,
            action=action,
            content_type=content_type,
            object_id=instance.pk,
            description=description,
            ip_address=ip_address or '',
        )

@receiver(post_save, sender='patients.Patient')
def log_patient_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    tenant = getattr(instance, 'tenant', None)
    description = f'Patient {instance.first_name} {instance.last_name} {"created" if created else "updated"}'
    log_action(instance, action, tenant=tenant, description=description)

@receiver(post_delete, sender='patients.Patient')
def log_patient_delete(sender, instance, **kwargs):
    tenant = getattr(instance, 'tenant', None)
    description = f'Patient {instance.first_name} {instance.last_name} deleted'
    log_action(instance, 'DELETE', tenant=tenant, description=description)

@receiver(post_save, sender='appointments.Appointment')
def log_appointment_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    tenant = getattr(instance, 'tenant', None)
    description = f'Appointment for {instance.patient} on {instance.date} {"created" if created else "updated"}'
    log_action(instance, action, tenant=tenant, description=description)

@receiver(post_delete, sender='appointments.Appointment')
def log_appointment_delete(sender, instance, **kwargs):
    tenant = getattr(instance, 'tenant', None)
    description = f'Appointment for {instance.patient} on {instance.date} deleted'
    log_action(instance, 'DELETE', tenant=tenant, description=description)
