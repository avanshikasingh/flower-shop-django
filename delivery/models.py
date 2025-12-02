from django.db import models
from payment.models import Order   # adjust import if your order model is in another app
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class DeliveryPartner(models.Model):
    name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    tracking_url = models.URLField(blank=True, null=True)  # e.g. DHL tracking site
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Delivery(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_no = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id} ({self.status})"

    def tracking_link(self):
        if self.partner and self.partner.tracking_url and self.tracking_no:
            return f"{self.partner.tracking_url}{self.tracking_no}"
        return None

@receiver(post_save, sender=Order)
def create_delivery_after_payment(sender, instance, created, **kwargs):
    # Only create delivery when payment is successful
    if instance.paid and not hasattr(instance, 'delivery'):
        Delivery.objects.create(order=instance, partner=None, status="pending")