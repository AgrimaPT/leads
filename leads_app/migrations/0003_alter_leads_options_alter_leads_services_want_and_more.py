# Generated by Django 5.2 on 2025-04-21 13:47

import multiselectfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads_app', '0002_leads_delete_lead'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leads',
            options={'ordering': ['-created_at'], 'verbose_name': 'Lead', 'verbose_name_plural': 'Leads'},
        ),
        migrations.AlterField(
            model_name='leads',
            name='services_want',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('digital_marketing', 'Digital Marketing'), ('software', 'Software'), ('web_development', 'Web Development'), ('graphic_design', 'Graphic Design')], max_length=57),
        ),
        migrations.AlterField(
            model_name='leads',
            name='shop_type',
            field=models.CharField(choices=[('supermarket', 'Supermarket'), ('saloon', 'Saloon'), ('restaurant', 'Restaurant'), ('clothing', 'Clothing Store'), ('electronics', 'Electronics Store')], max_length=50),
        ),
        migrations.AlterField(
            model_name='leads',
            name='status',
            field=models.CharField(choices=[('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold'), ('closed', 'Closed')], default='cold', max_length=10),
        ),
    ]
