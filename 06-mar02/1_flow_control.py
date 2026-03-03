# ============================================================
# Python Flow Control — Complete Overview
# ============================================================


# ============================================================
# 1. IF STATEMENT
# ============================================================

age = 20

if age >= 18:
    print("Adult")              # Runs only when condition is True


# ============================================================
# 2. IF-ELSE STATEMENT
# ============================================================

temperature = 15

if temperature >= 20:
    print("Wear a t-shirt")
else:
    print("Grab a jacket")      # Runs when condition is False


# ============================================================
# 3. IF-ELIF-ELSE STATEMENT
# ============================================================

score = 74

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"                 # Catch-all when no condition matched

print(grade)                    # "C"


# ============================================================
# 4. NESTED CONDITIONALS
# ============================================================

logged_in = True
is_admin  = False

if logged_in:
    if is_admin:
        print("Welcome to the admin panel")
    else:
        print("Welcome, regular user")
else:
    print("Please log in first")

# Tip: deeply nested conditionals hurt readability.
# Prefer combining conditions with logical operators when possible.

if logged_in and is_admin:
    print("Admin access granted")


# ============================================================
# 5. LOGICAL OPERATORS IN CONDITIONS
# ============================================================

x = 15

if x > 0 and x < 20:           # Both must be True
    print("x is between 0 and 20")

if x < 0 or x > 10:            # At least one must be True
    print("x is negative or greater than 10")

if not (x == 0):                # Inverts the boolean result
    print("x is not zero")

# Chained comparisons — Pythonic and readable
if 0 < x < 20:                  # Equivalent to x > 0 and x < 20
    print("x is between 0 and 20 (chained)")


# ============================================================
# 6. TERNARY (CONDITIONAL EXPRESSION)
# One-liner if-else for simple assignments
# ============================================================

age = 17
status = "adult" if age >= 18 else "minor"  # value_if_true if condition else value_if_false
print(status)                               # "minor"

# Can be nested (use sparingly — hurts readability)
label = "high" if x > 100 else ("medium" if x > 50 else "low")


# ============================================================
# 7. MATCH-CASE (Python 3.10+) — Structural Pattern Matching
# Python's answer to switch/case statements
# ============================================================

command = "quit"

match command:
    case "start":
        print("Starting...")
    case "stop" | "quit":       # OR pattern — matches either value
        print("Stopping...")
    case "help":
        print("Showing help...")
    case _:                     # Wildcard — catch-all, like else
        print(f"Unknown command: {command}")

# Match with conditions (guards)
point = (0, 5)

match point:
    case (0, 0):
        print("Origin")
    case (x, 0):
        print(f"On x-axis at {x}")
    case (0, y):
        print(f"On y-axis at {y}")         # matches (0, 5)
    case (x, y):
        print(f"Point at ({x}, {y})")

# Match against a class structure
from dataclasses import dataclass

@dataclass
class Shape:
    kind: str
    sides: int

s = Shape("polygon", 6)

match s:
    case Shape(kind="circle", sides=0):
        print("Circle")
    case Shape(kind=k, sides=n) if n > 4:
        print(f"{k} with {n} sides — guard condition used")
    case _:
        print("Other shape")


# ============================================================
# 8. FOR LOOP
# ============================================================

fruits = ["apple", "banana", "cherry"]

for fruit in fruits:            # Iterate over any iterable
    print(fruit)

for i in range(5):              # range(stop): 0,1,2,3,4
    print(i)

for i in range(2, 10, 2):      # range(start, stop, step): 2,4,6,8
    print(i)

for i, fruit in enumerate(fruits, start=1):  # index + value
    print(f"{i}. {fruit}")

for k, v in {"a": 1, "b": 2}.items():       # dict iteration
    print(f"{k} → {v}")

# zip() — iterate two iterables in parallel
names  = ["Alice", "Bob", "Charlie"]
scores = [90, 85, 92]
for name, score in zip(names, scores):
    print(f"{name}: {score}")


# ============================================================
# 9. WHILE LOOP
# ============================================================

count = 0
while count < 5:
    print(count)
    count += 1                  # Always update the condition to avoid infinite loops

# While with user-like input simulation
attempts = 0
password = "secret"
entry    = "wrong"

while entry != password and attempts < 3:
    attempts += 1
    entry = "secret" if attempts == 3 else "wrong"  # simulating input
print("Access granted" if entry == password else "Locked out")

