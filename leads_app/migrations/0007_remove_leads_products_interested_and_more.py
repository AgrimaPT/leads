# Generated by Django 5.2 on 2025-04-25 10:35

import multiselectfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads_app', '0006_product_service_remove_leads_service_products_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leads',
            name='products_interested',
        ),
        migrations.RemoveField(
            model_name='leads',
            name='services_want',
        ),
        migrations.AddField(
            model_name='leads',
            name='service_products',
            field=models.JSONField(blank=True, help_text='Dictionary mapping services to selected products', null=True),
        ),
        migrations.DeleteModel(
            name='Product',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.AddField(
            model_name='leads',
            name='services_want',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('digital_marketing', 'Digital Marketing'), ('software', 'Software'), ('web_development', 'Web Development'), ('graphic_design', 'Graphic Design')], max_length=57),
        ),
    ]
