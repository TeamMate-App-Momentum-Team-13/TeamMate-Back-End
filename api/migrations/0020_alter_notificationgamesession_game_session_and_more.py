# Generated by Django 4.0.6 on 2022-08-22 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_notificationgamesession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationgamesession',
            name='game_session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_session', to='api.gamesession'),
        ),
        migrations.AlterField(
            model_name='notificationgamesession',
            name='message',
            field=models.TextField(),
        ),
    ]
