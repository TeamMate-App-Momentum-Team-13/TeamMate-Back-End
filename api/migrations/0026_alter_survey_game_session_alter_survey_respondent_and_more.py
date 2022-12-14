# Generated by Django 4.0.6 on 2022-08-24 23:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_survey_surveyresponse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='game_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey', to='api.gamesession'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='respondent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='response',
            field=models.CharField(choices=[('No Show', 'No Show'), ('Winner', 'Winner'), ('Block User', 'Block User'), ('High Quality', 'High Quality'), ('Average Quality', 'Average Quality'), ('Poor Quality', 'Poor Quality')], max_length=25),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='survey_response', to='api.survey'),
        ),
    ]
