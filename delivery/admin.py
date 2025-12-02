from django.contrib import admin
from .models import DeliveryPartner, Delivery

@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "phone", "is_active")
    search_fields = ("name", "contact_email", "company_name")
    list_filter = ("is_active",)

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("order", "partner", "tracking_no", "status", "created_at")
    list_filter = ("status", "partner")
    search_fields = ("order__id", "tracking_no")
