# 🚀 To-Do App Upgrade Guide
### User Auth · Due Dates · Priorities · Categories · Search & Filter

> **Prerequisite:** You have already completed the original 10-step guide and your app runs at `http://127.0.0.1:8000/`.  
> Every section below tells you *exactly* which file to open, what to remove, and what to paste in its place.

---

## UPGRADE 1 — User Authentication

Django ships a full auth system out of the box. This upgrade locks every todo to the logged-in user so nobody else can see or touch it.

### 1.1 — Add auth URLs to the project

Open **`todoproject/urls.py`** and replace it entirely:

```python
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('admin/',  admin.site.urls),
    path('login/',  auth_views.LoginView.as_view(template_name='todos/login.html'),  name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login', http_method_names=['post']), name='logout'),
    path('',        include('todos.urls')),
]
```

> **Note:** The logout view requires POST for security (prevents logout via malicious links).

### 1.2 — Add LOGIN_URL to settings

Open **`todoproject/settings.py`** and append these two lines at the very bottom of the file:

```python
LOGIN_URL      = '/login/'
LOGIN_REDIRECT_URL = '/'
```

### 1.3 — Update the model (add owner)

Open **`todos/models.py`** and replace it entirely:

```python
from django.conf import settings
from django.db import models


class Category(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    def __str__(self):
        return self.name


class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]

    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed   = models.BooleanField(default=False)
    priority    = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='medium')
    due_date    = models.DateField(null=True, blank=True)
    category    = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='todos',
    )
    owner       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='todos',
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
```

> **Why replace now?** The model is the single source of truth. Upgrades 2, 3, and 4 all depend on fields defined here — doing it once keeps the migrations clean and linear.

### 1.4 — Run migrations

```bash
python manage.py makemigrations
```

Django will ask: *"You are trying to add a non-nullable field 'owner' …"*  
Choose option **1** (provide a one-off default). Type **1** and press Enter (this sets existing rows to user ID 1 — fine for development).

```bash
python manage.py migrate
```

### 1.5 — Create a superuser (if you haven't already)

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

### 1.6 — Create the login template

Create the file **`todos/templates/todos/login.html`**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Log In</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
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
  </style>
</head>
<body class="min-h-screen flex items-center justify-center px-4">

  <div class="w-full max-w-sm bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
    <div class="text-center mb-8">
      <div class="text-5xl mb-3">✅</div>
      <h1 class="text-2xl font-extrabold text-gray-800">My To-Do List</h1>
      <p class="text-gray-400 text-sm mt-1">Sign in to manage your tasks</p>
    </div>

    {% if form.errors %}
      <div class="bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl px-4 py-3 mb-5">
        Invalid username or password. Please try again.
      </div>
    {% endif %}

    <form method="post">
      {% csrf_token %}

      <label class="block text-sm font-semibold text-gray-600 mb-1">Username</label>
      <input type="text" name="username" autocomplete="username" required
             class="w-full px-4 py-3 rounded-xl border border-gray-200
                    focus:outline-none focus:ring-2 focus:ring-indigo-400
                    bg-white text-gray-800 placeholder-gray-400 mb-4"
             placeholder="Enter username" />

      <label class="block text-sm font-semibold text-gray-600 mb-1">Password</label>
      <input type="password" name="password" autocomplete="current-password" required
             class="w-full px-4 py-3 rounded-xl border border-gray-200
                    focus:outline-none focus:ring-2 focus:ring-indigo-400
                    bg-white text-gray-800 placeholder-gray-400 mb-6"
             placeholder="Enter password" />

      <button type="submit"
              class="w-full bg-indigo-600 hover:bg-indigo-700 text-white
                     font-semibold py-3 rounded-xl shadow transition-all
                     duration-200 hover:shadow-md hover:-translate-y-0.5">
        Log In
      </button>
    </form>
  </div>

