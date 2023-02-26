# Generated by Django 4.1.6 on 2023-02-19 15:58

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0027_alter_codevirif_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codevirif',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 19, 15, 58, 8, 557293, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Moyenne_poid_malle', models.IntegerField(default=3500)),
                ('Moyenne_poid_femalle', models.IntegerField(default=3000)),
                ('Moyenne_production_annuelle', models.IntegerField(default=50)),
                ('Moyenne_poid_2moi', models.IntegerField(default=3500)),
                ('Moyenne_production_par_accouplement', models.IntegerField(default=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
