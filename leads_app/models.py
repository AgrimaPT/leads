
# from django.db import models
# from django.contrib.auth.models import User
# from multiselectfield import MultiSelectField

# class Leads(models.Model):
#     STATUS_CHOICES = [
#         ('hot', 'Hot'),
#         ('warm', 'Warm'),
#         ('cold', 'Cold'),
#         ('closed', 'Closed'),
#     ]

#     SERVICE_CHOICES = [
#         ('digital_marketing', 'Digital Marketing'),
#         ('software', 'Software'),
#         ('web_development', 'Web Development'),
#         ('graphic_design', 'Graphic Design'),
#         # Add more services as needed
#     ]

#     SHOP_TYPE_CHOICES = [
#         ('supermarket', 'Supermarket'),
#         ('saloon', 'Saloon'),
#         ('restaurant', 'Restaurant'),
#         ('clothing', 'Clothing Store'),
#         ('electronics', 'Electronics Store'),
#         # Add more shop types as needed
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=20)
#     shop_name = models.CharField(max_length=100,blank=True, null=True)
#     shop_type = models.CharField(max_length=50, choices=SHOP_TYPE_CHOICES,blank=True, null=True)
#     location = models.CharField(max_length=100,blank=True, null=True)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES,blank=True, null=True)
#     services_want = MultiSelectField(choices=SERVICE_CHOICES, blank=True)
#     remarks = models.TextField(blank=True,null=True)
#     follow_up_date = models.DateField(blank=True, null=True) 
#     created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)

#     def __str__(self):
#         return f"{self.user.username}-{self.name} - {self.shop_name}"

#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = 'Lead'
#         verbose_name_plural = 'Leads'


from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.db.models import JSONField



class Service(models.Model):
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.service.name}"
    
class Leads(models.Model):
    STATUS_CHOICES = [
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
        ('closed', 'Closed'),
    ]

    # SERVICE_CHOICES = [
    #     ('digital_marketing', 'Digital Marketing'),
    #     ('software', 'Software'),
    #     ('web_development', 'Web Development'),
    #     ('graphic_design', 'Graphic Design'),
    # ]
    
    # Define products for each service
    # SERVICE_PRODUCTS = {
    #     'digital_marketing': [
    #         ('seo', 'SEO'),
    #         ('social_media', 'Social Media Marketing'),
    #         ('ppc', 'Pay-Per-Click Advertising'),
    #         ('email_marketing', 'Email Marketing'),
    #     ],
    #     'software': [
    #         ('erp', 'ERP Software'),
    #         ('crm', 'CRM Software'),
    #         ('inventory', 'Inventory Management'),
    #     ],
    #     'web_development': [
    #         ('ecommerce', 'E-commerce Website'),
    #         ('blog', 'Blog Website'),
    #         ('portfolio', 'Portfolio Website'),
    #     ],
    #     'graphic_design': [
    #         ('logo', 'Logo Design'),
    #         ('brochure', 'Brochure Design'),
    #         ('social_media_graphics', 'Social Media Graphics'),
    #     ],
    # }

    SHOP_TYPE_CHOICES = [
        ('supermarket', 'Supermarket'),
        ('saloon', 'Saloon'),
        ('restaurant', 'Restaurant'),
        ('clothing', 'Clothing Store'),
        ('electronics', 'Electronics Store'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    
    location = models.CharField(max_length=100, blank=True, null=True)
    shop_type = models.CharField(max_length=50, choices=SHOP_TYPE_CHOICES, blank=True, null=True)
    
    # services_want = MultiSelectField(choices=SERVICE_CHOICES, blank=True)
    # service_products = JSONField(
    #     blank=True, 
    #     null=True,
    #     help_text="Dictionary mapping services to selected products"
    # )
    services_want = models.ManyToManyField(Service, blank=True)
    products_interested = models.ManyToManyField(Product, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True) 
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}-{self.name} - {self.shop_name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def get_products_for_service(self, service_code):
        """Helper method to get products for a specific service"""
        return self.SERVICE_PRODUCTS.get(service_code, [])
    


class CompanySettings(models.Model):
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=18.00,
        verbose_name="Tax Rate (%)",
        help_text="The default tax rate to be applied to all quotations"
    )
    
    class Meta:
        verbose_name = "Company Settings"
        verbose_name_plural = "Company Settings"
    
    def __str__(self):
        return f"Company Settings (Tax Rate: {self.tax_rate}%)"
    
    @classmethod
    def load(cls):
        """Get or create the single CompanySettings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj