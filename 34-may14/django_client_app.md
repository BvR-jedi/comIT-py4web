# Django Client App — Fruit Shopping Cart
### TailwindCSS · DaisyUI · HTMX

A step-by-step guide to building a Django front-end that consumes the Fruit Shopping Cart REST API. All mutations are handled in-place by HTMX — no full page reloads. Role-based templates separate the Admin and Customer experience.

---

## 1. Project Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install django requests

django-admin startproject client_app .
python manage.py startapp store
```

---

## 2. Settings (`client_app/settings.py`)

```python
INSTALLED_APPS = [
    # ...default apps...
    "store",
]

# Where to redirect after login / logout
LOGIN_URL          = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"

# Base URL of the REST API (no trailing slash)
API_BASE_URL = "http://127.0.0.1:8000/api"
```

---

## 3. Project Structure

```
client_app/
├── client_app/
│   ├── settings.py
│   └── urls.py
├── store/
│   ├── api.py              # API helper layer
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── store/
│           ├── base.html
│           ├── login.html
│           │
│           ├── admin/
│           │   ├── dashboard.html
│           │   ├── fruits/
│           │   │   ├── list.html
│           │   │   ├── _row.html       # HTMX partial
│           │   │   └── _form.html      # HTMX partial
│           │   └── carts/
│           │       ├── list.html
│           │       ├── _cart_card.html # HTMX partial
│           │       └── _item_row.html  # HTMX partial
│           │
│           └── customer/
│               ├── dashboard.html
│               ├── fruits/
│               │   └── list.html
│               └── carts/
│                   ├── list.html
│                   ├── _cart_card.html
│                   └── _item_row.html
└── manage.py
```

---

## 4. Tailwind CSS + DaisyUI via CDN

Add both to the `<head>` of `base.html`. No build step required.

```html
<!-- store/templates/store/base.html -->
<!DOCTYPE html>
<html data-theme="garden" lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>🍉 Fruit Cart{% block title %}{% endblock %}</title>

  <!-- Tailwind CSS + DaisyUI (CDN, no build step) -->
  <link href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- HTMX -->
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
</head>
<body class="bg-base-200 min-h-screen">

  <!-- Navbar -->
  <div class="navbar bg-base-100 shadow-sm px-6">
    <div class="flex-1">
      <a href="/dashboard/" class="text-xl font-bold">🍉 Fruit Cart</a>
    </div>
    <div class="flex-none gap-2">
      {% if request.session.username %}
        <div class="badge badge-outline">
          {{ request.session.username }}
          {% if request.session.role == "admin" %}
            <span class="badge badge-error ml-2">admin</span>
          {% else %}
            <span class="badge badge-info ml-2">customer</span>
          {% endif %}
        </div>
        <a href="/logout/" class="btn btn-ghost btn-sm">Logout</a>
      {% endif %}
    </div>
  </div>

  <!-- Flash messages (HTMX swaps these too) -->
  <div id="flash" class="container mx-auto px-4 mt-4">
    {% if messages %}
      {% for message in messages %}
        <div role="alert" class="alert alert-{{ message.tags }} mb-2">
          <span>{{ message }}</span>
        </div>
      {% endfor %}
    {% endif %}
  </div>

  <main class="container mx-auto px-4 py-6">
    {% block content %}{% endblock %}
  </main>

</body>
</html>
```

> **Theme choices** — change `data-theme` to any DaisyUI theme:
> `light` `dark` `cupcake` `bumblebee` `emerald` `corporate` `synthwave` `retro` `cyberpunk` `valentine` `halloween` `garden` `forest` `aqua` `lofi` `pastel` `fantasy` `wireframe` `black` `luxury` `dracula` `cmyk` `autumn` `business` `acid` `lemonade` `night` `coffee` `winter`.

---

## 5. API Helper Layer (`store/api.py`)

Centralise all `requests` calls here. Views stay thin.

```python
import requests
from django.conf import settings

API = settings.API_BASE_URL


def _h(token):
    """Build Authorization header."""
    return {"Authorization": f"Bearer {token}"}


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_token(username, password):
    """Return (access_token, is_admin) or raise on failure."""
    resp = requests.post(f"{API}/token/", json={"username": username, "password": password})
    resp.raise_for_status()
    token = resp.json()["access"]

    # Detect admin: Send an empty payload to the restricted endpoint.
    # Customers get 403 (Permission Denied). 
    # Admins bypass permissions but get 400 (Bad Request - missing fields).
    probe = requests.post(f"{API}/fruits/", json={}, headers=_h(token))
    
    is_admin = (probe.status_code == 400)

    return token, is_admin


# ── Fruits ────────────────────────────────────────────────────────────────────

def list_fruits(token):
    return requests.get(f"{API}/fruits/", headers=_h(token)).json()

def get_fruit(token, pk):
    return requests.get(f"{API}/fruits/{pk}/", headers=_h(token)).json()

def create_fruit(token, data):
    return requests.post(f"{API}/fruits/", json=data, headers=_h(token))

def update_fruit(token, pk, data):
    return requests.patch(f"{API}/fruits/{pk}/", json=data, headers=_h(token))

def delete_fruit(token, pk):
    return requests.delete(f"{API}/fruits/{pk}/", headers=_h(token))


# ── Carts ─────────────────────────────────────────────────────────────────────

def list_carts(token):
    return requests.get(f"{API}/carts/", headers=_h(token)).json()

def get_cart(token, pk):
    return requests.get(f"{API}/carts/{pk}/", headers=_h(token)).json()

def create_cart(token):
    return requests.post(f"{API}/carts/", json={}, headers=_h(token))

def delete_cart(token, pk):
    return requests.delete(f"{API}/carts/{pk}/", headers=_h(token))


# ── Cart Items ────────────────────────────────────────────────────────────────

def add_item(token, cart_pk, data):
    return requests.post(f"{API}/carts/{cart_pk}/items/", json=data, headers=_h(token))

def update_item(token, cart_pk, item_pk, data):
    return requests.patch(f"{API}/carts/{cart_pk}/items/{item_pk}/", json=data, headers=_h(token))

def delete_item(token, cart_pk, item_pk):
    return requests.delete(f"{API}/carts/{cart_pk}/items/{item_pk}/", headers=_h(token))
```

---

## 6. Session-Based Auth Middleware

Store the JWT and role in the Django session — no database needed.

```python
# store/middleware.py
from django.shortcuts import redirect

EXEMPT = ("/login",)   # paths that don't need a token

class JWTSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not any(request.path.startswith(e) for e in EXEMPT):
            if not request.session.get("token"):
                return redirect("/login/")
        return self.get_response(request)
```

Register in `settings.py`:

```python
MIDDLEWARE = [
    # ...existing middleware...
    "store.middleware.JWTSessionMiddleware",
]
```

---

## 7. Views (`store/views.py`)

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from . import api


# ── Auth ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            token, is_admin = api.get_token(username, password)
            request.session["token"]    = token
            request.session["username"] = username
            request.session["role"]     = "admin" if is_admin else "customer"
            return redirect("/dashboard/")
        except Exception:
            messages.error(request, "Invalid credentials.")
    return render(request, "store/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("/login/")


def dashboard(request):
    """Route to role-specific dashboard."""
    if request.session.get("role") == "admin":
        return redirect("/admin-dash/")
    return redirect("/customer-dash/")


# ── Admin – Fruits ─────────────────────────────────────────────────────────────

def admin_fruits(request):
    fruits = api.list_fruits(request.session["token"])
    return render(request, "store/admin/fruits/list.html", {"fruits": fruits})


def admin_fruit_create(request):
    """HTMX: return the updated table row after creation."""
    if request.method == "POST":
        resp = api.create_fruit(request.session["token"], {
            "name":         request.POST["name"],
            "weight_kg":    request.POST["weight_kg"],
            "price_per_kg": request.POST["price_per_kg"],
        })
        if resp.status_code == 201:
            fruit = resp.json()
            return render(request, "store/admin/fruits/_row.html", {"fruit": fruit})
        return render(request, "store/admin/fruits/_form.html",
                      {"error": resp.json(), "action": "create"})
    # GET: return empty form partial
    return render(request, "store/admin/fruits/_form.html", {"action": "create"})


def admin_fruit_edit(request, pk):
    """HTMX: inline edit row → save → return updated row."""
    token = request.session["token"]
    if request.method == "POST":
        resp = api.update_fruit(token, pk, {
            "name":         request.POST["name"],
            "weight_kg":    request.POST["weight_kg"],
            "price_per_kg": request.POST["price_per_kg"],
        })
        fruit = resp.json()
        return render(request, "store/admin/fruits/_row.html", {"fruit": fruit})
    # GET: return editable form row
    fruit = api.get_fruit(token, pk)
    return render(request, "store/admin/fruits/_form.html",
                  {"fruit": fruit, "action": "edit"})


def admin_fruit_delete(request, pk):
    """HTMX: delete and return empty string to remove the row."""
    if request.method == "DELETE":
        api.delete_fruit(request.session["token"], pk)
        return render(request, "store/admin/fruits/_row.html", {"deleted": True})


# ── Admin – Carts ──────────────────────────────────────────────────────────────

def admin_carts(request):
    token = request.session["token"]
    carts = api.list_carts(token)
    fruits = api.list_fruits(token)
    return render(request, "store/admin/carts/list.html",
                  {"carts": carts, "fruits": fruits})


def admin_cart_create(request):
    if request.method == "POST":
        token = request.session["token"]           # Extract token
        resp = api.create_cart(token)
        cart = resp.json()
        fruits = api.list_fruits(token)            # Fetch fruits list
        
        # Pass 'fruits' in the context dictionary
        return render(request, "store/admin/carts/_cart_card.html", {
            "cart": cart, 
            "fruits": fruits
        })


def admin_cart_delete(request, pk):
    if request.method == "DELETE":
        api.delete_cart(request.session["token"], pk)
        return render(request, "store/admin/carts/_cart_card.html", {"deleted": True})


# store/views.py

def admin_item_add(request, cart_pk):
    if request.method == "POST":
        token = request.session["token"]
        api.add_item(token, cart_pk, {
            "fruit":       request.POST["fruit"],
            "quantity_kg": request.POST["quantity_kg"],
        })
        cart = api.get_cart(token, cart_pk)
        fruits = api.list_fruits(token)  # <-- ADD THIS
        
        return render(request, "store/admin/carts/_cart_card.html", {
            "cart": cart, 
            "fruits": fruits             # <-- ADD THIS
        })


def admin_item_update(request, cart_pk, item_pk):
    if request.method == "POST":
        token = request.session["token"]
        api.update_item(token, cart_pk, item_pk, {"quantity_kg": request.POST["quantity_kg"]})
        cart = api.get_cart(token, cart_pk)
        fruits = api.list_fruits(token)  # <-- ADD THIS
        
        return render(request, "store/admin/carts/_cart_card.html", {
            "cart": cart, 
            "fruits": fruits             # <-- ADD THIS
        })


def admin_item_delete(request, cart_pk, item_pk):
    if request.method == "DELETE":
        token = request.session["token"]
        api.delete_item(token, cart_pk, item_pk)
        cart = api.get_cart(token, cart_pk)
        fruits = api.list_fruits(token)  # <-- ADD THIS
        
        return render(request, "store/admin/carts/_cart_card.html", {
            "cart": cart, 
            "fruits": fruits             # <-- ADD THIS
        })


# ── Customer – Fruits (read-only) ─────────────────────────────────────────────

def customer_dashboard(request):
    token = request.session["token"]
    fruits = api.list_fruits(token)
    carts  = api.list_carts(token)
    return render(request, "store/customer/dashboard.html",
                  {"fruits": fruits, "carts": carts})


# ── Customer – Carts ──────────────────────────────────────────────────────────

def customer_cart_create(request):
    if request.method == "POST":
        token = request.session["token"]
        resp  = api.create_cart(token)
        cart  = resp.json()
        fruits = api.list_fruits(token)
        return render(request, "store/customer/carts/_cart_card.html",
                      {"cart": cart, "fruits": fruits})


def customer_cart_delete(request, pk):
    if request.method == "DELETE":
        api.delete_cart(request.session["token"], pk)
        return render(request, "store/customer/carts/_cart_card.html", {"deleted": True})


def customer_item_add(request, cart_pk):
    if request.method == "POST":
        token = request.session["token"]
        api.add_item(token, cart_pk, {
            "fruit":       request.POST["fruit"],
            "quantity_kg": request.POST["quantity_kg"],
        })
        cart   = api.get_cart(token, cart_pk)
        fruits = api.list_fruits(token)
        return render(request, "store/customer/carts/_cart_card.html",
                      {"cart": cart, "fruits": fruits})


def customer_item_update(request, cart_pk, item_pk):
    if request.method == "POST":
        token = request.session["token"]
        api.update_item(token, cart_pk, item_pk, {"quantity_kg": request.POST["quantity_kg"]})
        cart   = api.get_cart(token, cart_pk)
        fruits = api.list_fruits(token)
        return render(request, "store/customer/carts/_cart_card.html",
                      {"cart": cart, "fruits": fruits})


def customer_item_delete(request, cart_pk, item_pk):
    if request.method == "DELETE":
        token = request.session["token"]
        api.delete_item(token, cart_pk, item_pk)
        cart   = api.get_cart(token, cart_pk)
        fruits = api.list_fruits(token)
        return render(request, "store/customer/carts/_cart_card.html",
                      {"cart": cart, "fruits": fruits})
```

