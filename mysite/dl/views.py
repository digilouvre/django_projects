from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.views import View
from dl.models import Gallery, Category, Image, Payment, Item, OrderItem, Order, CheckoutAddress, Profile, ProvinceOrState, Setting
from django.views.generic import ListView, DetailView
from dl.owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from django.views.generic.list import MultipleObjectMixin

import stripe
from paypal.standard.forms import PayPalPaymentsForm

from django.core.mail import send_mail

# from django.utils.timezone import now

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from dl.token import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string

from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_KEY

from dl.forms import CreateImageForm, CreateCategoryForm, CreateGalleryForm, CheckoutForm, CreateProductForm, SignUpForm

from .filters import OrderFilter
from django_filters.views import FilterView


def send_contact(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    subject = request.POST.get("subject")
    message = request.POST.get("message")

    send_to_email = settings.ADMIN_EMAIL
    send_mail("New Message From Digi Louvre Contact Form", message, 'noreply@digilouvre.com', [send_to_email], html_message="<html>You received a new message from the Digi Louvre contact form." + "<br>" + "Name: " + name + "<br>" + "Email Address: " + email + "<br>" + "Subject: " + subject + "<br>" + "Message: " + message + "</html>")

    messages.success(request, 'Message Has Been Sent')
    return redirect('dl:contact_page')

def contact_page(request):
    return render(request, "dl/contact.html")

class UserListView(OwnerListView):
    model = Image
    template_name = 'dl/user_list.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'images'  # Default: object_list
    paginate_by = 3
    queryset = Image.objects.all().order_by('-id')  # Default: Model.objects.all()

def paypal_payment(request):
    host = request.get_host()
    order = Order.objects.get(user=request.user, ordered=False)
    taxes_enabled = Setting.objects.filter(name='Taxes').first()
    # *** add descriptive item_name to paypal payment
    amount = order.get_total_price()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': amount,
        'item_name': 'Digi Louvre order',
        'invoice': order.id,
        'currency_code': 'CAD',
        'notify_url': 'http://{}{}'.format(host, reverse('dl:paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('dl:payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('dl:payment_cancelled')),
        "no_shipping": '1',
        }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'dl/paypal-payment.html', {'form': form, 'order': order, 'taxes_enabled':taxes_enabled.enabled})

@csrf_exempt
def payment_done(request):
    messages.success(request, 'Success! Payment processed (Paypal).')
    return redirect('/')


@csrf_exempt
def payment_cancelled(request):
    messages.error(request, 'Payment cancelled (Paypal).')
    return redirect('/')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            # return redirect('dl:change_password')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Digilouvre Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # 'uid': str(user.pk),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject, message, 'noreply@digilouvre.com', [user.email])
            messages.info(request, "Please confirm your email address to complete the registration.")
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        # login(request, user, backend='django.core.mail.backends.console.EmailBackend')
        messages.success(request, "Account verified! Please login to buy images.")

        return redirect('/')
    else:
        messages.error(request, "The confirmation link was invalid, possibly because it has already been used.")
        return redirect('/')




class StripePaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        taxes_enabled = Setting.objects.filter(name='Taxes').first()
        context = {
            'order': order,
            'taxes_enabled' : taxes_enabled.enabled
        }
        return render(self.request, "dl/stripe-payment.html", context)
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total_price() * 100)  #cents
        taxes_enabled = Setting.objects.filter(name='Taxes').first()
        user = self.request.user

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="cad",
                source=token
            )

            # create payment
            payment = Payment()
            # payment.stripe_id = charge['id']
            payment.payment_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_price()
            payment.payment_type = 'S'
            payment.save()

            # assign payment to order
            order.ordered = True
            # *** sets order items to 'ordered' (important!)
            for item in order.items.all():
                item.ordered = True
                item.save()
            order.payment = payment
            order.save()

            messages.success(self.request, "Success! Order processed")

            # current_site = get_current_site(request)

            # ***
            # email receipt to customer
            subject = 'Receipt for order #' + str(order.id) + ' from Digi Louvre'
            message = render_to_string('payment_receipt_email.html', {
                'user': user,
                'order': order,
                'taxes_enabled': taxes_enabled.enabled

            })
            # user.email_user(subject, message)

            # email site owner/admin that order has been processed
            send_mail(subject, message, 'noreply@digilouvre.com', [user.email])

            subject2 = 'Digi Louvre Order #' + str(order.id) + ' payment processed'

            message2 = render_to_string('order_processed_email.html', {
                'user': user,
                'order': order,
                'taxes_enabled': taxes_enabled.enabled

            })
            # user.email_user(subject, message)
            send_mail(subject2, message2, 'noreply@digilouvre.com', [settings.ADMIN_EMAIL])

            return redirect('/')

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "To many request error")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid Parameter")
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentication with stripe failed")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network Error")
            return redirect('/')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong")
            return redirect('/')

        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "Not identified error")
            return redirect('/')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        get_profile = Profile.objects.get(id=self.request.user.profile.id)
        form = CheckoutForm({'billing_name': get_profile.billing_name, 'phone':get_profile.phone, 'street_address': get_profile.billing_street_address,'apartment_address':get_profile.billing_apartment_address,
        'country':get_profile.billing_country, 'city':get_profile.billing_city, 'province_or_state':get_profile.billing_state_province, 'zip':get_profile.billing_postal_zip_code,
        'shipping_street_address':get_profile.shipping_street_address, 'shipping_apartment_address':get_profile.shipping_apartment_address,
        'shipping_name':get_profile.shipping_name, 'shipping_country':get_profile.shipping_country, 'shipping_city':get_profile.shipping_city, 'shipping_province_or_state':get_profile.shipping_state_province,
        'shipping_zip':get_profile.shipping_postal_zip_code, 'same_billing_address':get_profile.address_is_same})
        taxes_enabled = Setting.objects.filter(name='Taxes').first()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order,
            'taxes_enabled': taxes_enabled.enabled
        }
        return render(self.request, 'dl/checkout.html', context)
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        update_profile = Profile.objects.get(id=self.request.user.profile.id)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                billing_name = form.cleaned_data.get('billing_name')
                phone = form.cleaned_data.get('phone')
                shipping_name = form.cleaned_data.get('shipping_name')
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                city = form.cleaned_data.get('city')
                province_or_state = form.cleaned_data.get('province_or_state')
                zip = form.cleaned_data.get('zip')
                shipping_street_address = form.cleaned_data.get('shipping_street_address')
                shipping_apartment_address = form.cleaned_data.get('shipping_apartment_address')
                shipping_country  = form.cleaned_data.get('shipping_country')
                shipping_city = form.cleaned_data.get('shipping_city')
                shipping_province_or_state = form.cleaned_data.get('shipping_province_or_state')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                shipping_amount = form.cleaned_data.get('shipping_amount')


                # TODO: add functionaly for these fields
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                checkout_address = CheckoutAddress(
                    user=self.request.user,
                    billing_name=billing_name,
                    phone=phone,
                    shipping_name=shipping_name,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    city=city,
                    country=country,
                    province_or_state=province_or_state,
                    zip=zip,
                    shipping_street_address=shipping_street_address,
                    shipping_apartment_address=shipping_apartment_address,
                    shipping_city=shipping_city,
                    shipping_province_or_state=shipping_province_or_state,
                    shipping_country=shipping_country,
                    shipping_zip=shipping_zip,
                    address_is_same=same_billing_address
                )
                checkout_address.save()
                order.checkout_address = checkout_address
                taxes_enabled = Setting.objects.filter(name='Taxes').first()
                # if TAXES_ENABLED:
                if taxes_enabled.enabled == True:
                    if same_billing_address or shipping_province_or_state == 0 or shipping_province_or_state == "" or shipping_province_or_state == None:
                        province_state = ProvinceOrState.objects.get(name=province_or_state)
                        order.tax_rate = province_state.rate
                    else:
                        province_state = ProvinceOrState.objects.get(name=shipping_province_or_state)
                        order.tax_rate = province_state.rate
                else:
                    order.tax_rate = 0

                if shipping_amount == None:
                    shipping_amount = 0
                order.shipping_amount = shipping_amount
                order.get_total_price()
                order.save()

                if save_info:
                    # update_profile = Profile.objects.get(id=self.request.user.profile.id)
                    update_profile.user = self.request.user
                    update_profile.billing_name = billing_name
                    update_profile.phone = phone
                    update_profile.shipping_name = shipping_name
                    update_profile.billing_street_address = street_address
                    update_profile.billing_apartment_address = apartment_address
                    update_profile.billing_city = city
                    update_profile.billing_state_province = province_or_state.id
                    update_profile.billing_postal_zip_code = zip
                    update_profile.billing_country = country
                    update_profile.shipping_street_address = shipping_street_address
                    update_profile.shipping_apartment_address = shipping_apartment_address
                    update_profile.shipping_city = shipping_city
                    try:
                        update_profile.shipping_state_province = shipping_province_or_state.id
                    except:
                        update_profile.shipping_state_province = ""
                    update_profile.shipping_country = shipping_country
                    update_profile.shipping_postal_zip_code = shipping_zip
                    update_profile.address_is_same = same_billing_address
                    update_profile.save()

                if payment_option == 'S':
                    return redirect('dl:stripe-payment', payment_option='stripe')
                elif payment_option == 'P':
                    # return redirect('dl:payment', payment_option='paypal')
                    # return redirect('dl:paypal-form')
                    # return redirect('dl:paypal-payment', payment_option='paypal')
                    return redirect('dl:paypal-payment')
                else:
                    messages.warning(self.request, "Invalid Payment option")
                    return redirect('dl:checkout')
