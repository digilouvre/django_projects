import django_filters
from dl.models import Order, Item


class OrderFilter(django_filters.FilterSet):
    # payment__payment_type = django_filters.ModelChoiceFilter(queryset=Payment.objects.distinct('payment_type'), label='Payment Type')
    items__item = django_filters.ModelChoiceFilter(queryset=Item.objects.all(), label='Product')
    ordered_date = django_filters.DateTimeFromToRangeFilter(label='Date Ordered',
        lookup_expr=('icontains'),
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'datetime-local', 'class':'form-control'}
        )
    )
    class Meta:
        model = Order
        fields = ['user', 'ordered_date', 'payment__payment_type', 'items__item' ]