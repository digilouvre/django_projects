# Generated by Django 3.1.5 on 2021-04-29 18:15

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(2, 'Title must be greater than 2 characters')])),
                ('description', models.CharField(default='', max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='CheckoutAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_name', models.CharField(blank=True, default='', max_length=100)),
                ('phone', models.CharField(blank=True, default='', max_length=50)),
                ('street_address', models.CharField(max_length=100)),
                ('apartment_address', models.CharField(max_length=100)),
                ('city', models.CharField(default='', max_length=100)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('zip', models.CharField(max_length=100)),
                ('shipping_name', models.CharField(default='', max_length=100)),
                ('shipping_street_address', models.CharField(default='', max_length=100)),
                ('shipping_apartment_address', models.CharField(default='', max_length=100)),
                ('shipping_city', models.CharField(default='', max_length=100)),
                ('shipping_country', django_countries.fields.CountryField(default='CA', max_length=2)),
                ('shipping_zip', models.CharField(default='', max_length=100)),
                ('address_is_same', models.BooleanField(default=False)),
                ('shipping_amount', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(2, 'Title must be greater than 2 characters')])),
                ('description', models.CharField(default='', max_length=2000)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(2, 'Title must be greater than 2 characters')])),
                ('description', models.CharField(default='', max_length=2000)),
                ('image', models.ImageField(default='', upload_to='images')),
                ('anchor', models.CharField(blank=True, choices=[('tl', 'TOP LEFT'), ('t', 'TOP'), ('tr', 'TOP RIGHT'), ('bl', 'BOTTOM LEFT'), ('b', 'BOTTOM'), ('br', 'BOTTOM RIGHT'), ('c', 'CENTER'), ('l', 'LEFT'), ('r', 'RIGHT')], max_length=2, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dl.category')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dl.gallery')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('discount_price', models.FloatField(blank=True, null=True)),
                ('description', models.TextField()),
                ('taxable', models.BooleanField(default=False)),
                ('image', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='dl.image')),
                ('owner', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProvinceOrState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128)),
                ('code', models.CharField(blank=True, max_length=2)),
                ('rate', models.FloatField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128)),
                ('billing_name', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_name', models.CharField(blank=True, max_length=128, null=True)),
                ('phone', models.CharField(blank=True, max_length=128, null=True)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('billing_street_address', models.CharField(blank=True, max_length=128, null=True)),
                ('billing_apartment_address', models.CharField(blank=True, max_length=128, null=True)),
                ('billing_city', models.CharField(blank=True, max_length=128, null=True)),
                ('billing_state_province', models.CharField(blank=True, max_length=128, null=True)),
                ('billing_postal_zip_code', models.CharField(blank=True, max_length=128, null=True)),
                ('billing_country', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_street_address', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_apartment_address', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_city', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_state_province', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_country', models.CharField(blank=True, max_length=128, null=True)),
                ('shipping_postal_zip_code', models.CharField(blank=True, max_length=128, null=True)),
                ('address_is_same', models.BooleanField(default=False)),
                ('user', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=50)),
                ('amount', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('payment_type', models.CharField(blank=True, choices=[('S', 'Stripe'), ('P', 'Paypal')], max_length=2, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('quantity', models.IntegerField(default=1)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dl.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('ordered_date', models.DateTimeField()),
                ('ordered', models.BooleanField(default=False)),
                ('shipping_amount', models.FloatField(blank=True, default=0)),
                ('tax_rate', models.FloatField(default=0)),
                ('tax_amount', models.FloatField(default=0)),
                ('subtotal', models.FloatField(default=0)),
                ('checkout_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dl.checkoutaddress')),
                ('items', models.ManyToManyField(to='dl.OrderItem')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dl.payment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='checkoutaddress',
            name='province_or_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dl.provinceorstate'),
        ),
        migrations.AddField(
            model_name='checkoutaddress',
            name='shipping_province_or_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dl.provinceorstate'),
        ),
        migrations.AddField(
            model_name='checkoutaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='category',
            name='gallery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dl.gallery'),
        ),
        migrations.AddField(
            model_name='category',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
