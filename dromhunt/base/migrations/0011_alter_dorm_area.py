# Generated by Django 4.2.16 on 2024-11-07 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_amenity_icon_url_location_city_location_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dorm',
            name='area',
            field=models.DecimalField(decimal_places=2, help_text='Area in square feet', max_digits=10, null=True),
        ),
    ]