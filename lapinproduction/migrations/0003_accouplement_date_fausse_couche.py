# Generated by Django 4.1.1 on 2022-10-30 14:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lapinproduction', '0002_alter_accouplement_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='accouplement',
            name='date_fausse_couche',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
