
from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

class Leads(models.Model):
    STATUS_CHOICES = [
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
        ('closed', 'Closed'),
    ]

    SERVICE_CHOICES = [
        ('digital_marketing', 'Digital Marketing'),
        ('software', 'Software'),
        ('web_development', 'Web Development'),
        ('graphic_design', 'Graphic Design'),
        # Add more services as needed
    ]

    SHOP_TYPE_CHOICES = [
        ('supermarket', 'Supermarket'),
        ('saloon', 'Saloon'),
        ('restaurant', 'Restaurant'),
        ('clothing', 'Clothing Store'),
        ('electronics', 'Electronics Store'),
        # Add more shop types as needed
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    shop_name = models.CharField(max_length=100)
    shop_type = models.CharField(max_length=50, choices=SHOP_TYPE_CHOICES)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    services_want = MultiSelectField(choices=SERVICE_CHOICES, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}-{self.name} - {self.shop_name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'