---

## 8. URLs (`store/urls.py` & `client_app/urls.py`)

```python
# store/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("login/",   views.login_view,  name="login"),
    path("logout/",  views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Admin – Fruits
    path("admin-dash/",                    views.admin_fruits,       name="admin-dash"),
    path("admin/fruits/create/",           views.admin_fruit_create, name="admin-fruit-create"),
    path("admin/fruits/<int:pk>/edit/",    views.admin_fruit_edit,   name="admin-fruit-edit"),
    path("admin/fruits/<int:pk>/delete/",  views.admin_fruit_delete, name="admin-fruit-delete"),

    # Admin – Carts
    path("admin/carts/",                                             views.admin_carts,        name="admin-carts"),
    path("admin/carts/create/",                                      views.admin_cart_create,  name="admin-cart-create"),
    path("admin/carts/<int:pk>/delete/",                             views.admin_cart_delete,  name="admin-cart-delete"),
    path("admin/carts/<int:cart_pk>/items/add/",                     views.admin_item_add,     name="admin-item-add"),
    path("admin/carts/<int:cart_pk>/items/<int:item_pk>/update/",    views.admin_item_update,  name="admin-item-update"),
    path("admin/carts/<int:cart_pk>/items/<int:item_pk>/delete/",    views.admin_item_delete,  name="admin-item-delete"),

    # Customer
    path("customer-dash/",                                              views.customer_dashboard,   name="customer-dash"),
    path("customer/carts/create/",                                      views.customer_cart_create, name="customer-cart-create"),
    path("customer/carts/<int:pk>/delete/",                             views.customer_cart_delete, name="customer-cart-delete"),
    path("customer/carts/<int:cart_pk>/items/add/",                     views.customer_item_add,    name="customer-item-add"),
    path("customer/carts/<int:cart_pk>/items/<int:item_pk>/update/",    views.customer_item_update, name="customer-item-update"),
    path("customer/carts/<int:cart_pk>/items/<int:item_pk>/delete/",    views.customer_item_delete, name="customer-item-delete"),
]
```

```python
# client_app/urls.py
from django.urls import path, include

urlpatterns = [
    path("", include("store.urls")),
]
```

---

## 9. Templates

### 9.1 Login (`store/templates/store/login.html`)

```html
{% extends "store/base.html" %}
{% block title %} — Login{% endblock %}

{% block content %}
<div class="flex min-h-[70vh] items-center justify-center">
  <div class="card w-96 bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-2xl mb-4">🍉 Sign In</h2>

      {% if messages %}
        {% for m in messages %}
          <div class="alert alert-error"><span>{{ m }}</span></div>
        {% endfor %}
      {% endif %}

      <form method="POST" action="/login/">
        {% csrf_token %}
        <label class="form-control mb-3">
          <span class="label-text">Username</span>
          <input name="username" type="text" class="input input-bordered" required />
        </label>
        <label class="form-control mb-6">
          <span class="label-text">Password</span>
          <input name="password" type="password" class="input input-bordered" required />
        </label>
        <button class="btn btn-primary w-full">Login</button>
      </form>
    </div>
  </div>
</div>
{% endblock %}
```

---

### 9.2 Admin — Fruit List (`store/templates/store/admin/fruits/list.html`)

