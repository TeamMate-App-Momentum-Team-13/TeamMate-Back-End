# Generated by Django 4.0.6 on 2022-08-18 13:05

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_guest_unique_game_sessoin_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='game_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest', to='api.gamesession'),
        ),
    ]
