# Generated by Django 5.1.3 on 2024-11-27 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicenow', '0003_alter_hardwareassetsservicenow_asset_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hardwareassetsservicenow',
            name='serial_number',
            field=models.CharField(max_length=255),
        ),
    ]