```html
{% extends "store/base.html" %}
{% block title %} — Manage Fruits{% endblock %}

{% block content %}
<div class="flex items-center justify-between mb-6">
  <h1 class="text-3xl font-bold">Fruits</h1>
  <div class="tabs tabs-boxed">
    <a class="tab tab-active">Fruits</a>
    <a class="tab" href="/admin/carts/">Carts</a>
  </div>
</div>

<!-- Inline create form -->
<div class="card bg-base-100 shadow mb-6">
  <div class="card-body">
    <h2 class="card-title text-lg">Add New Fruit</h2>
    <!--
      hx-post     : POST to create endpoint
      hx-target   : where to inject the response (the table body)
      hx-swap     : prepend the new row at the top
    -->
    <form hx-post="/admin/fruits/create/"
          hx-target="#fruit-tbody"
          hx-swap="beforeend"
          hx-on::after-request="this.reset()"
          class="flex flex-wrap gap-3 items-end">
      {% csrf_token %}
      <label class="form-control">
        <span class="label-text">Name</span>
        <input name="name" class="input input-bordered input-sm" required />
      </label>
      <label class="form-control">
        <span class="label-text">Weight (kg)</span>
        <input name="weight_kg" type="number" step="0.001" class="input input-bordered input-sm w-32" required />
      </label>
      <label class="form-control">
        <span class="label-text">Price / kg</span>
        <input name="price_per_kg" type="number" step="0.01" class="input input-bordered input-sm w-32" required />
      </label>
      <button class="btn btn-primary btn-sm">Add Fruit</button>
    </form>
  </div>
</div>

<!-- Fruits table -->
<div class="card bg-base-100 shadow overflow-x-auto">
  <table class="table table-zebra">
    <thead>
      <tr>
        <th>ID</th><th>Name</th><th>Weight (kg)</th><th>Price / kg</th><th>Actions</th>
      </tr>
    </thead>
    <tbody id="fruit-tbody">
      {% for fruit in fruits %}
        {% include "store/admin/fruits/_row.html" %}
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

---

### 9.3 Admin — Fruit Row Partial (`store/templates/store/admin/fruits/_row.html`)

```html
{% if not deleted %}
<tr id="fruit-row-{{ fruit.id }}">
  <td>{{ fruit.id }}</td>

  <td>{{ fruit.name }}</td>
  <td>{{ fruit.weight_kg }}</td>
  <td>${{ fruit.price_per_kg }}</td>

  <td class="flex gap-2">
    <!--
      hx-get    : fetch the edit form partial
      hx-target : replace this entire row
      hx-swap   : outerHTML so the <tr> is fully replaced
    -->
    <button class="btn btn-xs btn-warning"
            hx-get="/admin/fruits/{{ fruit.id }}/edit/"
            hx-target="#fruit-row-{{ fruit.id }}"
            hx-swap="outerHTML">
      Edit
    </button>

    <!--
      hx-delete  : send DELETE request
      hx-target  : replace the row
      hx-swap    : outerHTML removes the row from DOM
      hx-confirm : native browser confirm dialog before deletion
    -->
    <button class="btn btn-xs btn-error"
            hx-delete="/admin/fruits/{{ fruit.id }}/delete/"
            hx-target="#fruit-row-{{ fruit.id }}"
            hx-swap="outerHTML"
            hx-confirm="Delete {{ fruit.name }}?">
      Delete
    </button>
  </td>
</tr>
{% endif %}
```

---

### 9.4 Admin — Fruit Form Partial (`store/templates/store/admin/fruits/_form.html`)

```html
<!-- Inline edit or create form row — swapped in by HTMX -->
<tr id="{% if fruit %}fruit-row-{{ fruit.id }}{% else %}fruit-new-row{% endif %}">
  <td>{{ fruit.id|default:"—" }}</td>
  <td>
    <form hx-post="{% if action == 'edit' %}/admin/fruits/{{ fruit.id }}/edit/{% else %}/admin/fruits/create/{% endif %}"
          hx-target="#{% if fruit %}fruit-row-{{ fruit.id }}{% else %}fruit-tbody{% endif %}"
          hx-swap="{% if action == 'edit' %}outerHTML{% else %}afterbegin{% endif %}"
          class="flex flex-wrap gap-2 items-center">
      {% csrf_token %}
      <input name="name" value="{{ fruit.name|default:'' }}"
             class="input input-bordered input-xs w-28" placeholder="Name" required />
      <input name="weight_kg" value="{{ fruit.weight_kg|default:'' }}" type="number" step="0.001"
             class="input input-bordered input-xs w-24" placeholder="kg" required />
      <input name="price_per_kg" value="{{ fruit.price_per_kg|default:'' }}" type="number" step="0.01"
             class="input input-bordered input-xs w-24" placeholder="$/kg" required />
      <button class="btn btn-xs btn-success">Save</button>
      <!-- Cancel re-fetches the original read-only row -->
      {% if action == "edit" %}
        <button type="button" class="btn btn-xs btn-ghost"
                hx-get="/admin/fruits/{{ fruit.id }}/edit/"
                hx-target="#fruit-row-{{ fruit.id }}"
                hx-swap="outerHTML">
          Cancel
        </button>
      {% endif %}
    </form>
  </td>