# ***
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("dl:order-summary")

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        try:

            order = Order.objects.get(user=self.request.user, ordered=False)
            order.tax_rate = 0
            order.save()
            context = {
                'order': order
            }
            return render(self.request, 'dl/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("/")

@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists() :
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Item quantity was updated")
            return redirect("dl:order-summary")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("dl:order-summary")
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("dl:order-summary")

class HomeView(ListView):
    model = Item
    template_name = "dl/home.html"

class ProductView(DetailView):
    model = Item
    template_name = "dl/product.html"

class ProductListView(OwnerListView):
    model = Item
    # By convention:
    template_name = "dl/product_list.html"
    def get(self, request) :
        product_list = Item.objects.all()
        ctx = {'product_list' : product_list}
        return render(request, self.template_name, ctx)

class ProductCreateView(LoginRequiredMixin, View):
    template_name = 'dl/product_form.html'
    success_url = reverse_lazy('dl:all_products')

    def get(self, request, pk=None):
        form = CreateProductForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateProductForm(request.POST, request.FILES or None)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        product = form.save(commit=False)
        product.owner = self.request.user

        product.save()
        return redirect(self.success_url)

@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added quantity Item")
            return redirect("dl:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart")
            return redirect("dl:order-summary")
    else:
        # from django.utils.timezone import now -- should use now instead of timezone.now()?
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
        return redirect("dl:order-summary")

@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Item \""+order_item.item.item_name+"\" remove from your cart")
            return redirect("dl:order-summary")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("dl:product", pk=pk)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("dl:product", pk = pk)






class DlAboutView(TemplateView):
    template_name = "dl/dl_about.html"

    def get_context_data(self, **kwargs):
        context = super(DlAboutView, self).get_context_data(**kwargs)
        gallery_list = Gallery.objects.all()
        category_list = Category.objects.all()
        context = {'gallery_list': gallery_list, 'category_list': category_list}
        return context

