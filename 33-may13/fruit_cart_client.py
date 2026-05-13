"""
fruit_cart_client.py
--------------------
Consumes the Fruit Shopping Cart API.
- Seeds 20 fruits on first run
- While-loop menu with match-case for navigation
- Admins get full CRUD on fruits + carts
- Customers get CRUD on their own carts only
"""

import requests

BASE_URL = "http://127.0.0.1:8008/api"

# ─── Seed data ────────────────────────────────────────────────────────────────

SEED_FRUITS = [
    {"name": "Mango",       "weight_kg": "1.500", "price_per_kg": "3.50"},
    {"name": "Banana",      "weight_kg": "0.150", "price_per_kg": "1.20"},
    {"name": "Apple",       "weight_kg": "0.200", "price_per_kg": "2.00"},
    {"name": "Orange",      "weight_kg": "0.250", "price_per_kg": "1.80"},
    {"name": "Pineapple",   "weight_kg": "1.200", "price_per_kg": "2.50"},
    {"name": "Watermelon",  "weight_kg": "5.000", "price_per_kg": "0.80"},
    {"name": "Strawberry",  "weight_kg": "0.400", "price_per_kg": "4.50"},
    {"name": "Blueberry",   "weight_kg": "0.125", "price_per_kg": "8.00"},
    {"name": "Grape",       "weight_kg": "0.500", "price_per_kg": "3.00"},
    {"name": "Peach",       "weight_kg": "0.300", "price_per_kg": "3.20"},
    {"name": "Pear",        "weight_kg": "0.250", "price_per_kg": "2.10"},
    {"name": "Cherry",      "weight_kg": "0.100", "price_per_kg": "6.00"},
    {"name": "Papaya",      "weight_kg": "0.800", "price_per_kg": "2.80"},
    {"name": "Kiwi",        "weight_kg": "0.100", "price_per_kg": "4.00"},
    {"name": "Lemon",       "weight_kg": "0.130", "price_per_kg": "1.50"},
    {"name": "Lime",        "weight_kg": "0.100", "price_per_kg": "1.60"},
    {"name": "Coconut",     "weight_kg": "0.900", "price_per_kg": "3.00"},
    {"name": "Plum",        "weight_kg": "0.150", "price_per_kg": "2.90"},
    {"name": "Apricot",     "weight_kg": "0.080", "price_per_kg": "3.50"},
    {"name": "Pomegranate", "weight_kg": "0.350", "price_per_kg": "5.00"},
]


# ─── HTTP helpers ──────────────────────────────────────────────────────────────

def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def handle_response(resp: requests.Response) -> dict | list | None:
    """Print errors and return parsed JSON or None."""
    if resp.status_code in (200, 201):
        return resp.json()
    print(f"  [!] {resp.status_code}: {resp.text}")
    return None


# ─── Auth ──────────────────────────────────────────────────────────────────────

def login(username: str, password: str) -> str | None:
    """Return access token or None on failure."""
    resp = requests.post(f"{BASE_URL}/token/", json={"username": username, "password": password})
    data = handle_response(resp)
    return data["access"] if data else None


# ─── Seed ──────────────────────────────────────────────────────────────────────

def seed_fruits(token: str) -> None:
    """Post all seed fruits; skip those that already exist (unique name)."""
    headers = get_headers(token)
    existing = {f["name"] for f in requests.get(f"{BASE_URL}/fruits/", headers=headers).json()}
    created = 0
    for fruit in SEED_FRUITS:
        if fruit["name"] not in existing:
            resp = requests.post(f"{BASE_URL}/fruits/", json=fruit, headers=headers)
            if resp.status_code == 201:
                created += 1
    print(f"  Seeded {created} new fruit(s). ({len(existing)} already existed)")


# ─── Fruit CRUD (admin only) ───────────────────────────────────────────────────