</tr>
```

---

### 9.5 Admin — Cart List (`store/templates/store/admin/carts/list.html`)

```html
{% extends "store/base.html" %}
{% block title %} — Manage Carts{% endblock %}

{% block content %}
<div class="flex items-center justify-between mb-6">
  <h1 class="text-3xl font-bold">All Carts</h1>
  <div class="tabs tabs-boxed">
    <a class="tab" href="/admin-dash/">Fruits</a>
    <a class="tab tab-active">Carts</a>
  </div>
</div>

<!-- Create cart button -->
<div class="mb-6">
  <!--
    hx-post   : create a new cart
    hx-target : prepend the new cart card into the grid
  -->
  <button class="btn btn-primary"
          hx-post="/admin/carts/create/"
          hx-target="#carts-grid"
          hx-swap="afterbegin">
    + New Cart
  </button>
</div>

<!-- Carts grid -->
<div id="carts-grid" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {% for cart in carts %}
    {% include "store/admin/carts/_cart_card.html" %}
  {% endfor %}
</div>
{% endblock %}
```

---

### 9.6 Admin — Cart Card Partial (`store/templates/store/admin/carts/_cart_card.html`)

```html
{% if not deleted %}
<div class="card bg-base-100 shadow" id="cart-card-{{ cart.id }}">
  <div class="card-body p-4">

    <div class="flex justify-between items-center">
      <h3 class="card-title text-base">Cart #{{ cart.id }}
        <span class="badge badge-ghost text-xs">owner: {{ cart.owner }}</span>
      </h3>
      <!--
        hx-delete  : delete the cart
        hx-target  : the card itself
        hx-swap    : outerHTML removes the card from the grid
      -->
      <button class="btn btn-xs btn-error"
              hx-delete="/admin/carts/{{ cart.id }}/delete/"
              hx-target="#cart-card-{{ cart.id }}"
              hx-swap="outerHTML"
              hx-confirm="Delete Cart #{{ cart.id }}?">
        Delete Cart
      </button>
    </div>

    <!-- Items table -->
    <table class="table table-xs mt-2">
      <thead>
        <tr><th>Fruit</th><th>Qty (kg)</th><th>Subtotal</th><th></th></tr>
      </thead>
      <tbody>
        {% for item in cart.items %}
        <tr id="item-row-{{ item.id }}">
          <td>{{ item.fruit_name }}</td>
          <td>
            <!-- Inline qty edit form -->
            <form hx-post="/admin/carts/{{ cart.id }}/items/{{ item.id }}/update/"
                  hx-target="#cart-card-{{ cart.id }}"
                  hx-swap="outerHTML"
                  class="flex gap-1">
              {% csrf_token %}
              <input name="quantity_kg" value="{{ item.quantity_kg }}"
                     type="number" step="0.001" min="0.001"
                     class="input input-bordered input-xs w-20" />
              <button class="btn btn-xs btn-success">✓</button>
            </form>
          </td>
          <td>${{ item.subtotal }}</td>
          <td>
            <button class="btn btn-xs btn-ghost text-error"
                    hx-delete="/admin/carts/{{ cart.id }}/items/{{ item.id }}/delete/"
                    hx-target="#cart-card-{{ cart.id }}"
                    hx-swap="outerHTML">✕</button>
          </td>
        </tr>
        {% empty %}
          <tr><td colspan="4" class="text-center text-base-content/50 text-xs">No items yet.</td></tr>
        {% endfor %}
      </tbody>
    </table>

    <!-- Total -->
    <div class="flex justify-end mt-2">
      <span class="font-bold text-sm">Total: ${{ cart.total }}</span>
    </div>

    <!-- Add item form -->
    <form hx-post="/admin/carts/{{ cart.id }}/items/add/"
          hx-target="#cart-card-{{ cart.id }}"
          hx-swap="outerHTML"
          hx-on::after-request="this.reset()"
          class="flex flex-wrap gap-2 items-end mt-3 pt-3 border-t border-base-200">
      {% csrf_token %}
      <label class="form-control">
        <span class="label-text text-xs">Fruit</span>
        <select name="fruit" class="select select-bordered select-xs">
          {% for f in fruits %}
            <option value="{{ f.id }}">{{ f.name }} (${{ f.price_per_kg }}/kg)</option>
          {% endfor %}
        </select>
      </label>
      <label class="form-control">
        <span class="label-text text-xs">Qty (kg)</span>
        <input name="quantity_kg" type="number" step="0.001" min="0.001"
               class="input input-bordered input-xs w-24" value="1.000" />
      </label>
      <button class="btn btn-xs btn-primary">Add Item</button>
    </form>

  </div>
