# Generated by Django 5.2 on 2025-05-10 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads_app', '0015_alter_companyprofile_options_alter_product_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
