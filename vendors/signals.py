from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VendorProduct, SupplyLog
from warehouse.models import Stock, Warehouse


@receiver(post_save, sender=VendorProduct)
def ensure_stock_for_vendor_product(sender, instance, created, **kwargs):
    if created:
        # Try to use the first warehouse, or create one if none exists
        default_wh = Warehouse.objects.first()
        if not default_wh:
            default_wh = Warehouse.objects.create(
                name="Main Warehouse",
                location="Default Location",
                capacity=1000
            )

        Stock.objects.get_or_create(
            product=instance.product,
            warehouse=default_wh,
            defaults={"quantity": 0}
        )


@receiver(post_save, sender=SupplyLog)
def update_stock_on_supply(sender, instance, created, **kwargs):
    if created:
        stock_entry, _ = Stock.objects.get_or_create(
            product=instance.product,
            warehouse=instance.warehouse,
            defaults={"quantity": 0}
        )

        # Add the supplied quantity
        stock_entry.quantity += instance.quantity_supplied
        stock_entry.save()

        # (Optional) Low-stock alert check after update
        if stock_entry.is_low_stock():
            stock_entry.send_low_stock_alert()
