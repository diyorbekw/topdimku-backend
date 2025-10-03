from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from .views import (
    CategoryViewSet, ProductViewSet, ProductImageViewSet,
    ProductCommentViewSet, ProductCommentImageViewSet,
    CartViewSet, CartItemViewSet,
    OrderViewSet, OrderItemViewSet,
    RegisterAPIView, LoginAPIView
)

# 🔗 Router
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'product-comments', ProductCommentViewSet)
router.register(r'product-comment-images', ProductCommentImageViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

# 📑 Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Shop API",
        default_version="v1",
        description="CRUD API for Categories, Products, Images, Comments, Cart and Orders",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
]