</body>
</html>
```

### 1.7 — Update base.html (add nav bar with logout)

Open **`todos/templates/todos/base.html`** and replace it entirely:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My To-Do List</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
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
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .todo-card { animation: fadeInUp 0.3s ease both; }
  </style>
</head>
<body class="min-h-screen flex flex-col px-4">

  <!-- Top Nav -->
  <nav class="max-w-2xl w-full mx-auto mt-6 mb-2 flex items-center justify-between">
    <span class="text-sm text-gray-500">
      Hello, <span class="font-semibold text-gray-700">{{ request.user.username }}</span>
    </span>
    <form method="post" action="{% url 'logout' %}" class="inline">
      {% csrf_token %}
      <button type="submit"
              class="text-sm text-gray-400 hover:text-red-500 transition-colors duration-200 bg-transparent border-0 cursor-pointer">
        Logout
      </button>
    </form>
  </nav>

  <!-- Main Container -->
  <div class="w-full max-w-2xl mx-auto flex-1 py-6">
    <div class="text-center mb-8">
      <h1 class="text-5xl font-extrabold text-gray-800 tracking-tight">✅ My To-Do List</h1>
      <p class="text-gray-500 mt-2 text-lg">Stay organised, stay on top.</p>
    </div>

    {% block content %}{% endblock %}
  </div>

</body>
</html>
```

---

## UPGRADE 2 — Due Dates & Priorities

The fields are already in the model from step 1.3. This upgrade wires them into the form and displays them on every card.

### 2.1 — Update the form

Open **`todos/forms.py`** and replace it entirely:

```python
from django import forms
from .models import Todo, Category


class TodoForm(forms.ModelForm):
    class Meta:
        model  = Todo
        fields = ['title', 'description', 'priority', 'due_date', 'category']
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
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 '
                         'focus:outline-none focus:ring-2 focus:ring-indigo-400 '
                         'bg-white text-gray-800',
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 '
                         'focus:outline-none focus:ring-2 focus:ring-indigo-400 '
                         'bg-white text-gray-800',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 '
                         'focus:outline-none focus:ring-2 focus:ring-indigo-400 '
                         'bg-white text-gray-800',
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 '
                         'focus:outline-none focus:ring-2 focus:ring-indigo-400 '
                         'bg-white text-gray-800 placeholder-gray-400',
                'placeholder': 'e.g. Work, Personal, Shopping…',
            }),
        }
```

---

## UPGRADE 3 — Category Tags

Categories are already in the model. This upgrade adds the view and URL so users can create them, and populates the dropdown in the todo form with only the logged-in user's categories.

### 3.1 — Update views.py (everything together)

Open **`todos/views.py`** and replace it entirely:

```python
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo, Category
from .forms import TodoForm, CategoryForm


# ── List ────────────────────────────────────────────
@login_required
def todo_list(request):
    todos = Todo.objects.filter(owner=request.user)

    # ── search ──
    query = request.GET.get('q', '').strip()
    if query:
        todos = todos.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # ── filter by status ──
    status = request.GET.get('status', 'all')
    if status == 'completed':
        todos = todos.filter(completed=True)
    elif status == 'pending':
        todos = todos.filter(completed=False)

    # ── filter by priority ──
    priority = request.GET.get('priority', '')
    if priority in ('low', 'medium', 'high'):
        todos = todos.filter(priority=priority)

    # ── filter by category ──
    cat_id = request.GET.get('category', '')
    if cat_id.isdigit():
        todos = todos.filter(category_id=int(cat_id))

    # ── filter by due-date bucket ──
    due = request.GET.get('due', '')
    if due == 'overdue':
        from django.utils.timezone import now
        todos = todos.filter(due_date__lt=now().date(), completed=False)
    elif due == 'today':
        from django.utils.timezone import now
        todos = todos.filter(due_date=now().date())
    elif due == 'upcoming':
        from django.utils.timezone import now
        from datetime import timedelta
        today = now().date()
        todos = todos.filter(due_date__gte=today, due_date__lte=today + timedelta(days=7))

    completed_count = todos.filter(completed=True).count()
    pending_count   = todos.filter(completed=False).count()
    categories      = Category.objects.filter(owner=request.user)

    from django.utils.timezone import now
    return render(request, 'todos/todo_list.html', {
        'todos':           todos,
        'completed_count': completed_count,
        'pending_count':   pending_count,
        'categories':      categories,
        'query':           query,
        'status':          status,
        'priority':        priority,
        'cat_id':          cat_id,
        'due':             due,
        'today':           now().date(),                                          # used by "Overdue" badge in template
        'status_choices':   [('all','All'), ('pending','Pending'), ('completed','Completed')],
        'priority_choices': [('low','Low'), ('medium','Medium'), ('high','High')],
        'due_choices':      [('overdue','Overdue'), ('today','Today'), ('upcoming','This Week')],
    })


# ── Create ──────────────────────────────────────────
@login_required
def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        # limit category choices to this user
        form.fields['category'].queryset = Category.objects.filter(owner=request.user)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.owner = request.user
            todo.save()
            return redirect('todo_list')
    else:
        form = TodoForm()
        form.fields['category'].queryset = Category.objects.filter(owner=request.user)
    return render(request, 'todos/todo_form.html', {'form': form})


# ── Update ──────────────────────────────────────────
@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        form.fields['category'].queryset = Category.objects.filter(owner=request.user)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
        form.fields['category'].queryset = Category.objects.filter(owner=request.user)
    return render(request, 'todos/todo_form.html', {'form': form})


# ── Delete ──────────────────────────────────────────
@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('todo_list')
    return render(request, 'todos/todo_confirm_delete.html', {'todo': todo})


# ── Toggle ──────────────────────────────────────────
@login_required
def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo_list')


# ── Categories ──────────────────────────────────────
@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.owner = request.user
            cat.save()
            # Return to the page that sent us here (todo form or list)
            next_url = request.GET.get('next', 'todo_list')
            return redirect(next_url)
    else:
        form = CategoryForm()
    return render(request, 'todos/category_form.html', {'form': form})
```

