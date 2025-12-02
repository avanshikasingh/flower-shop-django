from django.db import models
from django.core.mail import send_mail
from django.conf import settings

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=0)  # max storage capacity
    manager = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.location}"


class Stock(models.Model):
    product = models.ForeignKey("shop.Product", on_delete=models.CASCADE)
    warehouse = models.ForeignKey("warehouse.Warehouse", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'warehouse')  # each product unique per warehouse

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in {self.warehouse.name}"
    
    # ✅ Low-stock alert method
    def is_low_stock(self, threshold=5):
        return self.quantity < threshold

    def send_low_stock_alert(self):
        """Send email alert if stock is below threshold"""
        if self.is_low_stock():
            subject = f"Low Stock Alert: {self.product.name}"
            message = (
                f"The product '{self.product.name}' in warehouse '{self.warehouse.name}' "
                f"is running low. Only {self.quantity} left in stock!"
            )
            admin_email = settings.DEFAULT_FROM_EMAIL
            notify_email = getattr(settings, "WAREHOUSE_ALERT_EMAIL", admin_email)

            send_mail(
                subject,
                message,
                admin_email,
                [notify_email],
                fail_silently=True,
            )
