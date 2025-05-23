# Generated by Django 5.2 on 2025-05-12 12:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads_app', '0017_employee_profile_pic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leads',
            name='products_interested',
        ),
        migrations.AddField(
            model_name='product',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='product_photos/'),
        ),
        migrations.AlterField(
            model_name='leads',
            name='status',
            field=models.CharField(blank=True, choices=[('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold'), ('closed', 'Closed'), ('lost', 'lost')], max_length=10, null=True),
        ),
        migrations.CreateModel(
            name='LeadProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads_app.leads')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads_app.product')),
            ],
            options={
                'unique_together': {('lead', 'product')},
            },
        ),
    ]
