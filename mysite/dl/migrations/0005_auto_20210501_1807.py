# Generated by Django 3.1.5 on 2021-05-01 22:07

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dl', '0004_auto_20210501_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128)),
                ('enabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='checkoutaddress',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='checkoutaddress',
            name='shipping_country',
            field=django_countries.fields.CountryField(default='CA', max_length=2),
        ),
    ]
