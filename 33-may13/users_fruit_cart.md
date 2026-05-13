Here are the step-by-step instructions for creating users and assigning them to the **admins** and **customers** groups using the Django shell.

### Step 1: Open the Django Shell
First, make sure your virtual environment is activated, then run the following command in your terminal at the root of your project (where `manage.py` is located):

```bash
python manage.py shell
```

### Step 2: Import the Models
Once inside the interactive Python shell, import the `User` and `Group` models:

```python
from django.contrib.auth.models import User, Group
```

### Step 3: Ensure the Groups Exist
Before adding users to groups, make sure the groups actually exist in your database. Using `get_or_create` is the safest way to do this:

```python
admin_group, _ = Group.objects.get_or_create(name="admins")
customer_group, _ = Group.objects.get_or_create(name="customers")
```

---

### Example 1: Creating a brand new Admin user
When creating users, you must use `create_user()` so that Django properly hashes the password. If you don't do this, the JWT login will fail.

```python
# 1. Create the user
admin_user = User.objects.create_user(username="admin_alice", password="securepassword123")

# 2. Add them to the admins group
admin_user.groups.add(admin_group)

print(f"User {admin_user.username} is now an admin!")
```

### Example 2: Creating a brand new Customer user

```python
# 1. Create the user
customer_user = User.objects.create_user(username="customer_bob", password="securepassword123")

# 2. Add them to the customers group
customer_user.groups.add(customer_group)

print(f"User {customer_user.username} is now a customer!")
```

### Example 3: Adding an existing user to a group
If you already created a user (for example, using `python manage.py createsuperuser` or through the API) and you want to assign them to a group:

```python
# 1. Fetch the existing user by their username
existing_user = User.objects.get(username="charlie")

# 2. Add them to the desired group (e.g., customers)
existing_user.groups.add(customer_group)

print(f"Existing user {existing_user.username} added to customers!")
```

### Example 4: Checking a user's groups (Troubleshooting)
If you want to verify that a user was correctly added to a group, you can check it like this:

```python
user_to_check = User.objects.get(username="admin_alice")

# This will print a list of group names the user belongs to
print(list(user_to_check.groups.values_list('name', flat=True)))
# Output should be: ['admins']
```

### Step 4: Exit the Shell
When you are done, simply type:
```python
exit()
```
*(or press `Ctrl + D` on Mac/Linux, `Ctrl + Z` then `Enter` on Windows).*

Now you can run the `fruit_cart_client.py` script and log in with these exact credentials!