def list_fruits(token: str) -> list:
    resp = requests.get(f"{BASE_URL}/fruits/", headers=get_headers(token))
    fruits = handle_response(resp) or []
    print(f"\n  {'ID':<5} {'Name':<15} {'Weight (kg)':<14} {'Price/kg':>10}")
    print("  " + "─" * 48)
    for f in fruits:
        print(f"  {f['id']:<5} {f['name']:<15} {f['weight_kg']:<14} {f['price_per_kg']:>10}")
    return fruits


def create_fruit(token: str) -> None:
    print("\n  — New Fruit —")
    name     = input("  Name         : ").strip()
    weight   = input("  Weight (kg)  : ").strip()
    price    = input("  Price/kg     : ").strip()
    resp = requests.post(
        f"{BASE_URL}/fruits/",
        json={"name": name, "weight_kg": weight, "price_per_kg": price},
        headers=get_headers(token),
    )
    data = handle_response(resp)
    if data:
        print(f"  Created: {data['name']} (id={data['id']})")


def update_fruit(token: str) -> None:
    list_fruits(token)
    fruit_id = input("\n  Fruit ID to update: ").strip()
    print("  Leave blank to keep current value.")
    name   = input("  New name         : ").strip()
    weight = input("  New weight (kg)  : ").strip()
    price  = input("  New price/kg     : ").strip()
    payload = {}
    if name:   payload["name"]         = name
    if weight: payload["weight_kg"]    = weight
    if price:  payload["price_per_kg"] = price
    resp = requests.patch(
        f"{BASE_URL}/fruits/{fruit_id}/",
        json=payload,
        headers=get_headers(token),
    )
    data = handle_response(resp)
    if data:
        print(f"  Updated: {data['name']}")


def delete_fruit(token: str) -> None:
    list_fruits(token)
    fruit_id = input("\n  Fruit ID to delete: ").strip()
    resp = requests.delete(f"{BASE_URL}/fruits/{fruit_id}/", headers=get_headers(token))
    if resp.status_code == 204:
        print("  Fruit deleted.")
    else:
        print(f"  [!] {resp.status_code}: {resp.text}")


# ─── Cart CRUD ─────────────────────────────────────────────────────────────────

def list_carts(token: str) -> list:
    resp = requests.get(f"{BASE_URL}/carts/", headers=get_headers(token))
    carts = handle_response(resp) or []
    print(f"\n  {'ID':<5} {'Owner':<10} {'Items':<8} {'Total':>10}")
    print("  " + "─" * 38)
    for c in carts:
        print(f"  {c['id']:<5} {str(c['owner']):<10} {len(c['items']):<8} {str(c['total']):>10}")
    return carts


def view_cart(token: str) -> None:
    list_carts(token)
    cart_id = input("\n  Cart ID to view: ").strip()
    resp = requests.get(f"{BASE_URL}/carts/{cart_id}/", headers=get_headers(token))
    data = handle_response(resp)
    if not data:
        return
    print(f"\n  Cart #{data['id']}  —  Owner: {data['owner']}  —  Created: {data['created_at']}")
    print(f"  {'Item ID':<9} {'Fruit':<15} {'Qty (kg)':<12} {'Subtotal':>10}")
    print("  " + "─" * 50)
    for item in data["items"]:
        print(f"  {item['id']:<9} {item['fruit_name']:<15} {item['quantity_kg']:<12} {str(item['subtotal']):>10}")
    print("  " + "─" * 50)
    print(f"  {'Total':>38}  {str(data['total']):>10}")


def create_cart(token: str) -> None:
    resp = requests.post(f"{BASE_URL}/carts/", json={}, headers=get_headers(token))
    data = handle_response(resp)
    if data:
        print(f"  Cart created (id={data['id']})")


def delete_cart(token: str) -> None:
    list_carts(token)
    cart_id = input("\n  Cart ID to delete: ").strip()
    resp = requests.delete(f"{BASE_URL}/carts/{cart_id}/", headers=get_headers(token))
    if resp.status_code == 204:
        print("  Cart deleted.")
    else:
        print(f"  [!] {resp.status_code}: {resp.text}")


