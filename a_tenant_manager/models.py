from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

from a_users.views import User

class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    auto_create_schema = True
    auto_drop_schema = True


class Domain(DomainMixin):
    pass

class TenantMember(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tenant', 'user')
        
    def __str__(self):
        return f"{self.tenant.name} - {self.user.name}{' (Admin)' if self.is_admin else ''}"
