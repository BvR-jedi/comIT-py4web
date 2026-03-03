# ============================================================
# Python String Methods — Complete Overview
# Strings are IMMUTABLE — every method returns a NEW string.
# ============================================================

s = "  Hello, World!  "

# ============================================================
# 1. CASE CONVERSION
# ============================================================

print("hello".upper())              # "HELLO"
print("HELLO".lower())              # "hello"
print("hello world".capitalize())   # "Hello world" — only first char
print("hello world".title())        # "Hello World" — each word capitalised
print("Hello World".swapcase())     # "hELLO wORLD"

# Case-insensitive comparison
print("Python".casefold())          # "python" — more aggressive than lower()
print("straße".casefold())          # "strasse" — handles Unicode edge cases
print("Python".lower() == "PYTHON".lower())     # True — safe comparison


# ============================================================
# 2. WHITESPACE & STRIPPING
# ============================================================

s = "  hello world  "

print(s.strip())                    # "hello world"  — both ends
print(s.lstrip())                   # "hello world  " — left only
print(s.rstrip())                   # "  hello world" — right only
print("xxhelloxx".strip("x"))       # "hello" — strip specific chars
print("...hello...".strip("."))     # "hello"


# ============================================================
# 3. SEARCHING & CHECKING POSITION
# ============================================================

s = "the cat sat on the mat"

print(s.find("cat"))                # 4  — index of first match, -1 if missing
print(s.find("dog"))                # -1 — no error if missing
print(s.rfind("at"))                # 20 — search from the right
print(s.index("cat"))               # 4  — like find() but raises ValueError if missing
print(s.rindex("at"))               # 20 — rightmost, raises ValueError if missing

print(s.count("at"))                # 3  — count non-overlapping occurrences
print(s.count("at", 5))            # 2  — count starting from index 5
print(s.count("at", 5, 15))        # 1  — count within slice [5:15]


# ============================================================
# 4. STARTS / ENDS WITH
# ============================================================

filename = "report_2025.pdf"

print(filename.startswith("report"))            # True
print(filename.endswith(".pdf"))                # True
print(filename.endswith((".pdf", ".docx")))     # True — accepts a tuple of suffixes
print(filename.startswith(("report", "draft"))) # True — accepts a tuple of prefixes
print(filename.startswith("report", 0, 6))      # True — check within a slice


# ============================================================
# 5. REPLACING & TRANSLATING
# ============================================================

s = "banana"

print(s.replace("a", "o"))         # "bonono" — replace all
print(s.replace("a", "o", 2))      # "bonona" — replace at most 2 occurrences

# translate() with str.maketrans() — bulk character-level replacement
table = str.maketrans("aeiou", "12345")
print("hello world".translate(table))  # "h2ll4 w4rld"

# Delete characters using translate
del_table = str.maketrans("", "", "aeiou")  # third arg = chars to delete
print("hello world".translate(del_table))   # "hll wrld"

# Replace using a mapping (e.g. encode special chars)
mapping = str.maketrans({"<": "&lt;", ">": "&gt;", "&": "&amp;"})
print("<b>Hello & World</b>".translate(mapping))


# ============================================================
# 6. SPLITTING & JOINING
# ============================================================

csv = "alice,bob,charlie,diana"

parts = csv.split(",")              # ["alice", "bob", "charlie", "diana"]
print(parts)

text = "one two   three"
print(text.split())                 # ["one", "two", "three"] — splits on any whitespace
print(text.split(" ", 2))          # ["one", "two", "  three"] — max 2 splits

print(csv.rsplit(",", 1))          # ["alice,bob,charlie", "diana"] — split from right

# splitlines() — split on any line ending (\n, \r\n, \r)
multiline = "line one\nline two\r\nline three"
print(multiline.splitlines())       # ["line one", "line two", "line three"]
print(multiline.splitlines(True))   # keepends=True — keeps the line endings

# join() — the reverse of split(); always called on the separator
words = ["one", "two", "three"]
print(", ".join(words))             # "one, two, three"
print(" | ".join(words))            # "one | two | three"
print("".join(["a", "b", "c"]))     # "abc" — no separator
print("\n".join(words))             # each word on its own line

# Efficient string building — join is far faster than += in a loop
tokens = ["Hello", "World", "from", "Python"]
sentence = " ".join(tokens)


# ============================================================
# 7. ALIGNMENT & PADDING
# ============================================================

s = "hello"

