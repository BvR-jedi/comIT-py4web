# 📋 Django To-Do List App — Full Guide

**Stack:** Django · SQLite · Tailwind CSS  
**Estimated Time:** 30–45 minutes  

---

## Prerequisites

Make sure these are installed before you start:

- **Python 3.10+** → [python.org](https://www.python.org/)
- **pip** (comes with Python)
- **A terminal / command prompt**

---

## STEP 1 — Create the Project & App

Open your terminal and run these commands one by one:

```bash
# 1.1  Create a new folder and move into it
mkdir todoproject
cd todoproject

# 1.2  Create a virtual environment
python -m venv venv

# 1.3  Activate the virtual environment
#      👉 Windows:
venv\Scripts\activate
#      👉 macOS / Linux:
source venv/bin/activate

# 1.4  Install Django
pip install django

# 1.5  Start the Django project
django-admin startproject todoproject .

# 1.6  Create the todo app
python manage.py startapp todos
```

Your folder structure should now look like this:

```
todoproject/
├── manage.py
├── todoproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── todos/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── views.py
    └── ...
```

---

## STEP 2 — Register the App in Settings

Open **`todoproject/settings.py`** and find the `INSTALLED_APPS` list.  
Add `'todos'` at the end:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'todos',                          # ← add this line
]
```

---

## STEP 3 — Define the Model

Open **`todos/models.py`** and replace its contents with:

```python
from django.db import models


class Todo(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']   # newest first

    def __str__(self):
        return self.title
```

### What each field does

| Field         | Purpose                                        |
|---------------|------------------------------------------------|
| `title`       | Short name of the task (required)              |
| `description` | Optional longer details                        |
| `completed`   | Checkbox toggle — `True` / `False`             |
| `created_at`  | Timestamp set automatically on creation        |
| `updated_at`  | Timestamp updated automatically on every save |

---

## STEP 4 — Run Migrations (Creates the SQLite DB)

```bash
python manage.py makemigrations
python manage.py migrate
```

Django automatically creates a **`db.sqlite3`** file in your project root.  
No database server needed — it's just a single file.

---

## STEP 5 — Register the Model in Admin (Optional but Handy)

Open **`todos/admin.py`** and replace its contents with:

```python
from django.contrib import admin
from .models import Todo

admin.site.register(Todo)
```

This lets you manage todos from Django's built-in admin panel at `/admin/`.

---

## STEP 6 — Create the Views

Open **`todos/views.py`** and replace its contents with:

```python
from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo
from .forms import TodoForm


# ── List all todos ─────────────────────────────────
def todo_list(request):
    todos          = Todo.objects.all()
    completed_count = todos.filter(completed=True).count()
    pending_count   = todos.filter(completed=False).count()
    return render(request, 'todos/todo_list.html', {
        'todos':           todos,
        'completed_count': completed_count,
        'pending_count':   pending_count,
    })


# ── Add a new todo ─────────────────────────────────
def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
    else:
        form = TodoForm()
    return render(request, 'todos/todo_form.html', {'form': form})


# ── Edit an existing todo ──────────────────────────
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todos/todo_form.html', {'form': form})


# ── Delete a todo ──────────────────────────────────
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        todo.delete()
        return redirect('todo_list')
    return render(request, 'todos/todo_confirm_delete.html', {'todo': todo})


# ── Toggle completed status (AJAX-friendly) ────────
def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo_list')
```

---

## STEP 7 — Create the Form

Create a new file **`todos/forms.py`**:

```python
from django import forms
from .models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model  = Todo
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 '
                         'focus:outline-none focus:ring-2 focus:ring-indigo-400 '
                         'bg-white text-gray-800 placeholder-gray-400',
                'placeholder': 'What needs to be done?',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 '
                         'focus:outline-none focus:ring-2 focus:ring-indigo-400 '
                         'bg-white text-gray-800 placeholder-gray-400',
                'placeholder': 'Add a description (optional)…',
                'rows': 3,
            }),
        }
```

---

## STEP 8 — Wire Up the URLs

### 8a — App-level URLs

Create a new file **`todos/urls.py`**:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.todo_list,   name='todo_list'),
    path('create/',             views.todo_create, name='todo_create'),
    path('<int:pk>/update/',    views.todo_update, name='todo_update'),
    path('<int:pk>/delete/',    views.todo_delete, name='todo_delete'),
    path('<int:pk>/toggle/',    views.todo_toggle, name='todo_toggle'),
]
```

### 8b — Project-level URLs

Open **`todoproject/urls.py`** and replace its contents with:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todos.urls')),
]
```

---

## STEP 9 — Create the Templates

Create the folder structure first:

```
todos/
└── templates/
    └── todos/
        ├── base.html
        ├── todo_list.html
        ├── todo_form.html
        └── todo_confirm_delete.html