# Infinite loop with break
while True:
    data = "ready"              # simulate data arriving
    if data == "ready":
        print("Processing...")
        break                   # Exit the loop


# ============================================================
# 10. LOOP CONTROL — break, continue, pass
# ============================================================

# break — exit the loop immediately
for n in range(10):
    if n == 5:
        break                   # Stops at 5; 5 is never printed
    print(n)

# continue — skip the rest of this iteration and go to the next
for n in range(10):
    if n % 2 == 0:
        continue                # Skip even numbers
    print(n)                    # Prints odd numbers only

# pass — syntactic placeholder; does nothing
for n in range(5):
    if n == 3:
        pass                    # TODO: handle this case later
    print(n)                    # All numbers still print

# else clause on loops — runs when loop completes WITHOUT a break
for n in range(5):
    if n == 10:                 # Never true
        break
else:
    print("Loop finished without break")   # This runs

for n in range(5):
    if n == 3:
        break
else:
    print("This will NOT print")           # Skipped because break fired


# ============================================================
# 11. EXCEPTION HANDLING — try / except / else / finally
# ============================================================

# Basic try-except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")

# Catch multiple exception types
try:
    value = int("abc")
except (ValueError, TypeError) as e:
    print(f"Conversion error: {e}")

# else — runs only when NO exception was raised
try:
    num = int("42")
except ValueError:
    print("Bad input")
else:
    print(f"Parsed successfully: {num}")   # Runs here

# finally — ALWAYS runs, exception or not (great for cleanup)
try:
    f = open("nonexistent.txt")
except FileNotFoundError:
    print("File not found")
finally:
    print("Cleanup complete")              # Always executes

# Catch all exceptions (use sparingly)
try:
    risky = 1 / 0
except Exception as e:
    print(f"Unexpected error: {type(e).__name__} — {e}")

# Re-raise an exception after handling it
def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print("Config missing — using defaults")
        raise                               # Re-raises the same exception

# Raise custom exceptions
class InsufficientFundsError(Exception):
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(f"Cannot withdraw {amount}, balance is {balance}")
    return balance - amount

try:
    withdraw(100, 200)
except InsufficientFundsError as e:
    print(e)


# ============================================================
# 12. CONTEXT MANAGERS — with statement
# Automatically handles setup and teardown (open/close, lock/unlock)
# ============================================================

# File handling — file closes automatically even if an error occurs
with open("/dev/null", "w") as f:
    f.write("hello")            # f.close() called automatically after block

# Multiple context managers in one line (Python 3.10+ preferred style)
with open("/dev/null") as src, open("/dev/null", "w") as dst:
    dst.write(src.read())


# ============================================================
# 13. COMPREHENSIONS — concise flow over iterables
# ============================================================

# List comprehension
squares   = [x**2 for x in range(10)]
evens     = [x for x in range(20) if x % 2 == 0]          # with filter
converted = [x**2 if x % 2 == 0 else x for x in range(6)] # with conditional

# Dict comprehension
word_lengths = {word: len(word) for word in ["apple", "kiwi", "banana"]}

# Set comprehension
unique_lengths = {len(word) for word in ["apple", "kiwi", "banana"]}

# Generator expression — lazy, memory-efficient (no brackets)
total = sum(x**2 for x in range(1000))    # Computes without building a list


# ============================================================
# 14. SHORT-CIRCUIT EVALUATION & TRUTHINESS
# ============================================================

# Python evaluates and/or lazily — stops as soon as the result is known
print(0 or "default")           # "default" — 0 is falsy, returns last evaluated value
print(1 and "yes")              # "yes"     — 1 is truthy, returns last evaluated value
print(None or [] or "fallback") # "fallback" — first truthy value wins with or

# Falsy values in Python
falsy_values = [False, None, 0, 0.0, "", [], {}, set(), ()]

# Common pattern: provide a default when a value may be falsy
name = ""
display = name or "Anonymous"   # "Anonymous"

# Walrus operator := (Python 3.8+) — assign AND test in one expression
import re
text = "Order number: 12345"
if m := re.search(r"\d+", text):   # assigns match AND checks truthiness
    print(f"Found number: {m.group()}")

# Also useful in while loops to avoid reading data twice
data_stream = iter([10, 20, 0, 30])
while chunk := next(data_stream, None):  # stops when chunk is falsy (0 or None)
    print(chunk)                          # prints 10, 20 — stops at 0
