from django.db import models
from tenants.models import Tenant

class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.codename

class Role(models.Model):
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return self.name
