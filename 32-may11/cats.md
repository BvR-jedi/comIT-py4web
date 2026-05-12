Creating a basic REST API with Django and Django REST Framework (DRF) is straightforward. Here are the step-by-step instructions to build a "Cats" API.

1. Prerequisites
Ensure you have Python installed. It is recommended to use a virtual environment.

```Bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install Django and Django REST Framework
pip install django djangorestframework
```

2. Create the Project and App

```Bash
# Create a new Django project named 'cat_project'
django-admin startproject cat_project .

# Create a new app named 'cats'
python manage.py startapp cats
```

3. Configure settings.py
Add rest_framework and your new app cats to the INSTALLED_APPS list in cat_project/settings.py.

```Python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'cats',
]
```

4. Define the Model
   
In cats/models.py, define the structure of your Cat data.

```Python
from django.db import models

class Cat(models.Model):
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=100)  # e.g., Persian, Siamese
    age = models.IntegerField()
    weight = models.FloatField()
    vaccinated = models.BooleanField(default=False)

    def __str__(self):
        return self.name

```


5. Create a Serializer

Create a new file cats/serializers.py. Serializers convert model instances to JSON.

```Python
from rest_framework import serializers
from .models import Cat

class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = '__all__'

```

6. Create the Views
In cats/views.py, use a ModelViewSet which provides default GET, POST, PUT, and DELETE actions.

```Python
from rest_framework import viewsets
from .models import Cat
from .serializers import CatSerializer

class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_with = CatSerializer
    serializer_class = CatSerializer

```

7. Configure URLs


First, create cats/urls.py:

```Python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatViewSet

router = DefaultRouter()
router.register(r'cats', CatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

```

Then, include these URLs in the main cat_project/urls.py:

```Python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.id),
    path('api/', include('cats.urls')),
]
```


1. Run Migrations and Start the Server

```Bash
# Create the database schema
python manage.py makemigrations
python manage.py migrate

# Start the development server
python manage.py runserver

```

9. Test the API

You can now access your API at http://127.0.0.1:8000/api/cats/.
GET: List all cats.
POST: Create a new cat (using JSON).
