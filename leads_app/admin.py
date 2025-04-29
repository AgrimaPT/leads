from django.contrib import admin
from .models import Leads,Product,Service,CompanySettings
# Register your models here.

admin.site.register(Leads)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(CompanySettings)