```

### 9a — `base.html` (shared layout)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My To-Do List</title>

  <!-- Tailwind CSS via CDN (swap to PostCSS build in production) -->
  <script src="https://cdn.tailwindcss.com"></script>

  <style>
    /* Subtle animated gradient background */
    @keyframes gradientShift {
      0%   { background-position: 0%   50%; }
      50%  { background-position: 100% 50%; }
      100% { background-position: 0%   50%; }
    }
    body {
      background: linear-gradient(135deg, #eef2ff, #fdf2f8, #ede9fe);
      background-size: 200% 200%;
      animation: gradientShift 8s ease infinite;
    }

    /* Smooth fade-in for todo cards */
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .todo-card {
      animation: fadeInUp 0.3s ease both;
    }
  </style>
</head>
<body class="min-h-screen flex items-start justify-center py-14 px-4">

  <div class="w-full max-w-2xl">
    <!-- Header -->
    <div class="text-center mb-10">
      <h1 class="text-5xl font-extrabold text-gray-800 tracking-tight">
        ✅ My To-Do List
      </h1>
      <p class="text-gray-500 mt-2 text-lg">Stay organised, stay on top.</p>
    </div>

    <!-- Page content injected here -->
    {% block content %}{% endblock %}
  </div>

</body>
</html>
```

---

### 9b — `todo_list.html` (main page)

```html
{% extends 'todos/base.html' %}

{% block content %}

<!-- Add-Todo Button -->
<div class="flex justify-end mb-4">
  <a href="{% url 'todo_create' %}"
     class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700
            text-white font-semibold py-2.5 px-6 rounded-xl shadow-md
            transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5">
    <span class="text-xl leading-none">+</span> New Task
  </a>
</div>

<!-- Stats Bar -->
<div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-4">
  <!-- Progress bar track -->
  <div class="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden mb-3">
    <div class="h-full bg-emerald-400 rounded-full transition-all duration-500"
         style="width: {% if todos|length > 0 %}{% widthratio completed_count todos|length 100 %}{% else %}0{% endif %}%;"></div>
  </div>
  <!-- Labels -->
  <div class="flex justify-between text-sm">
    <span class="text-gray-500">
      <span class="font-semibold text-gray-700">{{ todos|length }}</span> task{{ todos|length|pluralize }}
    </span>
    <span class="text-gray-500">
      <span class="font-semibold text-emerald-600">{{ completed_count }}</span> completed ·
      <span class="font-semibold text-indigo-600">{{ pending_count }}</span> pending
    </span>
  </div>
</div>

<!-- Todo Cards -->
{% if todos %}
  {% for todo in todos %}
  <div class="todo-card mb-3" style="animation-delay: {{ forloop.counter0 }}00ms;">
    <div class="flex items-start gap-3 bg-white rounded-2xl shadow-sm
                border border-gray-100 p-4 transition-all duration-200
                hover:shadow-md {% if todo.completed %} opacity-60 {% endif %}">

      <!-- Checkbox (toggle link) -->
      <a href="{% url 'todo_toggle' todo.pk %}"
         class="mt-1 flex-shrink-0 w-6 h-6 rounded-lg border-2
                {% if todo.completed %}
                  border-emerald-400 bg-emerald-400 flex items-center justify-center
                {% else %}
                  border-gray-300 hover:border-indigo-400
                {% endif %}
                transition-colors duration-200">
        {% if todo.completed %}
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor"
               stroke-width="3" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M5 13l4 4L19 7" />
          </svg>
        {% endif %}
      </a>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <h3 class="text-base font-semibold text-gray-800
                   {% if todo.completed %} line-through text-gray-400 {% endif %}">
          {{ todo.title }}
        </h3>
        {% if todo.description %}
          <p class="text-sm text-gray-500 mt-0.5 truncate">{{ todo.description }}</p>
        {% endif %}
        <p class="text-xs text-gray-400 mt-1">
          Added {{ todo.created_at|date:"M j, Y" }}
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <a href="{% url 'todo_update' todo.pk %}"
           class="text-gray-400 hover:text-indigo-500 transition-colors duration-200">
          <!-- Pencil icon -->
          <svg class="w-5 h-5" fill="none" stroke="currentColor"
               stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </a>
        <a href="{% url 'todo_delete' todo.pk %}"
           class="text-gray-400 hover:text-red-500 transition-colors duration-200">
          <!-- Trash icon -->
          <svg class="w-5 h-5" fill="none" stroke="currentColor"
               stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </a>
      </div>

    </div>
  </div>
  {% endfor %}

{% else %}
  <!-- Empty State -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
    <div class="text-6xl mb-4">🎉</div>
    <p class="text-gray-500 text-lg font-medium">No tasks yet!</p>
    <p class="text-gray-400 text-sm mt-1">
      <a href="{% url 'todo_create' %}" class="text-indigo-500 hover:underline">
        Create your first task
      </a>
    </p>
  </div>
{% endif %}

{% endblock %}
```

---

### 9c — `todo_form.html` (create & edit)

