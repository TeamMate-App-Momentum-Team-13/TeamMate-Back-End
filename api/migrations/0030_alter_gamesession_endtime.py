# Generated by Django 4.0.6 on 2022-08-27 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_alter_gamesession_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesession',
            name='endtime',
            field=models.DateTimeField(),
        ),
    ]
