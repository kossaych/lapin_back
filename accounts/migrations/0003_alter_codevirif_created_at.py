# Generated by Django 4.1.1 on 2022-10-14 17:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_codevirif_created_at_generalconfig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codevirif',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 14, 17, 50, 4, 286915, tzinfo=datetime.timezone.utc)),
        ),
    ]