# ─── Cart Item CRUD ────────────────────────────────────────────────────────────

def add_item(token: str) -> None:
    list_carts(token)
    cart_id = input("\n  Cart ID        : ").strip()
    list_fruits(token)
    fruit_id = input("\n  Fruit ID       : ").strip()
    qty      = input("  Quantity (kg)  : ").strip()
    resp = requests.post(
        f"{BASE_URL}/carts/{cart_id}/items/",
        json={"fruit": fruit_id, "quantity_kg": qty},
        headers=get_headers(token),
    )
    data = handle_response(resp)
    if data:
        print(f"  Added {data['quantity_kg']} kg of {data['fruit_name']}  —  subtotal: {data['subtotal']}")


def update_item(token: str) -> None:
    list_carts(token)
    cart_id = input("\n  Cart ID  : ").strip()
    view_cart_by_id(token, cart_id)
    item_id = input("  Item ID  : ").strip()
    qty     = input("  New quantity (kg): ").strip()
    resp = requests.patch(
        f"{BASE_URL}/carts/{cart_id}/items/{item_id}/",
        json={"quantity_kg": qty},
        headers=get_headers(token),
    )
    data = handle_response(resp)
    if data:
        print(f"  Updated: {data['quantity_kg']} kg  —  subtotal: {data['subtotal']}")


def remove_item(token: str) -> None:
    list_carts(token)
    cart_id = input("\n  Cart ID  : ").strip()
    view_cart_by_id(token, cart_id)
    item_id = input("  Item ID to remove: ").strip()
    resp = requests.delete(
        f"{BASE_URL}/carts/{cart_id}/items/{item_id}/",
        headers=get_headers(token),
    )
    if resp.status_code == 204:
        print("  Item removed.")
    else:
        print(f"  [!] {resp.status_code}: {resp.text}")


def view_cart_by_id(token: str, cart_id: str) -> None:
    """Helper to display a single cart inline without asking for ID again."""
    resp = requests.get(f"{BASE_URL}/carts/{cart_id}/", headers=get_headers(token))
    data = handle_response(resp)
    if not data:
        return
    print(f"\n  {'Item ID':<9} {'Fruit':<15} {'Qty (kg)':<12} {'Subtotal':>10}")
    print("  " + "─" * 50)
    for item in data["items"]:
        print(f"  {item['id']:<9} {item['fruit_name']:<15} {item['quantity_kg']:<12} {str(item['subtotal']):>10}")


# ─── Menus ────────────────────────────────────────────────────────────────────

def print_admin_menu() -> None:
    print("""
  ╔══════════════════════════════════╗
  ║     Fruit Cart  —  ADMIN         ║
  ╠══════════════════════════════════╣
  ║  Fruits                          ║
  ║    1  List fruits                ║
  ║    2  Add fruit                  ║
  ║    3  Edit fruit                 ║
  ║    4  Delete fruit               ║
  ╠══════════════════════════════════╣
  ║  Carts                           ║
  ║    5  List carts                 ║
  ║    6  View cart detail           ║
  ║    7  Create cart                ║
  ║    8  Delete cart                ║
  ╠══════════════════════════════════╣
  ║  Cart Items                      ║
  ║    9  Add item to cart           ║
  ║   10  Update item quantity       ║
  ║   11  Remove item from cart      ║
  ╠══════════════════════════════════╣
  ║    0  Exit                       ║
  ╚══════════════════════════════════╝""")


def print_customer_menu() -> None:
    print("""
  ╔══════════════════════════════════╗
  ║     Fruit Cart  —  CUSTOMER      ║
  ╠══════════════════════════════════╣
  ║  Fruits                          ║
  ║    1  List fruits                ║
  ╠══════════════════════════════════╣
  ║  Carts                           ║
  ║    2  My carts                   ║
  ║    3  View cart detail           ║
  ║    4  Create cart                ║
  ║    5  Delete cart                ║
  ╠══════════════════════════════════╣
  ║  Cart Items                      ║
  ║    6  Add item to cart           ║
  ║    7  Update item quantity       ║
  ║    8  Remove item from cart      ║
  ╠══════════════════════════════════╣
  ║    0  Exit                       ║
  ╚══════════════════════════════════╝""")