</div>
{% endif %}
```

---

### 9.7 Customer — Dashboard (`store/templates/store/customer/dashboard.html`)

```html
{% extends "store/base.html" %}
{% block title %} — My Cart{% endblock %}

{% block content %}
<h1 class="text-3xl font-bold mb-6">My Shopping Carts 🛒</h1>

<div class="grid grid-cols-1 xl:grid-cols-3 gap-6">

  <!-- Left: Fruit catalogue (read-only) -->
  <div class="xl:col-span-1">
    <div class="card bg-base-100 shadow">
      <div class="card-body p-4">
        <h2 class="card-title text-lg mb-2">🍓 Available Fruits</h2>
        <div class="overflow-y-auto max-h-[60vh]">
          <table class="table table-xs">
            <thead><tr><th>Fruit</th><th>$/kg</th></tr></thead>
            <tbody>
              {% for f in fruits %}
              <tr>
                <td>{{ f.name }}</td>
                <td>${{ f.price_per_kg }}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- Right: Customer carts -->
  <div class="xl:col-span-2">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">My Carts</h2>
      <!--
        hx-post   : create a new cart for this customer
        hx-target : prepend new cart card into the carts grid
      -->
      <button class="btn btn-primary btn-sm"
              hx-post="/customer/carts/create/"
              hx-target="#my-carts"
              hx-swap="afterbegin">
        + New Cart
      </button>
    </div>

    <div id="my-carts" class="flex flex-col gap-4">
      {% for cart in carts %}
        {% include "store/customer/carts/_cart_card.html" %}
      {% empty %}
        <div class="text-center text-base-content/50 py-12">
          No carts yet. Create one to start shopping!
        </div>
      {% endfor %}
    </div>
  </div>

