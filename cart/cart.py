import json
from shop.models import Product, Profile

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.request = request

        # get the current session cart if it exists
        cart = self.session.get('session_key')

        # if the user is new, no cart yet
        if 'session_key' not in self.session:
            cart = self.session['session_key'] = {}

        # make sure cart is available on all pages
        self.cart = cart

    def db_add(self, key, quantity):
        """Save the current cart to the Profile model for logged-in users."""
        self.cart[key] = quantity
        if self.request.user.is_authenticated:
            Profile.objects.filter(user_id=self.request.user.id).update(
                old_cart=json.dumps(self.cart)
            )

    # ---------- Product APIs ----------
    def add(self, product, quantity, replace=False):
        """
        Add a product to the cart or update its quantity.
        If replace=True, set the exact quantity.
        Otherwise, add to the existing quantity.
        """
        product_id = str(product.id if hasattr(product, 'id') else product)
        product_qty = int(quantity)

        if replace:
            self.cart[product_id] = product_qty
        else:
            self.cart[product_id] = self.cart.get(product_id, 0) + product_qty

        self.session.modified = True
        self.db_add(key=product_id, quantity=product_qty)

    def update(self, product, quantity):
        """Update the quantity of a product in the cart."""
        self.add(product, quantity, replace=True)
        return self.cart

    def delete(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    # ---------- Totals ----------
    def cart_total(self):
        total = 0
        quantities = self.cart

        for key, value in quantities.items():
            if str(key).startswith("cb:"):  # Custom bouquet
                total += float(value)
            else:  # Normal product
                try:
                    product = Product.objects.get(id=int(key))
                    total += product.price * value
                except Product.DoesNotExist:
                    pass
        return total

    def __len__(self):
        """Return total quantity of all items in the cart."""
        return sum(1 if str(k).startswith("cb:") else v for k, v in self.cart.items())

    def get_prods(self):
        """Return Product queryset for products in cart."""
        product_ids = [int(k) for k in self.cart.keys() if not str(k).startswith("cb:")]
        return Product.objects.filter(id__in=product_ids)


    def get_quants(self):
        """Return the quantities dict."""
        return self.cart
