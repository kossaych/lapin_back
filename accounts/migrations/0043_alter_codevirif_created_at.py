# Generated by Django 4.1.1 on 2023-03-31 23:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0042_alter_codevirif_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codevirif',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 31, 23, 31, 35, 836138, tzinfo=datetime.timezone.utc)),
        ),
    ]
