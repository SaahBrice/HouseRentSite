# Generated by Django 5.1.1 on 2024-09-11 11:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0004_rating_property_rated'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingreservation',
            name='property',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rental.property', verbose_name='Propriété'),
        ),
    ]
