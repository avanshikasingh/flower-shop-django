from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import OrderItem
from .models import Stock

@receiver(post_save, sender=OrderItem)
def reduce_stock(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        qty = instance.quantity

        # Try to find stock entry
        stock_entry = Stock.objects.filter(product=product).first()

        if not stock_entry:
            # If stock doesn’t exist yet, create it with quantity 0
            stock_entry = Stock.objects.create(
                product=product,
                warehouse_id=1,   # 👈 you can assign default warehouse
                quantity=0
            )

        # Reduce stock safely
        if stock_entry.quantity < qty:
            raise ValueError("Not enough stock available for this product!")

        stock_entry.quantity -= qty
        stock_entry.save()

        # Check if stock is low and send alert
        stock_entry.send_low_stock_alert()



