from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.

#Shipping model
#----------------------------------------------------------------------------------------
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    #Don't pluralize addess
    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'
    
#create order model
#--------------------------------------------------------------------------------
class Order(models.Model):
    #foreign key
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    #paypal invoice and paid T/F
    invoice = models.CharField(max_length=250, null=True, blank=True)
    paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'order - {str(self.id)}'
    

#Auto add shipping date 
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.shipped and not instance.date_shipped:
        instance.date_shipped = timezone.now()
            
                                        
#create order items model
#---------------------------------------------------------------------------------
class OrderItem(models.Model):
    #foreign key
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (${self.price})"






