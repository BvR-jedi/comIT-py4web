# Building a Django Client App for the Cats API

This guide walks you through creating a Django web application that consumes the Cats REST API using class-based views (CBVs) and the `requests` library. The client performs full CRUD operations: list, detail, create, update, and delete.

---

## Prerequisites

- Python 3.10+
- The Cats API server running at `http://127.0.0.1:8000`
- A virtual environment (recommended)

---

## 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install django requests
```

---

## 2. Create the Project and App

```bash
django-admin startproject cat_client .
python manage.py startapp cats_client
```

Register the app in `cat_client/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'cats_client',
]
```

---

## 3. Project Structure

When finished, the relevant files will look like this:

```
cat_client/
│
├── cat_client/
│   ├── settings.py
│   └── urls.py
│
└── cats_client/
    ├── services.py        # All API communication lives here
    ├── views.py           # Class-based views
    ├── urls.py            # App URL patterns
    └── templates/
        └── cats_client/
            ├── cat_list.html
            ├── cat_detail.html
            ├── cat_form.html
            └── cat_confirm_delete.html
```

---

## 4. API Service Layer

Create `cats_client/services.py`. This module centralises every HTTP call to the Cats API so the views stay clean.

```python
import requests

API_BASE = "http://127.0.0.1:8000/api/cats/"
AUTH = ("admin", "password")  # Replace or load from settings/environment


def get_all_cats():
    response = requests.get(API_BASE, auth=AUTH)
    response.raise_for_status()
    return response.json()


def get_cat(cat_id):
    response = requests.get(f"{API_BASE}{cat_id}/", auth=AUTH)
    response.raise_for_status()
    return response.json()


def create_cat(data):
    response = requests.post(API_BASE, json=data, auth=AUTH)
    response.raise_for_status()
    return response.json()


def update_cat(cat_id, data):
    response = requests.put(f"{API_BASE}{cat_id}/", json=data, auth=AUTH)
    response.raise_for_status()
    return response.json()


def delete_cat(cat_id):
    response = requests.delete(f"{API_BASE}{cat_id}/", auth=AUTH)
    response.raise_for_status()
```

> **Tip:** Move `AUTH` credentials to Django settings or environment variables rather than hardcoding them.

---

## 5. Class-Based Views

Create `cats_client/views.py` with one view class per CRUD operation.

```python
from django.views import View
from django.shortcuts import render, redirect
from . import services


class CatListView(View):
    """GET /cats/ — list all cats."""

    def get(self, request):
        cats = services.get_all_cats()
        return render(request, "cats_client/cat_list.html", {"cats": cats})


class CatDetailView(View):
    """GET /cats/<id>/ — show a single cat."""

    def get(self, request, cat_id):
        cat = services.get_cat(cat_id)
        return render(request, "cats_client/cat_detail.html", {"cat": cat})


class CatCreateView(View):
    """GET renders the form; POST submits it to the API."""

    def get(self, request):
        return render(request, "cats_client/cat_form.html", {"action": "Create"})

    def post(self, request):
        data = {
            "name":       request.POST.get("name"),
            "kind":       request.POST.get("kind"),
            "age":        int(request.POST.get("age", 0)),
            "weight":     float(request.POST.get("weight", 0)),
            "vaccinated": request.POST.get("vaccinated") == "on",
        }
        services.create_cat(data)
        return redirect("cat-list")


class CatUpdateView(View):
    """GET pre-fills the form; PUT sends the update to the API."""

    def get(self, request, cat_id):
        cat = services.get_cat(cat_id)
        return render(request, "cats_client/cat_form.html", {"cat": cat, "action": "Update"})

    def post(self, request, cat_id):
        data = {
            "name":       request.POST.get("name"),
            "kind":       request.POST.get("kind"),
            "age":        int(request.POST.get("age", 0)),
            "weight":     float(request.POST.get("weight", 0)),
            "vaccinated": request.POST.get("vaccinated") == "on",
        }
        services.update_cat(cat_id, data)
        return redirect("cat-detail", cat_id=cat_id)


class CatDeleteView(View):
    """GET shows a confirmation page; POST performs the deletion."""

    def get(self, request, cat_id):
        cat = services.get_cat(cat_id)
        return render(request, "cats_client/cat_confirm_delete.html", {"cat": cat})

    def post(self, request, cat_id):
        services.delete_cat(cat_id)
        return redirect("cat-list")
```

---

## 6. URL Configuration

Create `cats_client/urls.py`:

```python
from django.urls import path
from .views import (
    CatListView,
    CatDetailView,
    CatCreateView,
    CatUpdateView,
    CatDeleteView,
)

urlpatterns = [
    path("",               CatListView.as_view(),   name="cat-list"),
    path("<int:cat_id>/",  CatDetailView.as_view(), name="cat-detail"),
    path("new/",           CatCreateView.as_view(), name="cat-create"),
    path("<int:cat_id>/edit/",   CatUpdateView.as_view(), name="cat-update"),
    path("<int:cat_id>/delete/", CatDeleteView.as_view(), name="cat-delete"),
]
```

Then include them in `cat_client/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cats/", include("cats_client.urls")),
]
```

---

## 7. Templates

Create the directory structure first:

```bash
mkdir -p cats_client/templates/cats_client
```

### cat_list.html

Displays all cats with links to detail, edit, and delete.

```html
<!DOCTYPE html>
<html>
<head><title>Cats</title></head>
<body>

