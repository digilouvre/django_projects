from django import forms
from django.core.exceptions import ValidationError
from django.core import validators
from dl.models import Gallery, Category, Image, Item, ProvinceOrState
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.core.files.uploadedfile import InMemoryUploadedFile
#from django.core import serializers


PROVINCES_AND_STATES = (
    ('Alberta',	'AB'),
    ('British Columbia', 'BC'),
    ('Manitoba', 'MB'),
    ('New Brunswick', 'NB'),
    ('Newfoundland and Labrador','NL'),
    ('Northwest Territories', 'NT'),
    ('Nova Scotia', 'NS'),
    ('Nunavut',	'NU'),
    ('Ontario',	'ON'),
    ('Prince Edward Island', 'PE'),
    ('Quebec','QC'),
    ('Saskatchewan', 'SK'),
    ('Yukon', 'YT'),
    ('Alabama', 'AL'),
    ('Alaska','AK'),
    # ('American Samoa', 'AS')
    ('Arizona',	'AZ'),
    ('Arkansas','AR'),
    ('California','CA'),
    ('Colorado','CO'),
    ('Connecticut','CT'),
    ('Delaware','DE'),
    ('District of Columbia','DC'),
    ('Federated States of Micronesia','FM'),
    ('Florida','FL'),
    ('Georgia','GA'),
    # ('Guam','GU'),
    ('Hawaii','HI'),
    ('Idaho','ID'),
    ('Illinois','IL'),
    ('Indiana','IN'),
    ('Iowa','IA'),
    ('Kansas','KS'),
    ('Kentucky','KY'),
    ('Louisiana','LA'),
    ('Maine','ME'),
    # ('Marshall Islands','MH'),
    ('Maryland','MD'),
    ('Massachusetts','MA'),
    ('Michigan','MI'),
    ('Minnesota','MN'),
    ('Mississippi','MS'),
    ('Missouri','MO'),
    ('Montana','MT'),
    ('Nebraska','NE'),
    ('Nevada','NV'),
    ('New Hampshire','NH'),
    ('New Jersey','NJ'),
    ('New Mexico','NM'),
    ('New York','NY'),
    ('North Carolina','NC'),
    ('North Dakota', 'ND'),
    # ('Northern Mariana Islands','MP'),
    ('Ohio','OH'),
    ('Oklahoma','OK'),
    ('Oregon','OR'),
    ('Palau','PW'),
    ('Pennsylvania','PA'),
    ('Puerto Rico','PR'),
    ('Rhode Island','RI'),
    ('South Carolina','SC'),
    ('South Dakota','SD'),
    ('Tennessee','TN'),
    ('Texas','TX'),
    ('Utah', 'UT'),
    ('Vermont',	'VT'),
    ('Virgin Islands','VI'),
    ('Virginia', 'VA'),
    ('Washington','WA'),
    ('West Virginia','WV'),
    ('Wisconsin','WI'),
    ('Wyoming','WY'),
)

PAYMENT = (
    ('S', 'Credit Card (Stripe)'),
    ('P', 'PayPal')
)


class SignUpForm(UserCreationForm):
    # birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class CheckoutForm(forms.Form):
    billing_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone'}))

    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '1234 Main St'
    }))

    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apartment or suite'
    }))

    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        # 'class': 'custom-select d-block w-100'
        'class' : 'form-control'
    }))
    # country = CountryField(blank_label='(select country)').formfield()

    # country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
    #     # 'class': 'custom-select d-block w-100'
    #     'class' : 'form-control'
    # }))

    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    # province_or_state =forms.CharField(widget=forms.TextInput(attrs={
    #     'class': 'form-control'
    # }))

    province_or_state = forms.ModelChoiceField(queryset=ProvinceOrState.objects.all(), empty_label="(Province/State)", widget=forms.Select(attrs={
        'class': 'form-control'
    }))

    # province_or_state = forms.ChoiceField(choices=PROVINCES_AND_STATES, required=False, widget=forms.Select(attrs={
    #     'class': 'form-control'
    # }))

    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    shipping_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    shipping_street_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '1234 Main St'
    }))

    shipping_apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apartment or suite'
    }))

    shipping_country = CountryField(blank=True, blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        # 'class': 'custom-select d-block w-100'
        'class' : 'form-control'
    }))

    shipping_city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    # shipping_province_or_state =forms.CharField(required=False, widget=forms.TextInput(attrs={
    #     'class': 'form-control'
    # }))

    shipping_province_or_state = forms.ModelChoiceField(required=False, queryset=ProvinceOrState.objects.all(), empty_label="(Province/State)", widget=forms.Select(attrs={
        'class': 'form-control'
    }))

    # shipping_province_or_state =forms.ChoiceField(choices=PROVINCES_AND_STATES, required=False, widget=forms.Select(attrs={
    #     'class': 'form-control'
    # }))

    shipping_zip = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    shipping_amount = forms.FloatField(required=False, min_value=0, widget=forms.NumberInput(attrs={'id': 'id_shipping_amount', 'step': 'any', 'class':'form-control'}))


    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT)


class CreateGalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'description']

class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['gallery', 'title', 'description', 'link_title', 'link_url']

class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['image', 'item_name', 'price', 'description', 'product_enabled']


class CreateImageForm(forms.ModelForm):

    # def __init__(self, *args, **kwargs):
    #     super(CreateImageForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Image
        fields = ['gallery', 'category', 'title', 'description', 'image', 'anchor', 'link_title', 'link_url']
