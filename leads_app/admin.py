from django.contrib import admin
from .models import LeadProduct, Leads,Product,Service,CompanyProfile,Employee
# Register your models here.

admin.site.register(Leads)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(CompanyProfile)
admin.site.register(Employee)
admin.site.register(LeadProduct)
