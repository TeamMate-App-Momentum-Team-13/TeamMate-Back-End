# Generated by Django 4.0.6 on 2022-08-13 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courtaddress',
            old_name='court_address',
            new_name='court',
        ),
        migrations.RenameField(
            model_name='useraddress',
            old_name='user_address',
            new_name='user',
        ),
    ]
