"""Django admin configuration for the packing app."""

from django.contrib import admin

from .models import Box, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "length", "width", "height", "weight")
    search_fields = ("sku", "name")
    list_filter = ("name",)


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "inner_length",
        "inner_width",
        "inner_height",
        "max_weight",
        "cost",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "created_at")
    search_fields = ("reference",)
    inlines = [OrderItemInline]
