from django.shortcuts import get_object_or_404
from .models import Order, Payment, Setting
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        order = get_object_or_404(Order, id=ipn.invoice)
        user = order.user
        taxes_enabled = Setting.objects.filter(name='Taxes').first()

        # checks if total order cost matches payment amount on ipn
        #
        if order.get_total_price() == ipn.mc_gross:

            # create payment

            payment = Payment()
            # payment.payment_id = ipn.invoice
            payment.payment_id = ipn.txn_id
            payment.user = order.user
            payment.amount = order.get_total_price()
            payment.payment_type = 'P'
            payment.save()



            # mark the order as paid
            for item in order.items.all():
                item.ordered = True
                item.save()
            order.ordered = True
            order.payment = payment

            order.save()

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