# def is_admin(token: str) -> bool:
#     """Detect admin by attempting to create a test fruit and checking the status code."""
#     resp = requests.get(f"{BASE_URL}/fruits/", headers=get_headers(token))
#     # A lightweight check: admins can POST to /fruits/; we use a dry OPTIONS probe
#     probe = requests.options(f"{BASE_URL}/fruits/", headers=get_headers(token))
#     # Simpler: try fetching all carts — admins see everyone's, customers only theirs
#     # We rely on the server returning > own carts for admins, but the cleanest
#     # approach is to read the user profile. Since we have no /me/ endpoint, we
#     # use a write-permission probe on fruits.
#     test = requests.post(
#         f"{BASE_URL}/fruits/",
#         json={"name": "__probe__", "weight_kg": "0.001", "price_per_kg": "0.001"},
#         headers=get_headers(token),
#     )
#     if test.status_code == 201:
#         # Clean up the probe fruit immediately
#         fruit_id = test.json()["id"]
#         requests.delete(f"{BASE_URL}/fruits/{fruit_id}/", headers=get_headers(token))
#         return True
#     return False

def is_admin(token: str) -> bool:
    # A safe, dry way to check permissions without writing to the DB
    probe = requests.options(f"{BASE_URL}/fruits/", headers=get_headers(token))
    if probe.status_code == 200:
        # If "POST" is in the allowed actions, DRF confirms they are an Admin
        if "POST" in probe.json().get("actions", {}):
            return True
    return False


# ─── Admin loop ───────────────────────────────────────────────────────────────

def admin_loop(token: str) -> None:
    while True:
        print_admin_menu()
        choice = input("  > ").strip()
        match choice:
            case "1":
                list_fruits(token)
            case "2":
                create_fruit(token)
            case "3":
                update_fruit(token)
            case "4":
                delete_fruit(token)
            case "5":
                list_carts(token)
            case "6":
                view_cart(token)
            case "7":
                create_cart(token)
            case "8":
                delete_cart(token)
            case "9":
                add_item(token)
            case "10":
                update_item(token)
            case "11":
                remove_item(token)
            case "0":
                print("  Goodbye!")
                break
            case _:
                print("  Invalid option. Please choose from the menu.")


# ─── Customer loop ────────────────────────────────────────────────────────────

def customer_loop(token: str) -> None:
    while True:
        print_customer_menu()
        choice = input("  > ").strip()
        match choice:
            case "1":
                list_fruits(token)
            case "2":
                list_carts(token)
            case "3":
                view_cart(token)
            case "4":
                create_cart(token)
            case "5":
                delete_cart(token)
            case "6":
                add_item(token)
            case "7":
                update_item(token)
            case "8":
                remove_item(token)
            case "0":
                print("  Goodbye!")
                break
            case _:
                print("  Invalid option. Please choose from the menu.")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    print("\n  ╔══════════════════════════════════╗")
    print(  "  ║      Fruit Cart API Client       ║")
    print(  "  ╚══════════════════════════════════╝")

    # ── Login ──
    username = input("\n  Username: ").strip()
    password = input("  Password: ").strip()

    token = login(username, password)
    if not token:
        print("  Authentication failed. Check credentials and server.")
        return

    print(f"  Logged in as '{username}'.")

    # ── Detect role and seed if admin ──
    admin = is_admin(token)
    if admin:
        print("  Role: ADMIN")
        print("\n  Seeding fruits...")
        seed_fruits(token)
        admin_loop(token)
    else:
        print("  Role: CUSTOMER")
        customer_loop(token)


if __name__ == "__main__":
    main()
