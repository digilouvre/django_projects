# Generated by Django 3.1.5 on 2021-05-06 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dl', '0006_auto_20210502_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='link_title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='link_url',
            field=models.URLField(blank=True, max_length=300, null=True),
        ),
    ]
