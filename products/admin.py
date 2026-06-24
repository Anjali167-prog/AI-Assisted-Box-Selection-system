from django.contrib import admin

from products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "length", "width", "height", "weight"]
    search_fields = ["name"]