### 3.2 — Update urls.py

Open **`todos/urls.py`** and replace it entirely:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.todo_list,      name='todo_list'),
    path('create/',               views.todo_create,    name='todo_create'),
    path('<int:pk>/update/',      views.todo_update,    name='todo_update'),
    path('<int:pk>/delete/',      views.todo_delete,    name='todo_delete'),
    path('<int:pk>/toggle/',      views.todo_toggle,    name='todo_toggle'),
    path('category/create/',      views.category_create, name='category_create'),
]
```

### 3.3 — Add the category form template

Create **`todos/templates/todos/category_form.html`**:

```html
{% extends 'todos/base.html' %}

{% block content %}
<div class="bg-white rounded-2xl shadow-md border border-gray-100 p-8 max-w-md mx-auto">
  <h2 class="text-xl font-bold text-gray-800 mb-1">🏷️ New Category</h2>
  <p class="text-gray-400 text-sm mb-5">Give it a name and it will appear in your task form.</p>

  {% if request.GET.from_todo %}
    <div class="bg-indigo-50 border border-indigo-200 text-indigo-700 text-sm rounded-xl px-4 py-2 mb-4">
      💡 This window will close automatically after you create the category
    </div>
  {% endif %}

  <form method="post" id="categoryForm">
    {% csrf_token %}
    <label class="block text-sm font-semibold text-gray-600 mb-1">Category Name</label>
    {{ form.name }}
    {% if form.name.errors %}
      <p class="text-red-500 text-xs mt-1">{{ form.name.errors|first }}</p>
    {% endif %}

    <div class="flex gap-3 mt-6">
      <button type="submit"
              class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white
                     font-semibold py-3 rounded-xl shadow transition-all
                     duration-200 hover:shadow-md hover:-translate-y-0.5">
        Create Category
      </button>
      {% if request.GET.from_todo %}
        <button type="button" onclick="window.close()"
                class="px-5 py-3 rounded-xl border border-gray-200 text-gray-600
                       hover:bg-gray-50 font-medium transition-colors duration-200">
          Cancel
        </button>
      {% else %}
        <a href="{% url 'todo_list' %}"
           class="px-5 py-3 rounded-xl border border-gray-200 text-gray-600
                  hover:bg-gray-50 font-medium transition-colors duration-200">
          Cancel
        </a>
      {% endif %}
    </div>
  </form>
</div>

<script>
// If opened from todo form (popup), close after successful creation
{% if request.GET.from_todo %}
document.getElementById('categoryForm').addEventListener('submit', function() {
  // Small delay to allow form submission to complete
  setTimeout(function() {
    window.close();
  }, 800);
});
{% endif %}
</script>
{% endblock %}
```

---

## UPGRADE 4 — Search & Filter (+ full updated templates)

The view already handles every query parameter. This upgrade replaces the list and form templates with the final versions that expose all the UI controls.

### 4.1 — Replace `todo_list.html`

Open **`todos/templates/todos/todo_list.html`** and replace it entirely:

```html
{% extends 'todos/base.html' %}

{% block content %}

