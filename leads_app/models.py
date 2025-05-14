from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.db.models import JSONField
from django.utils import timezone


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255,default='name')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=18.00,
        verbose_name="Tax Rate (%)",
        help_text="The default tax rate to be applied to all quotations"
    )
    
    class Meta:
        
        verbose_name = 'CompanyProfile'
        verbose_name_plural = 'CompanyProfiles'
    
    def __str__(self):
        return f"{self.company_name}"
    

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    # company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='employees')
    # role = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='employee_profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"


class Service(models.Model):
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True,blank=True)

    # def save(self, *args, **kwargs):
    #     if not self.code:
    #         # Example: Auto code with prefix "SRV" + 4-digit number
    #         last_id = Service.objects.all().count() + 1
    #         self.code = f"SRV{last_id:04d}"
    #     super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        if not self.code:
            # Get the highest code and increment it
            last_service = Service.objects.all().order_by('-code').first()
            if last_service:
                last_id = int(last_service.code[3:]) + 1  # Assuming 'SRV' is the prefix
            else:
                last_id = 1
            self.code = f"SRV{last_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    code = models.SlugField(unique=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='product_photos/', blank=True, null=True)  # New photo field

    def save(self, *args, **kwargs):
        if not self.code:
            # Get the highest code and increment it
            last_product = Product.objects.all().order_by('-code').first()
            if last_product:
                last_id = int(last_product.code[3:]) + 1  # Assuming 'PRD' is the prefix
            else:
                last_id = 1
            self.code = f"PRD{last_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.service.name}"
    
class Leads(models.Model):
    STATUS_CHOICES = [
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
        ('closed', 'Closed'),
        ('lost','lost')
    ]

  
    SHOP_TYPE_CHOICES = [
        ('supermarket', 'Supermarket'),
        ('saloon', 'Saloon'),
        ('restaurant', 'Restaurant'),
        ('clothing', 'Clothing Store'),
        ('electronics', 'Electronics Store'),
    ]
    # company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='leads')
    # assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    
    location = models.CharField(max_length=100, blank=True, null=True)
    shop_type = models.CharField(max_length=50, choices=SHOP_TYPE_CHOICES, blank=True, null=True)
    
    lead_image = models.ImageField(upload_to='lead_images/', blank=True, null=True)
    services_want = models.ManyToManyField(Service, blank=True)
    products_interested = models.ManyToManyField(Product, blank=True,through='LeadProduct')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True) 
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.name} - {self.shop_name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    @property
    def is_follow_up_due(self):
        if self.follow_up_date:
            return self.follow_up_date < timezone.now().date()
        return False

    # def get_products_for_service(self, service_code):
    #     """Helper method to get products for a specific service"""
    #     return self.SERVICE_PRODUCTS.get(service_code, [])
    

class LeadProduct(models.Model):
    lead = models.ForeignKey('Leads', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('lead', 'product')