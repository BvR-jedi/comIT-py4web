# ============================================================
# Python List Methods - Overview & Common Variations
# ============================================================

nums = [3, 1, 4, 1, 5, 9, 2, 6]
fruits = ["banana", "apple", "cherry"]

# ------ Adding Elements ------

fruits.append("mango")          # Add single item to the end
fruits.insert(1, "grape")       # Insert at specific index
fruits.extend(["kiwi", "lime"]) # Add multiple items from iterable

# ------ Removing Elements ------

fruits.remove("grape")          # Remove first occurrence by value (raises ValueError if missing)
popped = fruits.pop()           # Remove & return last item
popped_at = fruits.pop(0)       # Remove & return item at index
fruits.clear()                  # Remove all items

# ------ Searching & Info ------

nums = [3, 1, 4, 1, 5, 9, 2, 6]

idx = nums.index(1)             # Index of first occurrence (raises ValueError if missing)
idx_range = nums.index(1, 2)    # Search starting from index 2
count = nums.count(1)           # Count occurrences of a value
length = len(nums)              # Number of items (built-in, not a method)

# ------ Ordering ------

# sort() — in-place, modifies the original list
nums.sort()                             # Ascending (default)
nums.sort(reverse=True)                 # Descending
words = ["Banana", "apple", "Cherry"]
words.sort(key=str.lower)               # Case-insensitive sort
words.sort(key=len)                     # Sort by string length
words.sort(key=len, reverse=True)       # Sort by length, longest first

# sorted() — returns a NEW sorted list, original unchanged
people = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
by_age = sorted(people, key=lambda p: p["age"])          # Sort dicts by field
by_name = sorted(people, key=lambda p: p["name"])

nums.reverse()                          # Reverse in-place
reversed_view = list(reversed(nums))    # Returns iterator; convert to list

# ------ Copying ------

shallow = nums.copy()           # Shallow copy (same as nums[:])
import copy
deep = copy.deepcopy(people)    # Deep copy (needed for nested objects)

# ------ Other ------

nums2 = [10, 20]
combined = nums + nums2         # Concatenate into new list
nums2 *= 3                      # Repeat list in-place: [10, 20, 10, 20, 10, 20]

a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)                   # True — compares by value
print(a is b)                   # False — different objects in memory