<!-- Top Row: New Task + New Category -->
<div class="flex justify-end gap-2 mb-4">
  <a href="{% url 'category_create' %}"
     class="inline-flex items-center gap-1.5 bg-white hover:bg-gray-50
            text-gray-600 font-medium py-2 px-4 rounded-xl shadow-sm
            border border-gray-200 transition-all duration-200
            hover:shadow hover:-translate-y-0.5 text-sm">
    🏷️ New Category
  </a>
  <a href="{% url 'todo_create' %}"
     class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700
            text-white font-semibold py-2 px-5 rounded-xl shadow-md
            transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 text-sm">
    <span class="text-lg leading-none">+</span> New Task
  </a>
</div>

<!-- Search Bar -->
<form method="get" action="{% url 'todo_list' %}" class="mb-3">
  <div class="flex gap-2">
    <input type="text" name="q" value="{{ query }}"
           placeholder="Search tasks…"
           class="flex-1 px-4 py-2.5 rounded-xl border border-gray-200
                  focus:outline-none focus:ring-2 focus:ring-indigo-400
                  bg-white text-gray-800 placeholder-gray-400 text-sm shadow-sm" />
    <!-- preserve active filters while searching -->
    {% if status != 'all' %}<input type="hidden" name="status"   value="{{ status }}" />{% endif %}
    {% if priority %}       <input type="hidden" name="priority" value="{{ priority }}" />{% endif %}
    {% if cat_id %}         <input type="hidden" name="category" value="{{ cat_id }}" />{% endif %}
    {% if due %}            <input type="hidden" name="due"      value="{{ due }}" />{% endif %}
    <button type="submit"
            class="bg-indigo-600 hover:bg-indigo-700 text-white
                   font-semibold px-5 rounded-xl shadow-sm transition-all
                   duration-200 text-sm">
      Search
    </button>
  </div>
</form>

<!-- Filter Pills -->
<div class="flex flex-wrap gap-2 mb-4">

  <!-- Status -->
  <div class="flex bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
    {% for val, label in status_choices %}
      <a href="?status={{ val }}{% if query %}&q={{ query }}{% endif %}{% if priority %}&priority={{ priority }}{% endif %}{% if cat_id %}&category={{ cat_id }}{% endif %}{% if due %}&due={{ due }}{% endif %}"
         class="px-3 py-1.5 text-xs font-semibold transition-colors duration-150
                {% if status == val %} bg-indigo-600 text-white {% else %} text-gray-500 hover:bg-gray-50 {% endif %}">
        {{ label }}
      </a>
    {% endfor %}
  </div>

  <!-- Priority -->
  <div class="flex bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
    <a href="?status={{ status }}{% if query %}&q={{ query }}{% endif %}{% if cat_id %}&category={{ cat_id }}{% endif %}{% if due %}&due={{ due }}{% endif %}"
       class="px-3 py-1.5 text-xs font-semibold transition-colors duration-150
              {% if not priority %} bg-indigo-600 text-white {% else %} text-gray-500 hover:bg-gray-50 {% endif %}">
      All
    </a>
    {% for val, label in priority_choices %}
      <a href="?priority={{ val }}&status={{ status }}{% if query %}&q={{ query }}{% endif %}{% if cat_id %}&category={{ cat_id }}{% endif %}{% if due %}&due={{ due }}{% endif %}"
         class="px-3 py-1.5 text-xs font-semibold transition-colors duration-150
                {% if priority == val %}
                  {% if val == 'high' %} bg-red-500 text-white
                  {% elif val == 'medium' %} bg-amber-500 text-white
                  {% else %} bg-emerald-500 text-white {% endif %}
                {% else %} text-gray-500 hover:bg-gray-50 {% endif %}">
        {{ label }}
      </a>
    {% endfor %}
  </div>

  <!-- Category -->
  {% if categories %}
  <div class="flex bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
    <a href="?status={{ status }}{% if query %}&q={{ query }}{% endif %}{% if priority %}&priority={{ priority }}{% endif %}{% if due %}&due={{ due }}{% endif %}"
       class="px-3 py-1.5 text-xs font-semibold transition-colors duration-150
              {% if not cat_id %} bg-indigo-600 text-white {% else %} text-gray-500 hover:bg-gray-50 {% endif %}">
      All
    </a>
    {% for cat in categories %}
      <a href="?category={{ cat.pk }}&status={{ status }}{% if query %}&q={{ query }}{% endif %}{% if priority %}&priority={{ priority }}{% endif %}{% if due %}&due={{ due }}{% endif %}"
         class="px-3 py-1.5 text-xs font-semibold transition-colors duration-150
                {% if cat_id == cat.pk|stringformat:'s' %} bg-violet-600 text-white {% else %} text-gray-500 hover:bg-gray-50 {% endif %}">
        {{ cat.name }}
      </a>
    {% endfor %}
  </div>
  {% endif %}

  <!-- Due-date bucket -->
  <div class="flex bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
    <a href="?status={{ status }}{% if query %}&q={{ query }}{% endif %}{% if priority %}&priority={{ priority }}{% endif %}{% if cat_id %}&category={{ cat_id }}{% endif %}"
       class="px-3 py-1.5 text-xs font-semibold transition-colors duration-150
              {% if not due %} bg-indigo-600 text-white {% else %} text-gray-500 hover:bg-gray-50 {% endif %}">
      All
    </a>
    {% for val, label in due_choices %}
      <a href="?due={{ val }}&status={{ status }}{% if query %}&q={{ query }}{% endif %}{% if priority %}&priority={{ priority }}{% endif %}{% if cat_id %}&category={{ cat_id }}{% endif %}"
         class="px-3 py-1.5 text-xs font-semibold transition-colors duration-150
                {% if due == val %} bg-indigo-600 text-white {% else %} text-gray-500 hover:bg-gray-50 {% endif %}">
        {{ label }}
      </a>
    {% endfor %}
  </div>

  <!-- Clear-all link (only when any filter or search is active) -->
  {% if query or status != 'all' or priority or cat_id or due %}
    <a href="{% url 'todo_list' %}"
       class="self-center text-xs text-red-400 hover:text-red-600 transition-colors duration-150 ml-1">
      ✕ Clear all
    </a>
  {% endif %}

