from django.db import models
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from imagekit import ImageSpec, register
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, Transpose, Anchor
from imagekit.utils import get_field_info
from django_countries.fields import CountryField
from django_countries import Countries
import math

from django.utils.translation import gettext_lazy as _



PAYMENT_TYPE = ( ('S', 'Stripe'), ('P', 'Paypal'))

ANCHOR = (
    ('tl', 'TOP LEFT'),
    ('t', 'TOP'),
    ('tr', 'TOP RIGHT'),
    ('bl', 'BOTTOM LEFT'),
    ('b', 'BOTTOM'),
    ('br', 'BOTTOM RIGHT'),
    ('c', 'CENTER'),
    ('l', 'LEFT'),
    ('r', 'RIGHT')
)


class Setting(models.Model):
    name = models.CharField(max_length=128, blank=True)
    enabled = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class NACountries(Countries):
    only = { 'CA': _('Canada'), 'US': _('United States') }

class G8Countries(Countries):
    only = [
        'CA', 'FR', 'DE', 'IT', 'JP', 'RU', 'GB'
    ]

class ProvinceOrState(models.Model):
    name = models.CharField(max_length=128, blank=True)
    code = models.CharField(max_length=2, blank=True)
    rate = models.FloatField(default=0, blank=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=128, blank=True)
    billing_name = models.CharField(max_length=128, blank=True, null=True)
    shipping_name = models.CharField(max_length=128, blank=True, null=True)
    phone = models.CharField(max_length=128, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    billing_street_address = models.CharField(max_length=128, blank=True, null=True)
    billing_apartment_address = models.CharField(max_length=128, blank=True, null=True)
    billing_city = models.CharField(max_length=128, blank=True, null=True)
    billing_state_province = models.CharField(max_length=128, blank=True, null=True)
    billing_postal_zip_code = models.CharField(max_length=128, blank=True, null=True)
    billing_country = models.CharField(max_length=128, blank=True, null=True)
    shipping_street_address= models.CharField(max_length=128, blank=True, null=True)
    shipping_apartment_address= models.CharField(max_length=128, blank=True, null=True)
    shipping_city = models.CharField(max_length=128, blank=True, null=True)
    shipping_state_province = models.CharField(max_length=128, blank=True, null=True)
    shipping_country = models.CharField(max_length=128, blank=True, null=True)
    shipping_postal_zip_code = models.CharField(max_length=128, blank=True, null=True)
    address_is_same = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Gallery(models.Model):
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    description = models.CharField(max_length=2000, default="")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    description = models.CharField(max_length=2000, default="")
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    link_title = models.CharField(max_length=200, blank=True, null=True)
    link_url = models.URLField(max_length = 300, blank=True, null=True)
    def __str__(self):
        return self.title

class ImageThumbnail(ImageSpec):
    processors = [ResizeToFill(600, 600)]
    format = 'JPEG'
    options = {'quality': 60}

    @property
    def processors(self):
        model, field_name = get_field_info(self.source)
        return [ResizeToFill(600, 600, anchor=model.anchor)]

register.generator('dl:image:image_thumbnail', ImageThumbnail)

# class Profile(models.Model):
#     avatar = models.ImageField(upload_to='avatars')
#     avatar_thumbnail = ImageSpecField(source='avatar',
#                                       id='myapp:profile:avatar_thumbnail')
#     thumbnail_width = models.PositiveIntegerField()
#     thumbnail_height = models.PositiveIntegerField()

class Image(models.Model):
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    description = models.CharField(max_length=2000, default="")
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images", default="")
    anchor = models.CharField(choices=ANCHOR, max_length=2, blank=True, null=True)
    thumbnail = ImageSpecField(source='image', id='dl:image:image_thumbnail', processors=[ResizeToFill(600, 600)], format='JPEG', options={'quality':60})
    preview = ImageSpecField(source='image', id='dl:image:image_preview', processors=[ResizeToFit(width=970, upscale=False)], format='JPEG', options={'quality':70})
    # thumbnail = ImageSpecField(source='image', processors=[Transpose(), ResizeToFill(600, 600, anchor=Anchor.BOTTOM)], format='JPEG', options={'quality':60})
    # processors.Thumbnail(width=72, height=72, crop=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    link_title = models.CharField(max_length=200, blank=True, null=True)
    link_url = models.URLField(max_length = 300, blank=True, null=True)

    def save(self, *args, **kwargs):
        #if self.anchor != None:
        self.thumbnail = ImageSpecField(source='image', processors=[ResizeToFill(400, 400, anchor=self.anchor)], format='JPEG', options={'quality':60})
        self.thumbnail.generate()
        super(Image, self).save(*args, **kwargs)

    def __str__(self):
        return self.title



class CheckoutAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    billing_name = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default="")
    province_or_state = models.ForeignKey(ProvinceOrState, models.SET_NULL, blank=True, null=True, related_name='+')
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    shipping_name = models.CharField(max_length=100, default="")
    shipping_street_address = models.CharField(max_length=100, default="")
    shipping_apartment_address = models.CharField(max_length=100, default="")
    shipping_city = models.CharField(max_length=100, default="")
    shipping_province_or_state = models.ForeignKey(ProvinceOrState, models.SET_NULL, blank=True, null=True, related_name='+')
    shipping_country = CountryField(multiple=False, default="CA", blank_label='(select country)')
    shipping_zip = models.CharField(max_length=100, default="")
    address_is_same = models.BooleanField(default=False)
    shipping_amount = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

class Item(models.Model):
    item_name = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    # category = models.CharField(choices=CATEGORY, max_length=2)
    # label = models.CharField(choices=LABEL, max_length=2)
    description = models.TextField()
    image = models.ForeignKey(Image, on_delete=models.CASCADE, default="")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    taxable = models.BooleanField(default=False)
    product_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.item_name

    def get_absolute_url(self):
        return reverse("dl:product", kwargs={
            "pk" : self.pk

        })

    def get_add_to_cart_url(self):
        return reverse("dl:add-to-cart", kwargs={
            "pk" : self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("dl:remove-from-cart", kwargs={
            "pk" : self.pk
        })

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.item_name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    checkout_address = models.ForeignKey(
        'CheckoutAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_amount = models.FloatField(default=0, blank=True, null=True)
    tax_rate = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = 0
        tax_amount = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        self.subtotal = total
        if self.shipping_amount != None:
            shipping_amount = self.shipping_amount
        else:
            shipping_amount = 0
        tax_amount = (total + shipping_amount) * self.tax_rate
        self.tax_amount = tax_amount
        return total + tax_amount + shipping_amount

    def payment_amount(self):
        return self.payment.amount

    def get_tax_rate(self):
        # check whether tax rate as a percentage is a whole number (e.g. 13% vs 14.975%)
        if (self.tax_rate * 100) == (math.ceil(self.tax_rate * 100)):
            # if so return tax rate without decimal place
            return str(int(self.tax_rate * 100))
        else:
            # otherwise return with decimal point
            return str(self.tax_rate * 100)

    def get_item_count(self):
        item_count = 0
        for order_item in self.items.all():
            item_count += order_item.quantity
        return item_count

class Payment(models.Model):
    payment_id = models.CharField(max_length=50)
    # stripe_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(choices=PAYMENT_TYPE, max_length=2, blank=True, null=True)

    def __str__(self):
        return self.user.username

