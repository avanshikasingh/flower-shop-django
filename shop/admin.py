from django.contrib import admin
from .models import Category, Customer, Product, Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Profile)

# Custom Product admin to show vendor field
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    list_filter = ('category',)  # filter by vendor or category
    search_fields = ('name', 'description')

admin.site.register(Product, ProductAdmin)


# Mix profile info and user info
class ProfileInline(admin.StackedInline):
    model = Profile

# Extend the user model
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username", "first_name", "last_name", "email", "password", "last_login", "date_joined"]
    inlines = [ProfileInline]

# Unregister the old way
admin.site.unregister(User)

# Re-register the new way
admin.site.register(User, UserAdmin)
