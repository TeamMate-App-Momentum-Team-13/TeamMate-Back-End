# Generated by Django 4.0.6 on 2022-08-29 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_profile_wins'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='wins',
            new_name='wins_losses',
        ),
    ]
