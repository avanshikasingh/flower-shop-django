from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import Order   # adjust path if needed
from .models import Delivery, DeliveryPartner
import uuid


@receiver(post_save, sender=Order)
def create_delivery(sender, instance, created, **kwargs):
    # Only create delivery if order is paid and not already linked
    if instance.paid:
        Delivery.objects.get_or_create(
            order=instance,
            defaults={
                "partner": DeliveryPartner.objects.first(),  # assign first partner
                "tracking_no": str(uuid.uuid4())[:8],
            },
        )
