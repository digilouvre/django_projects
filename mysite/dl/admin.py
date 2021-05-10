from django.contrib import admin

from dl.models import Gallery, Category, Image, Payment, Item, OrderItem, Order, CheckoutAddress, Profile, ProvinceOrState, Setting

admin.site.register(Gallery)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Payment)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(CheckoutAddress)
admin.site.register(Profile)
admin.site.register(ProvinceOrState)
admin.site.register(Setting)