# Generated by Django 4.0.6 on 2022-08-13 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_rename_locatation_gamesession_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesession',
            name='match_type',
            field=models.CharField(choices=[('Singles', 'Singles'), ('Doubles', 'Doubles')], default='Singles', max_length=250),
        ),
    ]
