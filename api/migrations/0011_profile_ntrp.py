# Generated by Django 4.0.6 on 2022-08-16 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_gamesession_match_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='ntrp',
            field=models.CharField(choices=[('2.5', '2.5'), ('3', '3'), ('3.5', '3.5'), ('4', '4'), ('4.5', '4.5'), ('5', '5'), ('5.5', '5.5'), ('6', '6'), ('6.5', '6.5'), ('7', '7')], default='2.5', max_length=10),
        ),
    ]
