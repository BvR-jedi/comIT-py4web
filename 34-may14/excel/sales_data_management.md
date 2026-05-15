This guide provides instructions to build a Django application that fulfills your requirements. We will use `pandas` and `openpyxl` to handle the Excel processing, and standard Django Generic Class-Based Views (GCBVs) for the logic.

### Prerequisites
You will need to install `pandas` and `openpyxl` to handle the `.xlsx` file:
```bash
pip install django pandas openpyxl
```

---

### Step 1: Define the Models
We need a model to store the sales data and a secondary model to store "Custom Column Names" so you can rename headers dynamically without migrating the database.

**`models.py`**
```python
from django.db import models
from django.urls import reverse

class Sale(models.Model):
    timestamp = models.DateTimeField()
    product = models.CharField(max_length=255)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    referer = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    email = models.EmailField()

    def get_absolute_url(self):
        return reverse('sale-list')

class ColumnLabel(models.Model):
    internal_name = models.CharField(max_length=50, unique=True) # e.g., 'product'
    display_name = models.CharField(max_length=50) # e.g., 'Item Name'

    def __str__(self):
        return f"{self.internal_name} -> {self.display_name}"
```

---

### Step 2: The Upload Form
**`forms.py`**
```python
from django import超forms
from .models import ColumnLabel

class UploadFileForm(forms.Form):
    file = forms.FileField()

class ColumnRenameForm(forms.ModelForm):
    class Meta:
        model = ColumnLabel
        fields = ['display_name']
```

---

### Step 3: The Views (Generic Class-Based Views)
We will use `ListView` for display/search/summary, `UpdateView` for editing rows, and a `FormView` for the upload logic.

**`views.py`**
```python
import pandas as pd
from django.views.generic import ListView, UpdateView, FormView, View
from django.db.models import Sum, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Sale, ColumnLabel
from .forms import UploadFileForm

class SaleListView(ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(product__icontains=search_query) | 
                Q(customer_name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Summary Calculation: Group by Year and Month
        context['summary'] = Sale.objects.annotate(
            year=ExtractYear('timestamp'),
            month=ExtractMonth('timestamp')
        ).values('year', 'month').annotate(
            total_revenue=Sum('revenue'),
            count=models.Count('id')
        ).order_by('-year', '-month')

        # Get Column Labels
        labels = ColumnLabel.objects.all()
        context['labels'] = {l.internal_name: l.display_name for l in labels}
        return context

class SaleUpdateView(UpdateView):
    model = Sale
    fields = '__all__'
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sale-list')

class UploadView(FormView):
    template_name = 'sales/upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('sale-list')

    def form_valid(self, form):
        file = self.request.FILES['file']
        df = pd.read_excel(file)
        
        # Clean Revenue string (€34.99 -> 34.99)
        if df['Revenue'].dtype == 'O':
            df['Revenue'] = df['Revenue'].replace('[€,]', '', regex=True).astype(float)

        sales_instances = []
        for _, row in df.iterrows():
            sales_instances.append(Sale(
                timestamp=row['Timestamp'],
                product=row['Product'],
                revenue=row['Revenue'],
                referer=row['Referer'],
                customer_name=row['Customer name'],
                country=row['Country'],
                email=row['Email']
            ))
        Sale.objects.bulk_create(sales_instances)
        
        # Initialize default labels if they don't exist
        columns = ['timestamp', 'product', 'revenue', 'referer', 'customer_name', 'country', 'email']
        for col in columns:
            ColumnLabel.objects.get_or_create(internal_name=col, defaults={'display_name': col.replace('_', ' ').title()})
            
        return super().form_valid(form)

class RenameColumnView(UpdateView):
    model = ColumnLabel
    fields = ['display_name']
    template_name = 'sales/rename_column.html'
    success_url = reverse_lazy('sale-list')
    
    def get_object(self):
        return ColumnLabel.objects.get(internal_name=self.kwargs['internal_name'])
```

---

### Step 4: URL Configuration
**`urls.py`**
```python
from django.urls import path
from .views import SaleListView, SaleUpdateView, UploadView, RenameColumnView

urlpatterns = [
    path('', UploadView.as_view(), name='upload'),
    path('list/', SaleListView.as_view(), name='sale-list'),
    path('edit/<int:pk>/', SaleUpdateView.as_view(), name='sale-edit'),
    path('rename/<str:internal_name>/', RenameColumnView.as_view(), name='rename-column'),
]
```

---

### Step 5: Templates (No CSS)
Create a folder `templates/sales/`.

**`upload.html`**
```html
<h1>Upload Sales Excel File</h1>
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Upload and Process</button>
</form>
```

**`sale_list.html`**
```html
<h1>Sales Data</h1>

<!-- Search -->
<form method="get">
    <input type="text" name="q" placeholder="Search product or customer...">
    <button type="submit">Search</button>
</form>

<hr>

<!-- Summary Table -->
<h2>Monthly Summary</h2>
<table border="1">
    <thead>
        <tr><th>Year</th><th>Month</th><th>Total Revenue</th><th>Total Sales</th></tr>
    </thead>
    <tbody>
        {% for item in summary %}
        <tr>
            <td>{{ item.year }}</td>
            <td>{{ item.month }}</td>
            <td>€{{ item.total_revenue|floatformat:2 }}</td>
            <td>{{ item.count }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<hr>

<!-- Data Table -->
<h2>All Records</h2>
<table border="1">
    <thead>
        <tr>
            <th><a href="{% url 'rename-column' 'timestamp' %}">{{ labels.timestamp }}</a></th>
            <th><a href="{% url 'rename-column' 'product' %}">{{ labels.product }}</a></th>
            <th><a href="{% url 'rename-column' 'revenue' %}">{{ labels.revenue }}</a></th>
            <th><a href="{% url 'rename-column' 'customer_name' %}">{{ labels.customer_name }}</a></th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for sale in sales %}
        <tr>
            <td>{{ sale.timestamp }}</td>
            <td>{{ sale.product }}</td>
            <td>€{{ sale.revenue }}</td>
            <td>{{ sale.customer_name }}</td>
            <td><a href="{% url 'sale-edit' sale.pk %}">Edit</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**`sale_form.html`**
```html
<h1>Edit Sale</h1>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save Changes</button>
</form>
<a href="{% url 'sale-list' %}">Cancel</a>
```

**`rename_column.html`**
```html
<h1>Rename Column: {{ object.internal_name }}</h1>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Update Name</button>
</form>
```

---

### How it works:
1.  **Landing Page:** Use the root URL to upload an `.xlsx` file. Pandas reads the file, cleans the Euro symbol from the revenue, and saves it to SQLite.
2.  **Generic Views:**
    *   `ListView` handles the data display and basic search using `Q` objects.
    *   `UpdateView` handles row editing.
3.  **Calculations:** The `get_context_data` in the `ListView` uses Django's `Sum` and `ExtractMonth` functions to create a monthly summary table on the fly.
4.  **Column Modifying:** Instead of changing database schema (which is risky), we map internal field names (like `product`) to a `ColumnLabel` model. Clicking the header in the table allows you to rename it.
5.  **Styling:** No CSS files or `<style>` blocks are used; only standard HTML tags and attributes like `border="1"`.