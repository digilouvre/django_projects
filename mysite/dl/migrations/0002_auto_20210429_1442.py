# Generated by Django 3.1.5 on 2021-04-29 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dl', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_amount',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
