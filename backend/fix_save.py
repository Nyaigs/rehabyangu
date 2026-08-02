import re

with open('users/models.py', 'r') as f:
    content = f.read()

new_save = '''\
    def save(self, *args, **kwargs):
        if not self.tenant_user_id and self.tenant_id:
            abbreviation = self.tenant.subdomain[:3].upper()
            from django.db.models import Max
            from django.db.models.functions import Substr
            last = TenantMembership.objects.filter(
                tenant=self.tenant,
                tenant_user_id__startswith=abbreviation
            ).annotate(
                num=Substr('tenant_user_id', len(abbreviation)+2, 3)
            ).aggregate(max_num=Max('num'))['max_num']
            next_num = 1 if last is None else int(last) + 1
            self.tenant_user_id = f"{abbreviation}-{next_num:03d}"
        super().save(*args, **kwargs)'''

# Replace the old save method with the new one
# We match from 'def save(self' to the next non-indented line (next class or EOF)
pattern = r'    def save\(self.*?\)\n(?:        .*\n)*'
content = re.sub(pattern, new_save, content, count=1)

with open('users/models.py', 'w') as f:
    f.write(content)
print('save method replaced successfully')
