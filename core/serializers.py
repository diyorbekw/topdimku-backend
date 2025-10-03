from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, ProductComment, ProductCommentImage,
    Cart, CartItem, Order, OrderItem, User
)

# ------------------ CATEGORY & PRODUCT ------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductCommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCommentImage
        fields = "__all__"


class ProductCommentSerializer(serializers.ModelSerializer):
    images = ProductCommentImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductComment
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    comments = ProductCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

# ------------------ AUTH ------------------
class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    verification_code = serializers.CharField(max_length=6)

# ------------------ CART ------------------
class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    product_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "cart", "product", "product_title", "product_slug", "product_price", "quantity", "added_at")

    def get_product_price(self, obj):
        return obj.product.discount_price if obj.product.discount_price is not None else obj.product.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "user", "session_key", "is_active", "items", "total_items", "subtotal", "created_at", "updated_at")


class AddCartItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)  # 0 -> delete

# ------------------ ORDER ------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_title", "quantity", "unit_price", "total_price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "user", "phone_number", "total", "status", "shipping_address", "note", "created_at", "items")
        read_only_fields = ("total", "status", "created_at", "items")
