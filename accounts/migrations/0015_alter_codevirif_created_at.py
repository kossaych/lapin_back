# Generated by Django 3.2.16 on 2022-12-29 11:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_codevirif_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codevirif',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 29, 11, 20, 4, 272823, tzinfo=utc)),
        ),
    ]
