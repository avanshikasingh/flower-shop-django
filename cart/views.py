from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from shop.models import Product
from .cart import Cart
from django.http import JsonResponse

# Create your views here.

#detail view
def cart_detail(request):
    #get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, "cart/cart_detail.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals})

def cart_add(request):
    #get the cart
    cart = Cart(request)

    #test the post
    if request.POST.get('action') == 'post':
        # get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        #lookup product in DB
        product = get_object_or_404(Product, id=product_id)

        #save to session
        cart.add(product=product, quantity=product_qty)

        #get cart quantity
        cart_quantity = cart.__len__()

        #return response
        response = JsonResponse({'qty:':cart_quantity})
        return response
    

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product = get_object_or_404(Product, id=product_id)
        cart.delete(product)

        # return updated cart count
        response = JsonResponse({'qty': len(cart)})
        return response

def cart_update(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product_qty = request.POST.get("product_qty")

        # Validate product ID
        if not product_id:
            messages.error(request, "Missing product ID.")
            return redirect("cart_detail")

        product = get_object_or_404(Product, id=product_id)

        # Validate quantity
        try:
            quantity = int(product_qty)
            if quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity provided.")
            return redirect("cart_detail")

        # Update the cart
        cart = Cart(request)
        cart.update(product=product, quantity=quantity)
        messages.success(request, f"{product.name} quantity updated.")

    return redirect("cart_detail")