print(s.center(15))                 # "     hello     "
print(s.center(15, "-"))            # "-----hello-----"
print(s.ljust(15))                  # "hello          "
print(s.ljust(15, "."))             # "hello.........."
print(s.rjust(15))                  # "          hello"
print(s.rjust(15, "0"))             # "0000000000hello"
print("42".zfill(6))                # "000042" — zero-pad numbers
print("-42".zfill(6))               # "-00042" — handles sign correctly


# ============================================================
# 8. CHECKING CONTENT — is* METHODS
# ============================================================

print("Hello".isalpha())            # True  — all alphabetic
print("Hello123".isalnum())         # True  — all alphanumeric
print("12345".isdigit())            # True  — all digits (0-9)
print("12345".isnumeric())          # True  — broader: includes ² ½ etc.
print("12345".isdecimal())          # True  — strictest: decimal digits only
print("   ".isspace())              # True  — all whitespace
print("Hello World".istitle())      # True  — title-cased
print("HELLO".isupper())            # True  — all uppercase
print("hello".islower())            # True  — all lowercase
print("hello".isidentifier())       # True  — valid Python identifier
print("3hello".isidentifier())      # False — can't start with a digit
print("".isalpha())                 # False — empty string is always False


# ============================================================
# 9. ENCODING & BYTES
# ============================================================

s = "Hello, World!"

encoded = s.encode("utf-8")        # b'Hello, World!' — bytes object
decoded = encoded.decode("utf-8")  # "Hello, World!"  — back to str

# encode with error handling
s2 = "caf\u00e9"                   # "café"
print(s2.encode("ascii", errors="ignore"))      # b'caf'   — drop unknowns
print(s2.encode("ascii", errors="replace"))     # b'caf?'  — replace unknowns
print(s2.encode("ascii", errors="xmlcharrefreplace"))  # b'caf&#233;'


# ============================================================
# 10. FORMATTING
# ============================================================

name, age, score = "Alice", 30, 95.678

# f-strings (Python 3.6+) — fastest and most readable
print(f"Name: {name}, Age: {age}, Score: {score:.2f}")

# Format spec mini-language inside f-strings
print(f"{score:10.2f}")             # "     95.68" — width 10, 2 decimals
print(f"{age:05d}")                 # "00030"      — zero-padded int
print(f"{name:<10}")                # "Alice     " — left-aligned, width 10
print(f"{name:>10}")                # "     Alice" — right-aligned
print(f"{name:^10}")                # "  Alice   " — centred
print(f"{1_000_000:,}")             # "1,000,000"  — thousand separator
print(f"{0.1234:.1%}")              # "12.3%"      — percentage

# str.format() — still common in older codebases
print("{0} is {1} years old".format(name, age))
print("{name} scored {score:.1f}".format(name=name, score=score))
print("{:>10}".format("right"))     # right-aligned

# % formatting — legacy, avoid in new code
print("Hello, %s! You are %d years old." % (name, age))

# Template strings — safe for user-controlled input
from string import Template
t = Template("Hello, $name! You scored $score.")
print(t.substitute(name=name, score=score))
print(t.safe_substitute(name=name))   # No error if $score is missing


# ============================================================
# 11. SLICING & INDEXING
# ============================================================

s = "Hello, World!"

print(s[0])                         # "H"   — first character
print(s[-1])                        # "!"   — last character
print(s[7:12])                      # "World"
print(s[:5])                        # "Hello"
print(s[7:])                        # "World!"
print(s[::2])                       # Every other character
print(s[::-1])                      # "!dlroW ,olleH" — reversed string


# ============================================================
# 12. USEFUL PATTERNS
# ============================================================

# Check if a substring exists
print("python" in "I love python")      # True
print("java" not in "I love python")    # True

# Remove a prefix or suffix (Python 3.9+)
print("unwanted_hello".removeprefix("unwanted_"))   # "hello"
print("hello_unwanted".removesuffix("_unwanted"))   # "hello"

# Partition — split into exactly 3 parts around a separator
print("user@example.com".partition("@"))    # ("user", "@", "example.com")
print("user@example.com".rpartition("."))   # ("user@example", ".", "com")

# Expand tabs to spaces
print("col1\tcol2\tcol3".expandtabs(10))    # "col1      col2      col3"

# Unique sorted characters in a string
unique_chars = sorted(set("mississippi"))   # ['i', 'm', 'p', 's']

# Palindrome check
word = "racecar"
print(word == word[::-1])                   # True

# Count words in a sentence
sentence = "the quick brown fox jumps over the lazy dog"
word_freq = {}
for word in sentence.split():
    word_freq[word] = word_freq.get(word, 0) + 1