<h1>All Cats</h1>
<a href="{% url 'cat-create' %}">Add New Cat</a>

<table border="1">
  <thead>
    <tr>
      <th>ID</th>
      <th>Name</th>
      <th>Kind</th>
      <th>Age</th>
      <th>Weight (kg)</th>
      <th>Vaccinated</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for cat in cats %}
    <tr>
      <td>{{ cat.id }}</td>
      <td>{{ cat.name }}</td>
      <td>{{ cat.kind }}</td>
      <td>{{ cat.age }}</td>
      <td>{{ cat.weight }}</td>
      <td>{{ cat.vaccinated|yesno:"Yes,No" }}</td>
      <td>
        <a href="{% url 'cat-detail' cat.id %}">View</a> |
        <a href="{% url 'cat-update' cat.id %}">Edit</a> |
        <a href="{% url 'cat-delete' cat.id %}">Delete</a>
      </td>
    </tr>
    {% empty %}
    <tr><td colspan="7">No cats found.</td></tr>
    {% endfor %}
  </tbody>
</table>

</body>
</html>
```

### cat_detail.html

Shows all fields for a single cat.

```html
<!DOCTYPE html>
<html>
<head><title>{{ cat.name }}</title></head>
<body>

<h1>{{ cat.name }}</h1>

<ul>
  <li><strong>ID:</strong> {{ cat.id }}</li>
  <li><strong>Kind:</strong> {{ cat.kind }}</li>
  <li><strong>Age:</strong> {{ cat.age }}</li>
  <li><strong>Weight:</strong> {{ cat.weight }} kg</li>
  <li><strong>Vaccinated:</strong> {{ cat.vaccinated|yesno:"Yes,No" }}</li>
</ul>

<a href="{% url 'cat-update' cat.id %}">Edit</a> |
<a href="{% url 'cat-delete' cat.id %}">Delete</a> |
<a href="{% url 'cat-list' %}">Back to list</a>

</body>
</html>
```

### cat_form.html

Shared form for both create and update. When `cat` is present in context, fields are pre-filled.

```html
<!DOCTYPE html>
<html>
<head><title>{{ action }} Cat</title></head>
<body>

<h1>{{ action }} Cat</h1>

<form method="post">
  {% csrf_token %}

  <label for="name">Name</label><br>
  <input type="text" id="name" name="name" value="{{ cat.name }}" required><br><br>

  <label for="kind">Kind</label><br>
  <input type="text" id="kind" name="kind" value="{{ cat.kind }}" required><br><br>

  <label for="age">Age</label><br>
  <input type="number" id="age" name="age" value="{{ cat.age }}" min="0" required><br><br>

  <label for="weight">Weight (kg)</label><br>
  <input type="number" id="weight" name="weight" value="{{ cat.weight }}"
         step="0.1" min="0" required><br><br>

  <label for="vaccinated">
    <input type="checkbox" id="vaccinated" name="vaccinated"
           {% if cat.vaccinated %}checked{% endif %}>
    Vaccinated
  </label><br><br>

  <button type="submit">{{ action }}</button>
  <a href="{% url 'cat-list' %}">Cancel</a>
</form>

</body>
</html>
```

### cat_confirm_delete.html

Asks the user to confirm before deleting.

```html
<!DOCTYPE html>
<html>
<head><title>Delete {{ cat.name }}</title></head>
<body>

<h1>Delete {{ cat.name }}?</h1>
<p>Are you sure you want to delete <strong>{{ cat.name }}</strong> ({{ cat.kind }})?
   This action cannot be undone.</p>

<form method="post">
  {% csrf_token %}
  <button type="submit">Yes, delete</button>
  <a href="{% url 'cat-detail' cat.id %}">Cancel</a>
</form>

</body>
</html>
```

---

## 8. Run the Client App

```bash
python manage.py migrate
python manage.py runserver 8001
```

> Run on port **8001** so it does not clash with the Cats API server on port 8000.

Open your browser at `http://127.0.0.1:8001/cats/`.

---

## 9. URL Reference

| URL | View | Purpose |
|---|---|---|
| `/cats/` | `CatListView` | List all cats |
| `/cats/<id>/` | `CatDetailView` | View a single cat |
| `/cats/new/` | `CatCreateView` | Create a cat |
| `/cats/<id>/edit/` | `CatUpdateView` | Edit a cat |
| `/cats/<id>/delete/` | `CatDeleteView` | Delete a cat |

---

## 10. Error Handling (Optional Improvement)

Wrap service calls in views to handle API errors gracefully:

```python
from requests.exceptions import HTTPError
from django.http import HttpResponseNotFound, HttpResponseServerError

class CatDetailView(View):
    def get(self, request, cat_id):
        try:
            cat = services.get_cat(cat_id)
        except HTTPError as e:
            if e.response.status_code == 404:
                return HttpResponseNotFound("<h1>Cat not found</h1>")
            return HttpResponseServerError("<h1>API error</h1>")
        return render(request, "cats_client/cat_detail.html", {"cat": cat})
```

Apply the same pattern to the remaining views as needed.
