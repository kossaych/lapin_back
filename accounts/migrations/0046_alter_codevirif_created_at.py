# Generated by Django 4.1.7 on 2023-04-02 11:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0045_alter_codevirif_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codevirif',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 2, 11, 29, 42, 26677, tzinfo=datetime.timezone.utc)),
        ),
    ]
