# Generated by Django 4.2.16 on 2024-11-08 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_alter_dorm_guest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dorm',
            name='guest',
            field=models.CharField(default=0, max_length=10),
        ),
    ]
