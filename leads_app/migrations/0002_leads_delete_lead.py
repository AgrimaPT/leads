# Generated by Django 5.2 on 2025-04-21 06:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Leads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('shop_name', models.CharField(max_length=100)),
                ('shop_type', models.CharField(choices=[('supermarket', 'Supermarket'), ('saloon', 'Saloon'), ('restaurant', 'Restaurant')], max_length=50)),
                ('location', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold'), ('closed', 'Closed')], max_length=10)),
                ('services_want', models.CharField(choices=[('digital_marketing', 'Digital Marketing'), ('software', 'Software')], max_length=50)),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Lead',
        ),
    ]