</div>

<!-- Stats Bar -->
<div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-4">
  <div class="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden mb-3">
    <div class="h-full bg-emerald-400 rounded-full transition-all duration-500"
         style="width: {% if todos|length > 0 %}{% widthratio completed_count todos|length 100 %}{% else %}0{% endif %}%;"></div>
  </div>
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

      <!-- Checkbox -->
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
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        {% endif %}
      </a>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <h3 class="text-base font-semibold text-gray-800
                     {% if todo.completed %} line-through text-gray-400 {% endif %}">
            {{ todo.title }}
          </h3>

          <!-- Priority badge -->
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full
                       {% if todo.priority == 'high' %}    bg-red-100    text-red-600
                       {% elif todo.priority == 'medium' %} bg-amber-100  text-amber-700
                       {% else %}                           bg-emerald-100 text-emerald-700
                       {% endif %}">
            {{ todo.get_priority_display }}
          </span>
        </div>

        {% if todo.description %}
          <p class="text-sm text-gray-500 mt-0.5 truncate">{{ todo.description }}</p>
        {% endif %}

        <!-- Meta row: category tag + due date + created -->
        <div class="flex items-center gap-3 mt-1.5 flex-wrap">
          {% if todo.category %}
            <span class="inline-flex items-center gap-1 text-xs font-medium text-violet-700
                         bg-violet-100 px-2 py-0.5 rounded-full">
              🏷️ {{ todo.category.name }}
            </span>
          {% endif %}

          {% if todo.due_date %}
            <span class="text-xs {% if todo.due_date < today and not todo.completed %} text-red-500 font-semibold {% else %} text-gray-400 {% endif %}">
              📅 Due {{ todo.due_date|date:"M j, Y" }}
              {% if todo.due_date < today and not todo.completed %} — Overdue {% endif %}
            </span>
          {% endif %}

          <span class="text-xs text-gray-400">Added {{ todo.created_at|date:"M j, Y" }}</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <a href="{% url 'todo_update' todo.pk %}"
           class="text-gray-400 hover:text-indigo-500 transition-colors duration-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </a>
        <a href="{% url 'todo_delete' todo.pk %}"
           class="text-gray-400 hover:text-red-500 transition-colors duration-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </a>
      </div>

    </div>
  </div>
  {% endfor %}

