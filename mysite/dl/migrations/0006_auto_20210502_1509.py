# Generated by Django 3.1.5 on 2021-05-02 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dl', '0005_auto_20210501_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='link_title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='link_url',
            field=models.URLField(blank=True, max_length=300, null=True),
        ),
    ]
