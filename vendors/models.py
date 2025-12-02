from django.db import models
from warehouse.models import Warehouse

class Vendor(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class VendorProduct(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey("shop.Product",  on_delete=models.CASCADE,related_name="vendors")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    supply_lead_time = models.PositiveIntegerField(default=7)  # days to deliver
    is_preferred = models.BooleanField(default=False)  # 👈 Add this

    def __str__(self):
        return f"{self.vendor.name} supplies {self.product.name}"

#  Log vendor deliveries
class SupplyLog(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="supplies")
    product = models.ForeignKey("shop.Product", on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity_supplied = models.PositiveIntegerField()
    supplied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} supplied {self.quantity_supplied} x {self.product.name}"