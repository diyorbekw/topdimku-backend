from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Category, Product, ProductImage, ProductComment, ProductCommentImage,
    Cart, CartItem, Order, OrderItem, Verification, User
)
from .serializers import (
    CategorySerializer, ProductSerializer, ProductImageSerializer,
    ProductCommentSerializer, ProductCommentImageSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer,
    RegisterSerializer, LoginSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from datetime import timedelta
import random

# ------------------ CRUD ------------------
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductCommentViewSet(ModelViewSet):
    queryset = ProductComment.objects.all()
    serializer_class = ProductCommentSerializer


class ProductCommentImageViewSet(ModelViewSet):
    queryset = ProductCommentImage.objects.all()
    serializer_class = ProductCommentImageSerializer

# ------------------ CART ------------------
class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

# ------------------ ORDER ------------------
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

# ------------------ AUTH ------------------
def generate_code():
    return f"{random.randint(0, 999999):06d}"


class RegisterAPIView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: openapi.Response("Deep link created", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"deep_link": openapi.Schema(type=openapi.TYPE_STRING, description="Telegram deep link")}
        ))}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]

        code = generate_code()
        verification = Verification.objects.create(
            phone_number=phone,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        bot_username = "scommerce_bot"
        deep_link = f"https://t.me/{bot_username}?start={verification.token}"

        return Response({"deep_link": deep_link}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["verification_code"]

        verification = Verification.objects.filter(
            phone_number=phone, code=code, is_used=False
        ).order_by("-created_at").first()

        if not verification or not verification.is_valid():
            return Response({"detail": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)

        verification.is_used = True
        verification.save()

        user, _ = User.objects.get_or_create(phone_number=phone)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "refresh": str(refresh),
            "access": str(access),
            "user_id": user.id,
        }, status=status.HTTP_200_OK)
