# Generated by Django 5.2 on 2025-04-29 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads_app', '0008_product_service_remove_leads_service_products_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=18.0, help_text='The default tax rate to be applied to all quotations', max_digits=5, verbose_name='Tax Rate (%)')),
            ],
            options={
                'verbose_name': 'Company Settings',
                'verbose_name_plural': 'Company Settings',
            },
        ),
    ]
