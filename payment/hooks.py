from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    #add a tne second pause for paypal to send IPN data
    time.sleep(10)
    #grab the info that paypal sends
    paypal_obj = sender
    #get the invoice
    my_invoice = str(paypal_obj.invoice)

    #match the paypal invoice to the order invoice
    my_Order = Order.objects.get(invoice=my_invoice)

    #recorde the order was paid
    my_Order.paid = True
    #save the order
    my_Order.save()

    #print(paypal_obj)
    #print(f'Amount Paid: {paypal_obj.mc_gross}')
