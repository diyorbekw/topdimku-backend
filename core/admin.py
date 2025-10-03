from django.contrib import admin
from .models import (
    Category, Product, ProductImage, ProductComment, ProductCommentImage,
    Cart, CartItem, Order, OrderItem
)

# ------------------ PRODUCT ------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductCommentImageInline(admin.TabularInline):
    model = ProductCommentImage
    extra = 1


class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "comment_text")
    inlines = [ProductCommentImageInline]
    search_fields = ("user", "comment_text")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "discount_price", "slug", "count")
    search_fields = ("title", "description")
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title",)


admin.site.register(ProductComment, ProductCommentAdmin)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    autocomplete_fields = ["product"]  # Productni tanlash uchun
    readonly_fields = ["added_at"]     # faqat ko‘rsatish uchun
    fields = ("product", "quantity", "added_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at", "updated_at")
    search_fields = ("user__phone_number",)
    inlines = [CartItemInline]
    exclude = ("session_key",)  # guest user session key ko‘rinmas bo‘ladi

# ------------------ ORDER ------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ["product"]  # <-- Productni tanlash uchun
    readonly_fields = ("unit_price", "total_price")
    fields = ("product", "quantity", "unit_price", "total_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__phone_number", "id")
    inlines = [OrderItemInline]