</div>
{% endblock %}
```

---

### 9.8 Customer — Cart Card Partial (`store/templates/store/customer/carts/_cart_card.html`)

```html
{% if not deleted %}
<div class="card bg-base-100 shadow" id="my-cart-{{ cart.id }}">
  <div class="card-body p-4">

    <div class="flex justify-between items-center">
      <h3 class="font-bold">Cart #{{ cart.id }}</h3>
      <button class="btn btn-xs btn-error"
              hx-delete="/customer/carts/{{ cart.id }}/delete/"
              hx-target="#my-cart-{{ cart.id }}"
              hx-swap="outerHTML"
              hx-confirm="Remove Cart #{{ cart.id }}?">
        Remove
      </button>
    </div>

    <!-- Items -->
    <table class="table table-xs mt-2">
      <thead>
        <tr><th>Fruit</th><th>Qty (kg)</th><th>Subtotal</th><th></th></tr>
      </thead>
      <tbody>
        {% for item in cart.items %}
        <tr>
          <td>{{ item.fruit_name }}</td>
          <td>
            <form hx-post="/customer/carts/{{ cart.id }}/items/{{ item.id }}/update/"
                  hx-target="#my-cart-{{ cart.id }}"
                  hx-swap="outerHTML"
                  class="flex gap-1">
              {% csrf_token %}
              <input name="quantity_kg" value="{{ item.quantity_kg }}"
                     type="number" step="0.001" min="0.001"
                     class="input input-bordered input-xs w-20" />
              <button class="btn btn-xs btn-success">✓</button>
            </form>
          </td>
          <td>${{ item.subtotal }}</td>
          <td>
            <button class="btn btn-xs btn-ghost text-error"
                    hx-delete="/customer/carts/{{ cart.id }}/items/{{ item.id }}/delete/"
                    hx-target="#my-cart-{{ cart.id }}"
                    hx-swap="outerHTML">✕</button>
          </td>
        </tr>
        {% empty %}
          <tr><td colspan="4" class="text-center text-base-content/50 text-xs py-2">Empty cart.</td></tr>
        {% endfor %}
      </tbody>
    </table>

    <!-- Total -->
    <div class="divider my-1"></div>
    <div class="flex justify-end font-bold">Total: ${{ cart.total }}</div>

    <!-- Add item form -->
    <form hx-post="/customer/carts/{{ cart.id }}/items/add/"
          hx-target="#my-cart-{{ cart.id }}"
          hx-swap="outerHTML"
          hx-on::after-request="this.reset()"
          class="flex flex-wrap gap-2 items-end mt-3 pt-3 border-t border-base-200">
      {% csrf_token %}
      <label class="form-control">
        <span class="label-text text-xs">Fruit</span>
        <select name="fruit" class="select select-bordered select-xs">
          {% for f in fruits %}
            <option value="{{ f.id }}">{{ f.name }} (${{ f.price_per_kg }}/kg)</option>
          {% endfor %}
        </select>
      </label>
      <label class="form-control">
        <span class="label-text text-xs">Qty (kg)</span>
        <input name="quantity_kg" type="number" step="0.001" min="0.001"
               class="input input-bordered input-xs w-24" value="1.000" />
      </label>
      <button class="btn btn-xs btn-primary">Add</button>
    </form>

  </div>
</div>
{% endif %}
```

---

## 10. HTMX Pattern Reference

| Operation | HTMX attribute | Swap strategy | Target |
|-----------|---------------|---------------|--------|
| Create fruit | `hx-post` | `afterbegin` | `#fruit-tbody` |
| Edit fruit (open form) | `hx-get` | `outerHTML` | `#fruit-row-{id}` |
| Save edit | `hx-post` | `outerHTML` | `#fruit-row-{id}` |
| Delete fruit | `hx-delete` | `outerHTML` | `#fruit-row-{id}` |
| Create cart | `hx-post` | `afterbegin` | `#carts-grid` / `#my-carts` |
| Delete cart | `hx-delete` | `outerHTML` | `#cart-card-{id}` |
| Add/update/delete item | `hx-post` / `hx-delete` | `outerHTML` | `#cart-card-{id}` (re-renders full card with new total) |

> **Why re-render the whole cart card on item changes?**
> The cart total and every subtotal must be consistent after any mutation. Swapping the entire card from the server ensures the displayed numbers always match the API — no client-side math required.

---

## 11. CSRF Token for Non-Form HTMX Requests

Django requires CSRF tokens on state-changing requests. Add this snippet once in `base.html` so HTMX automatically attaches the token to every request header:

```html
<!-- Add inside <body>, anywhere after HTMX is loaded -->
<script>
  document.body.addEventListener("htmx:configRequest", (e) => {
    e.detail.headers["X-CSRFToken"] =
      document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? "";
  });
</script>
```

Also ensure Django's CSRF middleware is active (it is by default):

```python
# settings.py
MIDDLEWARE = [
    ...
    "django.middleware.csrf.CsrfViewMiddleware",
    ...
]
```

---

## 12. Run the App

```bash
python manage.py migrate
python manage.py runserver 8001   # use port 8001 so it doesn't clash with the API on 8000
```

Visit `http://127.0.0.1:8001/login/` and sign in as an admin or customer.

---

## 13. Full Feature Matrix

| Feature | Admin | Customer |
|---------|-------|----------|
| Browse fruit catalogue | ✅ | ✅ (read-only) |
| Add / edit / delete fruits | ✅ | ✗ |
| View all carts (any user) | ✅ | ✗ |
| View own carts only | ✅ | ✅ |
| Create / delete carts | ✅ | ✅ |
| Add / update / remove cart items | ✅ | ✅ |
| See per-item subtotals + cart total | ✅ | ✅ |