```html
{% extends 'todos/base.html' %}

{% block content %}

<div class="bg-white rounded-2xl shadow-md border border-gray-100 p-8">

  <h2 class="text-2xl font-bold text-gray-800 mb-1">
    {% if form.instance.pk %} ✏️ Edit Task {% else %} 📝 New Task {% endif %}
  </h2>
  <p class="text-gray-400 text-sm mb-6">
    {% if form.instance.pk %}
      Update the details below.
    {% else %}
      Fill in the details and hit Save.
    {% endif %}
  </p>

  <form method="post">
    {% csrf_token %}

    <!-- Title -->
    <label class="block text-sm font-semibold text-gray-600 mb-1">Title</label>
    {{ form.title }}
    {% if form.title.errors %}
      <p class="text-red-500 text-xs mt-1">{{ form.title.errors|first }}</p>
    {% endif %}

    <!-- Description -->
    <label class="block text-sm font-semibold text-gray-600 mt-5 mb-1">Description</label>
    {{ form.description }}

    <!-- Buttons -->
    <div class="flex gap-3 mt-8">
      <button type="submit"
              class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white
                     font-semibold py-3 rounded-xl shadow transition-all
                     duration-200 hover:shadow-md hover:-translate-y-0.5">
        {% if form.instance.pk %} Save Changes {% else %} Add Task {% endif %}
      </button>
      <a href="{% url 'todo_list' %}"
         class="px-5 py-3 rounded-xl border border-gray-200 text-gray-600
                hover:bg-gray-50 font-medium transition-colors duration-200">
        Cancel
      </a>
    </div>
  </form>
</div>

{% endblock %}
```

---

### 9d — `todo_confirm_delete.html` (delete confirmation)

```html
{% extends 'todos/base.html' %}

{% block content %}

<div class="bg-white rounded-2xl shadow-md border border-gray-100 p-8 text-center">

  <div class="text-5xl mb-4">🗑️</div>
  <h2 class="text-xl font-bold text-gray-800 mb-2">Delete This Task?</h2>
  <p class="text-gray-500 mb-1">You are about to permanently delete:</p>
  <p class="text-indigo-600 font-semibold text-lg mb-6">"{{ todo.title }}"</p>

  <form method="post">
    {% csrf_token %}
    <div class="flex justify-center gap-3">
      <button type="submit"
              class="bg-red-500 hover:bg-red-600 text-white font-semibold
                     py-2.5 px-6 rounded-xl shadow transition-all duration-200
                     hover:shadow-md hover:-translate-y-0.5">
        Yes, Delete
      </button>
      <a href="{% url 'todo_list' %}"
         class="px-6 py-2.5 rounded-xl border border-gray-200 text-gray-600
                hover:bg-gray-50 font-medium transition-colors duration-200">
        Cancel
      </a>
    </div>
  </form>
</div>

{% endblock %}
```

---

## STEP 10 — Run the Server & Test

```bash
python manage.py runserver
```

Open your browser and go to:

```
http://127.0.0.1:8000/
```

You should see the To-Do List app live. Try adding, editing, completing, and deleting tasks.

---

## Quick-Reference Cheat Sheet

| What you want to do          | URL in your browser                  |
|------------------------------|--------------------------------------|
| See all tasks                | `http://127.0.0.1:8000/`            |
| Create a new task            | `http://127.0.0.1:8000/create/`     |
| Edit task #3                 | `http://127.0.0.1:8000/3/update/`   |
| Delete task #3               | `http://127.0.0.1:8000/3/delete/`   |
| Toggle task #3 done/undone   | `http://127.0.0.1:8000/3/toggle/`   |
| Django admin panel           | `http://127.0.0.1:8000/admin/`      |

---

## Common Errors & Fixes

| Error                                | Fix                                                                 |
|--------------------------------------|---------------------------------------------------------------------|
| `ModuleNotFoundError: todos`         | Make sure `'todos'` is in `INSTALLED_APPS` in `settings.py`         |
| `TemplateDoesNotExist`               | Double-check the folder path: `todos/templates/todos/`              |
| `no such table: todos_todo`          | Run `python manage.py migrate`                                      |
| Port 8000 already in use             | Use `python manage.py runserver 8001` and visit port `8001`         |
| Tailwind classes not applying        | Ensure the `<script src="https://cdn.tailwindcss.com"></script>` tag is in `base.html` |

---

## ⚡ Next Steps (Optional Upgrades)

1. **User authentication** — Each user sees only their own tasks (`request.user`).
2. **Due dates & priorities** — Add `DateField` and a `priority` choice field to the model.
3. **Category / tags** — Group tasks with a ForeignKey or ManyToMany relation.
4. **Search & filter** — Filter by completed / pending status.
5. **Production Tailwind** — Replace the CDN `<script>` with a PostCSS build for smaller CSS bundles.
6. **Deploy** — Push to Railway, Render, or any Django-friendly host.
