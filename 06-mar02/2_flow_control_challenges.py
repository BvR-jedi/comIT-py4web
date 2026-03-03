# ============================================================
# Python Flow Control — 10 Beginner Challenges
# Practice each one before reading the hint!
# Hints are at the bottom of the file.
# ============================================================


# --------------------------------------------------------------
# Challenge 1 — Ticket Price
# Write an if-elif-else chain that prints the ticket price
# based on the visitor's age:
#   Under 5    → Free
#   5 to 17    → $8
#   18 to 64   → $15
#   65+        → $10
# Test with at least three different ages.
# Concept: if-elif-else
# --------------------------------------------------------------

age = 34
# your code here


# --------------------------------------------------------------
# Challenge 2 — Login Gate
# Using nested conditionals, check two things in order:
# 1. Is the user logged in?
# 2. If yes, do they have admin rights?
# Print a different message for each combination:
# not logged in / logged in as user / logged in as admin.
# Concept: nested if-else
# --------------------------------------------------------------

logged_in = True
is_admin  = False
# your code here


# --------------------------------------------------------------
# Challenge 3 — FizzBuzz
# Loop through numbers 1 to 30. For each number print:
#   "FizzBuzz" if divisible by both 3 and 5
#   "Fizz"     if divisible by 3 only
#   "Buzz"     if divisible by 5 only
#   The number itself otherwise
# Concept: for loop + if-elif-else
# --------------------------------------------------------------

# your code here


# --------------------------------------------------------------
# Challenge 4 — Find the First Negative
# Iterate over the list and print the FIRST negative number
# found, then stop the loop immediately.
# If no negative number exists, print "All positive!".
# Concept: for loop + break + else clause
# --------------------------------------------------------------

numbers = [4, 7, 2, -3, 8, -1, 5]
# your code here


# --------------------------------------------------------------
# Challenge 5 — Skip the Vowels
# Loop over the string below and print only the consonants,
# one character per line. Skip spaces and vowels silently.
# Concept: for loop + continue
# --------------------------------------------------------------

phrase = "flow control"
vowels = "aeiou"
# your code here


# --------------------------------------------------------------
# Challenge 6 — Guess the Number (while loop)
# Simulate a number guessing game. Start with guess = 0 and
# keep incrementing by 13 each iteration until you hit or
# exceed the secret number. Print each guess and how many
# attempts it took.
# Concept: while loop
# --------------------------------------------------------------

secret  = 91
guess   = 0
attempts = 0
# your code here


# --------------------------------------------------------------
# Challenge 7 — Safe Division (try-except-else-finally)
# Write a function called safe_divide(a, b) that:
#   - Returns the result of a / b
#   - Catches ZeroDivisionError and prints a friendly message
#   - Uses else to print "Success!" when no error occurs
#   - Uses finally to always print "Operation complete."
# Test it with (10, 2) and (5, 0).
# Concept: try / except / else / finally
# --------------------------------------------------------------

def safe_divide(a, b):
    pass  # your code here

safe_divide(10, 2)
safe_divide(5, 0)


# --------------------------------------------------------------
# Challenge 8 — Command Router (match-case)
# Write a match-case block that handles these commands:
#   "start"          → print "Server starting..."
#   "stop" or "quit" → print "Server shutting down..."
#   "status"         → print "Server is running."
#   anything else    → print "Unknown command: <command>"
# Test with at least four different commands.
# Concept: match-case (Python 3.10+)
# --------------------------------------------------------------

commands = ["start", "status", "restart", "quit"]
for command in commands:
    pass  # your code here


# --------------------------------------------------------------
# Challenge 9 — Comprehension Makeover
# Rewrite the code below (which uses a loop and append)
# as a single list comprehension, then do the same using
# a dict comprehension for the second block.
# Concept: list & dict comprehensions
# --------------------------------------------------------------

# Block A — rewrite as a list comprehension
result = []
for n in range(1, 11):
    if n % 2 != 0:
        result.append(n ** 2)

# your list comprehension here

# Block B — rewrite as a dict comprehension
word_map = {}
for word in ["apple", "banana", "cherry"]:
    if len(word) > 5:
        word_map[word] = len(word)

# your dict comprehension here


# --------------------------------------------------------------
# Challenge 10 — Walrus & Short-Circuit
# Part A — Walrus operator:
# Loop over the strings list. For each item, use the walrus
# operator to check if its length is greater than 5 AND assign
# that length at the same time. Print only the long words and
# their lengths.
#
# Part B — Short-circuit default:
# You have three variables that may be empty. Use `or` chaining
# to assign the first truthy value to `display_name`.
# Concept: walrus operator :=, short-circuit evaluation
# --------------------------------------------------------------

# Part A
strings = ["hi", "python", "ok", "programming", "AI", "flow"]
# your code here

# Part B
nickname  = ""
username  = ""
full_name = "Alice Johnson"
# your code here — assign display_name using `or` chaining
# then print display_name


# ============================================================
# BONUS TIPS
# - Order matters in if-elif chains — put the most specific
#   conditions first (e.g. check divisibility by 15 before 3 or 5).
# - The else clause on a for/while loop only runs when no break
#   was hit — a subtle but powerful pattern.
# - Use try-except for EXPECTED errors, not as general flow control.
# - match-case requires Python 3.10+; check your version first.
# - Comprehensions are great for simple transforms; use loops
#   when logic becomes complex or multi-line.
# ============================================================


# ============================================================
# HINTS — try to solve each challenge before reading these!
# ============================================================

# Challenge 1:  Chain elif branches from most restrictive to least; the final else catches 65+.

# Challenge 2:  Place the is_admin check INSIDE the if logged_in block as a nested if-else.

# Challenge 3:  Check divisibility by 15 (FizzBuzz) FIRST, before checking 3 or 5 separately.

# Challenge 4:  Use break to exit early; the for-else clause runs only when no break fired.

# Challenge 5:  Use continue inside the loop to skip vowels and spaces without an else branch.

# Challenge 6:  Increment guess and attempts inside the while body; loop condition is guess < secret.

# Challenge 7:  Structure: try → division, except ZeroDivisionError → message, else → success, finally → always.

# Challenge 8:  Use case "stop" | "quit": for the OR pattern; case _: for the wildcard catch-all.

# Challenge 9:  List comprehension: [expr for x in iterable if condition]. Dict: {k: v for ...}.

# Challenge 10: Part A — if (n := len(s)) > 5. Part B — display_name = nickname or username or full_name.
