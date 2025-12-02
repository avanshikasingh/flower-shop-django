from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from shop.models import Product, Profile
import datetime
#paypal stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
#unique user id for duplicate orders
import uuid 


#Checkout page view
#---------------------------------------------------------------------------------------
def checkout(request):
    # get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    # Pass the form to the template by default
    shipping_form = ShippingForm(request.POST or None)

    if request.user.is_authenticated:
        # Check if a shipping address exists for the user
        try:
            shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
            # Use the existing address as the initial data for the form
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except ShippingAddress.DoesNotExist:
            # If no address exists, the form will be empty
            pass

    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form  # Pass the form to the template
    })

#Billing Information view
#----------------------------------------------------------------------------------------
def billing_info(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.method == 'POST':
        # Create a session with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        # PayPal setup
        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': 'Book Order',
            'no_shipping': '2',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'USD',
            'notify_url': 'http://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'http://{}{}'.format(host, reverse("payment_success")),
            'cancel_url': 'http://{}{}'.format(host, reverse("payment_failed")),
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        # Get billing form
        billing_form = PaymentForm()

        # Create order
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(
                user=user, full_name=full_name, email=email,
                shipping_address=shipping_address, amount_paid=amount_paid
            )
            create_order.save()

            # Add order items
            for product in cart_products:
                price = product.sale_price if product.is_sale else product.price
                for key, value in quantities.items():
                    if int(key) == product.id:
                        OrderItem.objects.create(
                            order=create_order, product=product,
                            user=user, quantity=value, price=price
                        )

            # Clear cart
            Profile.objects.filter(user__id=request.user.id).update(old_cart="")

        else:  # guest user
            create_order = Order(
                full_name=full_name, email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid, invoice=str(uuid.uuid4())
            )
            create_order.save()

            for product in cart_products:
                price = product.sale_price if product.is_sale else product.price
                for key, value in quantities.items():
                    if int(key) == product.id:
                        OrderItem.objects.create(
                            order=create_order, product=product,
                            quantity=value, price=price
                        )

        # ✅ Always return a response here
        return render(request, "payment/billing_info.html", {
            "paypal_form": paypal_form,
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_info": request.POST,
            "billing_form": billing_form
        })

    # GET request → show page
    return render(request, "payment/billing_info.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
    })

    
#process order
def process_order(request):
    if request.POST:
         #get the cart
         cart = Cart(request)
         cart_products = cart.get_prods()
         quantities = cart.get_quants()
         totals = cart.cart_total()

         #get billing inf from the last page
         payment_form = PaymentForm(request.POST or None)
         #get shipping Session bata
         my_shipping = request.session.get('my_shipping')
 
         #gather order info
         full_name = my_shipping['shipping_full_name']
         email = my_shipping['shipping_email']
         #Create shipping address from session.info
         shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
         amount_paid = totals

         #create an order
         if request.user.is_authenticated:
             #logged in
             user = request.user
             #create order
             create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
             create_order.save()

             #add order items
             #get the order ID
             order_id = create_order.pk

             #get product info
             for product in cart_products:
                 #get product ID
                 product_id = product.id
                 #get product price
                 if product.is_sale:
                     price = product.sale_price
                 else:
                     price = product.price

                 #get quantity
                 for key, value in quantities.items():
                     if int(key) == product.id:
                         #Create order item
                         create_order_item = OrderItem(order=create_order, product=product, user=user, quantity=value, price=price)
                         create_order_item.save()

             #Delete the cart
             for key in list(request.session.keys()):
                 if key == "session_key":
                     #delete the key 
                     del request.session[key]

             #Delete cart from database 
             current_user = Profile.objects.filter(user__id=request.user.id)
             #delete shopping cart in database 
             current_user.update(old_cart="")
                             
             messages.success(request, "Order Placed!")
             return redirect('home')
         else:
             #not logged in
             create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
             create_order.save()
             #add order items
             #get the order ID
             order_id = create_order.pk

             #get product info
             for product in cart_products:
                 #get product ID
                 product_id = product.id
                 #get product price
                 if product.is_sale:
                     price = product.sale_price
                 else:
                     price = product.price

                 #get quantity
                 for key, value in quantities.items():
                     if int(key) == product.id:
                         #Create order item
                         create_order_item = OrderItem(order=create_order, product=product, quantity=value, price=price)
                         create_order_item.save()

              #Delete the cart
             for key in list(request.session.keys()):
                 if key == "session_key":
                     #delete the key 
                     del request.session[key]

             messages.success(request, "Order Placed!")
             return redirect('home')
    else:
        messages.success(request, "Access Denied")
        return redirect('home')
    
#Shipped dashboard
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            orders.update(shipped=False)

            messages.success(request, "Shipping status Updated")
            return redirect('home')
        return render(request, "payment/shipped_dash.html", {"orders": orders})
    else:
        messages.error(request, "Not authorized")
        return redirect('home')

#Not shipped dashboard
def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            #get the order
            order = Order.objects.filter(id=num)
            #get date and time
            now = datetime.datetime.now()
            #update order
            orders.update(shipped=False, date_shipped=now)

            messages.success(request, "Shipping status Updated")
            return redirect('home')
        
        return render(request, "payment/not_shipped_dash.html", {"orders": orders})
    else:
        messages.error(request, "Not authorized")
        return redirect('home')

#Orders
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #get the order
        order = Order.objects.get(id=pk)
        #get the order items
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            #check if true or false
            if status == "true":
                #get the ordeer
                order = Order.objects.filter(id=pk)
                #update the status
                order.update(shipped=True)
            else:
                #get the ordeer
                order = Order.objects.filter(id=pk)
                #update the status
                now = datetime.datetime.now()
                order.update(shipped=False, date_shipped=now)
            messages.success(request, "Shipping status Updated")
            return redirect('home')


        return render(request, 'payment/orders.html', {"order":order, "items":items})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def payment_success(request):
    # delete the browser cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    # ✅ Mark the latest order as paid
    if request.user.is_authenticated:
        try:
            # get the latest order of this user
            order = Order.objects.filter(user=request.user).latest('id')
            order.paid = True   # make sure your Order model has a 'paid' BooleanField
            order.save()
        except Order.DoesNotExist:
            pass
    else:
        # for guest checkout, if you store order_id in session
        order_id = request.session.get("guest_order_id")
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.save()
            except Order.DoesNotExist:
                pass

    # Delete the cart session
    for key in list(request.session.keys()):
        if key == "session_key":
            del request.session[key]

    return render(request, "payment/payment_success.html", {})


def payment_failed(request):
    return render(request, "payment/payment_failed.html", {})

