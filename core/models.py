from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid
from django.conf import settings

class Category(models.Model):
    title = models.CharField(max_length=150, unique=True, verbose_name="Title")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="Image")
    slug = models.SlugField(unique=True, blank=True, editable=False)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to="products/main/", blank=True, null=True, verbose_name="Main Image")
    count = models.PositiveIntegerField(default=0, verbose_name="Stock Count")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Discount Price")
    slug = models.SlugField(unique=True, blank=True, editable=False)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/", verbose_name="Image")

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"Image for {self.product.title}"


class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    user = models.CharField(max_length=100, verbose_name="User")
    rating = models.PositiveSmallIntegerField(
        default=1,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Rating"
    )
    comment_text = models.TextField(verbose_name="Comment Text")

    class Meta:
        verbose_name = "Product Comment"
        verbose_name_plural = "Product Comments"
        ordering = ["-id"]

    def __str__(self):
        return f"Comment by {self.user} on {self.product.title}"


class ProductCommentImage(models.Model):
    comment = models.ForeignKey(ProductComment, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/comments/", verbose_name="Comment Image")

    class Meta:
        verbose_name = "Product Comment Image"
        verbose_name_plural = "Product Comment Images"

    def __str__(self):
        return f"Image for {self.comment.user}'s comment"

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password or self.make_random_password())
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number


class Verification(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    chat_id = models.BigIntegerField(blank=True, null=True)

    def is_valid(self):
        return (not self.is_used) and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.phone_number} - {self.code}"
    
class Cart(models.Model):
    """
    Har bir Cart user bilan bog'lanishi mumkin yoki guest session_key bilan.
    Active cart bo'lishi tavsiya etiladi (bitta user uchun bir nechta bo'lishi mumkin).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="carts")
    session_key = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        if self.user:
            return f"Cart of {self.user}"
        return f"Guest cart ({self.session_key})"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def subtotal(self):
        total = 0
        for item in self.items.select_related('product').all():
            price = item.product.discount_price if item.product.discount_price is not None else item.product.price
            total += price * item.quantity
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders")
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # fallback contact
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # narxni saqlaydi
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)  # unit_price * quantity


    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.discount_price if self.product.discount_price else self.product.price
        
        self.total_price = self.unit_price * self.quantity
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} (Order {self.order.id})"

class SliderImage(models.Model):
    image = models.ImageField(upload_to="sliders/", verbose_name="Slider Image")
    
    def __str__(self):
        return f"Slider Image {self.id}"
    
    class Meta:
        verbose_name = "Slider Image"
        verbose_name_plural = "Slider Images"
