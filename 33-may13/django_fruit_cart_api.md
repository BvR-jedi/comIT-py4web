# Django REST Framework — Fruit Shopping Cart API

A step-by-step guide to building a shopping cart API for fruits with role-based access control.

---

## 1. Project Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt

# Start project and app
django-admin startproject fruit_cart .
python manage.py startapp store
```

---

## 2. Settings (`fruit_cart/settings.py`)

```python
INSTALLED_APPS = [
    # ...default apps...
    "rest_framework",
    "store",
]

# DRF: use JWT by default and enforce authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

---

## 3. Models (`store/models.py`)

```python
from django.db import models
from django.contrib.auth.models import User


class Fruit(models.Model):
    name         = models.CharField(max_length=100, unique=True)
    weight_kg    = models.DecimalField(max_digits=8, decimal_places=3)   # kg
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)  # currency/kg

    def __str__(self):
        return self.name


class Cart(models.Model):
    # Each customer owns one or more carts
    owner      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart #{self.pk} — {self.owner.username}"


class CartItem(models.Model):
    cart       = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    fruit      = models.ForeignKey(Fruit, on_delete=models.PROTECT)
    quantity_kg = models.DecimalField(max_digits=8, decimal_places=3)   # how many kg ordered

    @property
    def subtotal(self):
        """Price for this line item: quantity × price per kg."""
        return self.quantity_kg * self.fruit.price_per_kg

    def __str__(self):
        return f"{self.quantity_kg} kg of {self.fruit.name}"
```

---

## 4. Serializers (`store/serializers.py`)

```python
from rest_framework import serializers
from .models import Fruit, Cart, CartItem


class FruitSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Fruit
        fields = ["id", "name", "weight_kg", "price_per_kg"]


class CartItemSerializer(serializers.ModelSerializer):
    fruit_name = serializers.ReadOnlyField(source="fruit.name")
    subtotal   = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model  = CartItem
        fields = ["id", "fruit", "fruit_name", "quantity_kg", "subtotal"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model  = Cart
        fields = ["id", "owner", "created_at", "items", "total"]
        read_only_fields = ["owner", "created_at"]

    def get_total(self, obj):
        """Sum of all item subtotals in the cart."""
        return sum(item.subtotal for item in obj.items.all())
```

---

## 5. Permissions (`store/permissions.py`)

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Full access for users in the 'admins' group."""
    def has_permission(self, request, view):
        return request.user.groups.filter(name="admins").exists()


class IsCustomer(BasePermission):
    """Customers can only touch carts/items — not fruits."""
    def has_permission(self, request, view):
        return request.user.groups.filter(name="customers").exists()


class IsAdminOrCustomerReadCart(BasePermission):
    """
    Admins: unrestricted.
    Customers: full CRUD on carts, read-only on fruits.
    """
    def has_permission(self, request, view):
        user = request.user
        if user.groups.filter(name="admins").exists():
            return True
        if user.groups.filter(name="customers").exists():
            # Customers are blocked at the view level for fruit writes;
            # this permission just gates the cart/item views.
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Customers may only access their own carts."""
        from .models import Cart, CartItem
        if request.user.groups.filter(name="admins").exists():
            return True
        if isinstance(obj, Cart):
            return obj.owner == request.user
        if isinstance(obj, CartItem):
            return obj.cart.owner == request.user
        return False
```

---

## 6. Views (`store/views.py`)

```python
from rest_framework import viewsets, permissions
from .models import Fruit, Cart, CartItem
from .serializers import FruitSerializer, CartSerializer, CartItemSerializer
from .permissions import IsAdmin, IsAdminOrCustomerReadCart

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


class FruitViewSet(viewsets.ModelViewSet):
    """
    Admins: full CRUD.
    Customers: read-only (list + retrieve).
    """
    queryset         = Fruit.objects.all()
    serializer_class = FruitSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            # Both groups can browse fruits
            return [permissions.IsAuthenticated()]
        # Only admins can create, update, or delete fruits
        return [IsAdmin()]


