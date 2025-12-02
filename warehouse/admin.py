from django.contrib import admin
from .models import Warehouse, Stock
from django.utils.html import format_html

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'manager')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity')
    list_filter = ('warehouse',)
    search_fields = ('product__name',)

    def status(self, obj):
        if obj.is_low_stock():
            return format_html('<span style="color:red; font-weight:bold;">Low Stock!</span>')
        return "OK"

