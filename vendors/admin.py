from django.contrib import admin
from .models import Vendor, VendorProduct


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "company_name", "is_active")
    search_fields = ("name", "email", "company_name")
    list_filter = ("is_active",)


@admin.register(VendorProduct)
class VendorProductAdmin(admin.ModelAdmin):
    list_display = ("vendor", "product", "cost_price", "supply_lead_time", "is_preferred")
    list_filter = ("vendor", "is_preferred")
    search_fields = ("vendor__name", "product__name")
