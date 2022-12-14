# Generated by Django 4.0.6 on 2022-08-13 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressModelMixin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('address1', models.CharField(max_length=250)),
                ('address2', models.CharField(blank=True, max_length=250, null=True)),
                ('city', models.CharField(max_length=250)),
                ('state', models.CharField(max_length=250)),
                ('zipcode', models.CharField(max_length=5)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
