# Generated by Django 5.1.7 on 2025-04-06 14:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20210322_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(3, 'Название должно содержать минимум 3 символа'), django.core.validators.MaxLengthValidator(200, 'Название не должно превышать 200 символов')]),
        ),
    ]