{% else %}
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
    <div class="text-6xl mb-4">🎉</div>
    {% if query or status != 'all' or priority or cat_id or due %}
      <p class="text-gray-500 text-lg font-medium">No tasks match your filters.</p>
      <a href="{% url 'todo_list' %}" class="text-indigo-500 hover:underline text-sm mt-1 inline-block">Clear filters</a>
    {% else %}
      <p class="text-gray-500 text-lg font-medium">No tasks yet!</p>
      <p class="text-gray-400 text-sm mt-1">
        <a href="{% url 'todo_create' %}" class="text-indigo-500 hover:underline">Create your first task</a>
      </p>
    {% endif %}
  </div>
{% endif %}

{% endblock %}
```

### 4.2 — Replace `todo_form.html`

Open **`todos/templates/todos/todo_form.html`** and replace it entirely:

```html
{% extends 'todos/base.html' %}

{% block content %}
<div class="bg-white rounded-2xl shadow-md border border-gray-100 p-8">

  <h2 class="text-2xl font-bold text-gray-800 mb-1">
    {% if form.instance.pk %} ✏️ Edit Task {% else %} 📝 New Task {% endif %}
  </h2>
  <p class="text-gray-400 text-sm mb-6">
    {% if form.instance.pk %} Update the details below. {% else %} Fill in the details and hit Save. {% endif %}
  </p>

  <form method="post" id="todoForm">
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

    <!-- Priority + Due Date side by side -->
    <div class="grid grid-cols-2 gap-4 mt-5">
      <div>
        <label class="block text-sm font-semibold text-gray-600 mb-1">Priority</label>
        {{ form.priority }}
      </div>
      <div>
        <label class="block text-sm font-semibold text-gray-600 mb-1">Due Date</label>
        {{ form.due_date }}
      </div>
    </div>

    <!-- Category + create-new link -->
    <div class="mt-5">
      <label class="block text-sm font-semibold text-gray-600 mb-1">
        Category
        <a href="#" id="newCategoryLink" class="font-normal text-indigo-500 hover:underline ml-2">+ New</a>
      </label>
      {{ form.category }}
      <p class="text-xs text-gray-400 mt-1">Click "+ New" to create a category (opens in new tab, your form data will be saved)</p>
    </div>

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

<script>
// Form field IDs
const STORAGE_KEY = 'todoFormData';
const form = document.getElementById('todoForm');
const titleField = form.querySelector('[name="title"]');
const descField = form.querySelector('[name="description"]');
const priorityField = form.querySelector('[name="priority"]');
const dueDateField = form.querySelector('[name="due_date"]');
const categoryField = form.querySelector('[name="category"]');

// Save form data to sessionStorage
function saveFormData() {
  const data = {
    title: titleField.value,
    description: descField.value,
    priority: priorityField.value,
    due_date: dueDateField.value,
    category: categoryField.value
  };
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

// Restore form data from sessionStorage
function restoreFormData() {
  const saved = sessionStorage.getItem(STORAGE_KEY);
  if (saved) {
    const data = JSON.parse(saved);
    titleField.value = data.title || '';
    descField.value = data.description || '';
    priorityField.value = data.priority || '';
    dueDateField.value = data.due_date || '';
    if (data.category) {
      categoryField.value = data.category;
    }
    // Clear the saved data after restoring
    sessionStorage.removeItem(STORAGE_KEY);
  }
}

// On page load, check if we need to restore data
window.addEventListener('load', function() {
  restoreFormData();
});

// When clicking "+ New", save form data and open popup
document.getElementById('newCategoryLink').addEventListener('click', function(e) {
  e.preventDefault();
  saveFormData();
  const url = "{% url 'category_create' %}?from_todo=1";
  window.open(url, '_blank', 'width=500,height=400');
});

// Poll for new categories every second while popup might be open
let pollInterval;
document.getElementById('newCategoryLink').addEventListener('click', function() {
  const originalCount = categoryField.options.length;
  
  pollInterval = setInterval(function() {
    // Fetch the current page to get updated category dropdown
    fetch(window.location.href)
      .then(response => response.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newSelect = doc.querySelector('[name="category"]');
        
        if (newSelect && newSelect.options.length > originalCount) {
          // New category was added - update our dropdown
          const currentValue = categoryField.value;
          categoryField.innerHTML = newSelect.innerHTML;
          
          // Select the newly added category (last option)
          categoryField.value = newSelect.options[newSelect.options.length - 1].value;
          
          // Stop polling
          clearInterval(pollInterval);
        }
      });
  }, 1000);
  
  // Stop polling after 60 seconds
  setTimeout(() => clearInterval(pollInterval), 60000);
});
</script>
{% endblock %}
```

### 4.3 — Update admin.py (register Category too)

Open **`todos/admin.py`** and replace it entirely:

```python
from django.contrib import admin
from .models import Todo, Category