class ImageListView(OwnerListView):
    model = Image
    template_name = "dl/image_list.html"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(ImageListView, self).get_context_data(**kwargs)
        images = Image.objects.all().order_by('-id')
        paginator = Paginator(images, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            image_list = paginator.page(page)
        except PageNotAnInteger:
            image_list = paginator.page(1)
        except EmptyPage:
            image_list = paginator.page(paginator.num_pages)

        context['image_list'] = image_list
        category_list = Category.objects.all()
        context['category_list'] = category_list
        gallery_list = Gallery.objects.all()
        context['image_carousel_list'] = Image.objects.all().order_by('-id')
        context['gallery_list'] = gallery_list
        return context


class OrderListView(ListView, FilterView):
    model = Order
    context_object_name = 'order_list'
    filter_class = OrderFilter
    # By convention:
    template_name = "dl/order_list.html"
    def get(self, request) :
        order_list = Order.objects.all().order_by('-id')
        order_filter = OrderFilter(request.GET, queryset=order_list)
        payment_list = Payment.objects.all()
        total = 0
        order_count = 0
        for order in order_filter.qs:
            if order.ordered:
                total += order.payment.amount
                order_count += 1
        # for item in payment_list:
        #     total += item.amount
        checkout_address = CheckoutAddress.objects.all()
        item_list = Item.objects.all()
        taxes_enabled = Setting.objects.filter(name='Taxes').first()
        ctx = {'order_count':order_count, 'order_filter':order_filter, 'total': total, 'order_list' : order_list, 'payment_list' : payment_list, 'checkout_address': checkout_address, 'item_list' : item_list, 'taxes_enabled' : taxes_enabled.enabled}
        return render(request, self.template_name, ctx)


class OrderDetailView(OwnerDetailView):
    model = Order
    template_name = "dl/order_detail.html"
    def get(self, request, pk) :
        order = Order.objects.get(id=pk)
        taxes_enabled = Setting.objects.filter(name='Taxes').first()
        item_list = OrderItem.objects.all().filter(order=order.id)
        # category_list = Category.objects.all().filter(gallery=gallery.id)
        # gallery_list = Gallery.objects.all()
        context = { 'order' : order, 'item_list' : item_list, 'taxes_enabled':taxes_enabled.enabled}
        return render(request, self.template_name, context)


class CategoryListView(OwnerListView):
    model = Category
    # By convention:
    template_name = "dl/category_list.html"
    def get(self, request) :
        category_list = Category.objects.all()
        gallery_list = Gallery.objects.all()

        ctx = {'category_list' :category_list, 'gallery_list':gallery_list}
        return render(request, self.template_name, ctx)

class GalleryListView(OwnerListView):
    model = Gallery
    # By convention:
    template_name = "dl/gallery_list.html"
    def get(self, request) :
        gallery_list = Gallery.objects.all()
        category_list = Category.objects.all()
        ctx = {'gallery_list' :gallery_list, 'category_list':category_list}
        return render(request, self.template_name, ctx)

class ImageDetailView(OwnerDetailView):
    model = Image
    template_name = "dl/image_detail.html"
    def get(self, request, pk) :
        image = Image.objects.get(id=pk)
        image_list = Image.objects.all()
        gallery_list = Gallery.objects.all()
        category_list = Category.objects.all()
        product_list = Item.objects.all().filter(image=image.id)
        next_image = image_list.filter(pk__gt=image.pk).order_by('pk').first()
        previous_image = image_list.filter(pk__lt=image.pk).order_by('-pk').first()
        context = { 'image' : image, 'gallery_list': gallery_list, 'category_list':category_list, 'product_list':product_list, 'next_image':next_image, 'previous_image':previous_image }
        return render(request, self.template_name, context)

class CategoryDetailView(OwnerDetailView,MultipleObjectMixin):
    model = Category
    template_name = "dl/category_detail.html"
    # context_object_name = 'category'  # Default: object_list
    paginate_by = 3

    def get_context_data(self, **kwargs):
        object_list = Image.objects.filter(category=self.object)
        # context = super(CategoryDetailView, self).get_context_data(category=category, **kwargs)
        context = super(CategoryDetailView, self).get_context_data(object_list=object_list, **kwargs)
        # category = Category.objects.get(id=pk)
        # context['category'] = self.category
        images = Image.objects.all().filter(category=self.object.id).order_by('-id')
        paginator = Paginator(images, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            image_list = paginator.page(page)
        except PageNotAnInteger:
            image_list = paginator.page(1)
        except EmptyPage:
            image_list = paginator.page(paginator.num_pages)
        context['image_list'] = image_list
        category_list = Category.objects.all()
        context['category_list'] = category_list
        gallery_list = Gallery.objects.all()
        context['image_carousel_list'] = Image.objects.filter(category=self.object.id).order_by('-id')
        context['gallery_list'] = gallery_list
        return context

class GalleryDetailView(OwnerDetailView):
    model = Gallery
    template_name = "dl/gallery_detail.html"
    def get(self, request, pk) :
        gallery = Gallery.objects.get(id=pk)
        category_list = Category.objects.all().filter(gallery=gallery.id)
        gallery_list = Gallery.objects.all()
        context = { 'gallery' : gallery, 'category_list':category_list, 'gallery_list': gallery_list}
        return render(request, self.template_name, context)

class ImageCreateView(LoginRequiredMixin, View):
    template_name = 'dl/image_form.html'
    success_url = reverse_lazy('dl:all')

    def get(self, request, pk=None):
        form = CreateImageForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateImageForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        image = form.save(commit=False)
        image.owner = self.request.user

        image.save()
        return redirect(self.success_url)

class CategoryCreateView(LoginRequiredMixin, View):
    template_name = 'dl/category_form.html'
    success_url = reverse_lazy('dl:all_categories')

    def get(self, request, pk=None):
        form = CreateCategoryForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateCategoryForm(request.POST, request.FILES or None)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        category = form.save(commit=False)
        category.owner = self.request.user

        category.save()
        return redirect(self.success_url)

class GalleryCreateView(LoginRequiredMixin, View):
    template_name = 'dl/gallery_form.html'
    success_url = reverse_lazy('dl:all_galleries')

    def get(self, request, pk=None):
        form = CreateGalleryForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateGalleryForm(request.POST, request.FILES or None)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        gallery = form.save(commit=False)
        gallery.owner = self.request.user

        gallery.save()
        return redirect(self.success_url)

class ImageUpdateView(LoginRequiredMixin, View):
    template_name = 'dl/image_form.html'
    success_url = reverse_lazy('dl:all')

    def get(self, request, pk):
        image = get_object_or_404(Image, id=pk, owner=self.request.user)
        form = CreateImageForm(instance=image)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        image = get_object_or_404(Image, id=pk, owner=self.request.user)
        form = CreateImageForm(request.POST, request.FILES or None, instance=image)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        image.thumbnail.generate()
        image = form.save(commit=False)

        image.save()

        return redirect(self.success_url)

class ProductUpdateView(LoginRequiredMixin, View):
    template_name = 'dl/product_form.html'
    success_url = reverse_lazy('dl:all_products')

    def get(self, request, pk):
        product = get_object_or_404(Item, id=pk, owner=self.request.user)
        form = CreateProductForm(instance=product)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        product = get_object_or_404(Item, id=pk, owner=self.request.user)
        form = CreateProductForm(request.POST, request.FILES or None, instance=product)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        product = form.save(commit=False)
        product.save()

        return redirect(self.success_url)

class CategoryUpdateView(LoginRequiredMixin, View):
    template_name = 'dl/category_form.html'
    success_url = reverse_lazy('dl:all_categories')

    def get(self, request, pk):
        category = get_object_or_404(Category, id=pk, owner=self.request.user)
        form = CreateCategoryForm(instance=category)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        category = get_object_or_404(Category, id=pk, owner=self.request.user)
        form = CreateCategoryForm(request.POST, request.FILES or None, instance=category)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        category = form.save(commit=False)
        category.save()

        return redirect(self.success_url)

class GalleryUpdateView(LoginRequiredMixin, View):
    template_name = 'dl/gallery_form.html'
    success_url = reverse_lazy('dl:all_galleries')

    def get(self, request, pk):
        gallery = get_object_or_404(Gallery, id=pk, owner=self.request.user)
        form = CreateGalleryForm(instance=gallery)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        gallery = get_object_or_404(Gallery, id=pk, owner=self.request.user)
        form = CreateGalleryForm(request.POST, request.FILES or None, instance=gallery)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        gallery = form.save(commit=False)
        gallery.save()

        return redirect(self.success_url)

class ImageDeleteView(OwnerDeleteView):
    model = Image

class CategoryDeleteView(OwnerDeleteView):
    model = Category

class GalleryDeleteView(OwnerDeleteView):
    model = Gallery

class ProductDeleteView(OwnerDeleteView):
    model = Item