class CartViewSet(viewsets.ModelViewSet):
    """
    Admins see all carts; customers see only their own.
    """
    serializer_class = CartSerializer
    permission_classes = [IsAdminOrCustomerReadCart]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="admins").exists():
            return Cart.objects.all()
        # Customers access only their own carts
        return Cart.objects.filter(owner=user)

    def perform_create(self, serializer):
        # Cart is always created for the requesting user
        serializer.save(owner=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    Nested under carts; enforces cart ownership for customers.
    """
    serializer_class   = CartItemSerializer
    permission_classes = [IsAdminOrCustomerReadCart]

    def get_queryset(self):
        user    = self.request.user
        cart_pk = self.kwargs.get("cart_pk")
        qs      = CartItem.objects.filter(cart_id=cart_pk)
        if user.groups.filter(name="admins").exists():
            return qs
        # Customers only see items from their own cart
        return qs.filter(cart__owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        cart_pk = self.kwargs.get("cart_pk")
        
        # Safely fetch the cart or return a clean 404 Not Found
        cart = get_object_or_404(Cart, pk=cart_pk)
        
        # Prevent customers from adding items to other people's carts
        is_admin = user.groups.filter(name="admins").exists()
        if not is_admin and cart.owner != user:
            raise PermissionDenied("You do not have permission to add items to this cart.")
            
        # If checks pass, save the item to the cart
        serializer.save(cart=cart)
```

---

## 7. URLs (`store/urls.py` & `fruit_cart/urls.py`)

```python
# store/urls.py
from rest_framework_nested import routers   # pip install drf-nested-routers
from django.urls import path, include
from .views import FruitViewSet, CartViewSet, CartItemViewSet

router = routers.DefaultRouter()
router.register(r"fruits", FruitViewSet, basename="fruit")
router.register(r"carts",  CartViewSet,  basename="cart")

# Nested router: /carts/{cart_pk}/items/
carts_router = routers.NestedDefaultRouter(router, r"carts", lookup="cart")
carts_router.register(r"items", CartItemViewSet, basename="cart-items")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(carts_router.urls)),
]
```

```python
# fruit_cart/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/",          admin.site.urls),
    path("api/token/",      TokenObtainPairView.as_view(),  name="token_obtain"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/",            include("store.urls")),
]
```

> Install the nested router helper:
> ```bash
> pip install drf-nested-routers
> ```

---

## 8. Migrations & Groups Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Create the two user groups via the Django shell:

```python
# python manage.py shell
from django.contrib.auth.models import Group
Group.objects.get_or_create(name="admins")
Group.objects.get_or_create(name="customers")
```

Assign users to groups through the Django admin at `/admin/` or programmatically:

```python
from django.contrib.auth.models import User, Group

user = User.objects.get(username="alice")
user.groups.add(Group.objects.get(name="customers"))
```

---

## 9. API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Obtain JWT (`username`, `password`) |
| POST | `/api/token/refresh/` | Refresh JWT |

### Fruits *(Admin: full CRUD — Customer: read only)*
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/fruits/` | List all fruits |
| POST | `/api/fruits/` | Create a fruit |
| GET | `/api/fruits/{id}/` | Retrieve a fruit |
| PUT/PATCH | `/api/fruits/{id}/` | Update a fruit |
| DELETE | `/api/fruits/{id}/` | Delete a fruit |

### Carts *(Admin: all carts — Customer: own carts only)*
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/carts/` | List carts |
| POST | `/api/carts/` | Create a cart |
| GET | `/api/carts/{id}/` | Retrieve a cart (includes items + total) |
| PUT/PATCH | `/api/carts/{id}/` | Update a cart |
| DELETE | `/api/carts/{id}/` | Delete a cart |

### Cart Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/carts/{cart_pk}/items/` | List items in a cart |
| POST | `/api/carts/{cart_pk}/items/` | Add an item |
| GET | `/api/carts/{cart_pk}/items/{id}/` | Retrieve an item (shows subtotal) |
| PUT/PATCH | `/api/carts/{cart_pk}/items/{id}/` | Update quantity |
| DELETE | `/api/carts/{cart_pk}/items/{id}/` | Remove an item |

---

## 10. Example Payloads

**Create a fruit** (`POST /api/fruits/`)
```json
{ "name": "Mango", "weight_kg": "1.500", "price_per_kg": "3.50" }
```

**Add an item to cart** (`POST /api/carts/1/items/`)
```json
{ "fruit": 1, "quantity_kg": "2.000" }
```

**Cart retrieve response** (`GET /api/carts/1/`)
```json
{
  "id": 1,
  "owner": 3,
  "created_at": "2026-05-13T10:00:00Z",
  "items": [
    {
      "id": 1,
      "fruit": 1,
      "fruit_name": "Mango",
      "quantity_kg": "2.000",
      "subtotal": "7.00"
    }
  ],
  "total": "7.00"
}
```

---

## 11. Project Structure

```
fruit_cart/
├── fruit_cart/
│   ├── settings.py
│   └── urls.py
├── store/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   └── urls.py
└── manage.py
```