admin.site.register(Todo)
admin.site.register(Category)
```

### 4.4 — Final migration & run

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## How the Filter Pills Work

Every pill is a plain `<a>` tag that builds a query-string URL.  
The view reads each parameter, stacks the filters on the queryset, and passes the active values back so the correct pills stay highlighted.  
The hidden `<input>` fields inside the search `<form>` make sure typing a new search word doesn't reset your active status/priority/category/due filter.

| Query param   | Values                            | What it does                                      |
|---------------|-----------------------------------|---------------------------------------------------|
| `q`           | any text                          | Case-insensitive search on task **title and description** |
| `status`      | `all` · `completed` · `pending`   | Filter by done / not done                         |
| `priority`    | `low` · `medium` · `high`         | Filter by priority level                          |
| `category`    | category PK (integer)             | Filter to one category                            |
| `due`         | `overdue` · `today` · `upcoming`  | Filter by due-date bucket                         |

All filters combine. Example URL: `/?q=report&status=pending&priority=high&due=today`

---

## Updated URL Map

| Page                         | URL                                    |
|------------------------------|----------------------------------------|
| Login                        | `/login/`                              |
| Logout                       | `/logout/`                             |
| Task list (+ search/filter)  | `/`                                    |
| Create task                  | `/create/`                             |
| Edit task #3                 | `/3/update/`                           |
| Delete task #3               | `/3/delete/`                           |
| Toggle task #3               | `/3/toggle/`                           |
| Create category              | `/category/create/`                    |
| Django admin                 | `/admin/`                              |

---

## Common Errors & Fixes (Upgraded)

| Error                                              | Fix                                                                                          |
|----------------------------------------------------|----------------------------------------------------------------------------------------------|
| `IntegrityError: NOT NULL constraint failed: owner`| You forgot the one-off default during `makemigrations` — delete `db.sqlite3`, re-run migrations |
| Login page shows but login fails                   | Make sure you ran `createsuperuser` and are using those exact credentials                    |
| Category dropdown is empty                         | You haven't created any categories yet — click **+ New** on the task form                    |
| Filters reset when you search                      | The hidden inputs in the search `<form>` carry active filters — check they are present       |
| `TemplateDoesNotExist: todos/login.html`           | File must live at `todos/templates/todos/login.html`                                         |
| Due-date "Overdue" label never appears             | Make sure `today` is passed from the view context (already done in the view above)           |

---

## 🐛 Bug Fixes (Applied in This Guide)

This guide includes fixes for three common issues users reported:

### Issue #1: Logout returns HTTP 405 error

**Problem:** Clicking "Logout" shows "Method Not Allowed" error because Django's logout view requires POST for security.

**Fix Applied:**
- Changed `urls.py` to add `http_method_names=['post']` to LogoutView
- Updated `base.html` to use a `<form>` with POST instead of a regular link
- The logout button now submits a form instead of navigating to a URL

### Issue #2: Creating a category loses todo form data

**Problem:** Clicking "+ New" on the todo form navigates to the category creation page, and all entered data (title, description, etc.) is lost when you come back.

**Fix Applied:**
- Saves all form data to browser sessionStorage before opening the category popup
- When you return to the todo form (after creating the category), the saved data is automatically restored
- Polls the server every second to detect when a new category is added and updates the dropdown
- Auto-selects the newly created category for you
- The popup window closes automatically after you create the category

**How it works:**
1. You fill out the todo form partially
2. Click "+ New" to create a category
3. JavaScript saves your form data (title, description, priority, due date) to sessionStorage
4. Popup opens with the category creation form
5. You create the category and the popup closes
6. The main form detects the new category and adds it to the dropdown
7. Your original form data is automatically restored from sessionStorage

### Issue #3: Search only works on title, not description

**Problem:** Typing text in the search bar only finds tasks where the title contains that text — it ignores the description field entirely.

**Fix Applied:**
- Updated the `todo_list` view to use Django's `Q` objects for OR logic
- Search now matches against **both** `title` and `description` fields
- Example: searching "meeting" will find tasks with "meeting" in the title OR description
