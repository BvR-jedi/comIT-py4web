#!/usr/bin/env python3
"""
Cats API Client — Full CRUD operations against the Django REST Framework Cats API.
"""

import json
import getpass
import sys
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:8000/api/cats/"

# ── ANSI colours ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"

def header(title: str) -> None:
    width = 60
    print(f"\n{BOLD}{CYAN}{'─' * width}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * width}{RESET}")

def show_request(method: str, url: str, payload: dict | None = None) -> None:
    print(f"\n{BOLD}{YELLOW}▶ REQUEST{RESET}")
    print(f"  {BOLD}{method}{RESET}  {url}")
    if payload:
        print(f"  {DIM}Body:{RESET}")
        for line in json.dumps(payload, indent=4).splitlines():
            print(f"    {line}")

def show_response(response: requests.Response) -> None:
    colour = GREEN if response.ok else RED
    print(f"\n{BOLD}{colour}◀ RESPONSE  [{response.status_code} {response.reason}]{RESET}")
    try:
        data = response.json()
        pretty = json.dumps(data, indent=4)
        for line in pretty.splitlines():
            print(f"  {line}")
    except ValueError:
        print(f"  {response.text or '(empty body)'}")

def divider() -> None:
    print(f"\n{DIM}{'·' * 60}{RESET}")

# ── CRUD helpers ──────────────────────────────────────────────────────────────

def list_cats(auth: HTTPBasicAuth) -> list:
    """GET /api/cats/ — list all cats."""
    header("LIST ALL CATS  (GET)")
    url = BASE_URL
    show_request("GET", url)
    r = requests.get(url, auth=auth)
    show_response(r)
    return r.json() if r.ok else []

def get_cat(auth: HTTPBasicAuth, cat_id: int) -> dict | None:
    """GET /api/cats/{id}/ — retrieve a single cat."""
    header(f"GET CAT #{cat_id}  (GET)")
    url = f"{BASE_URL}{cat_id}/"
    show_request("GET", url)
    r = requests.get(url, auth=auth)
    show_response(r)
    return r.json() if r.ok else None

def create_cat(auth: HTTPBasicAuth, payload: dict) -> dict | None:
    """POST /api/cats/ — create a new cat."""
    header("CREATE CAT  (POST)")
    url = BASE_URL
    show_request("POST", url, payload)
    r = requests.post(url, json=payload, auth=auth)
    show_response(r)
    return r.json() if r.ok else None

def update_cat(auth: HTTPBasicAuth, cat_id: int, payload: dict) -> dict | None:
    """PUT /api/cats/{id}/ — fully replace a cat record."""
    header(f"UPDATE CAT #{cat_id}  (PUT)")
    url = f"{BASE_URL}{cat_id}/"
    show_request("PUT", url, payload)
    r = requests.put(url, json=payload, auth=auth)
    show_response(r)
    return r.json() if r.ok else None

def patch_cat(auth: HTTPBasicAuth, cat_id: int, payload: dict) -> dict | None:
    """PATCH /api/cats/{id}/ — partially update a cat record."""
    header(f"PATCH CAT #{cat_id}  (PATCH)")
    url = f"{BASE_URL}{cat_id}/"
    show_request("PATCH", url, payload)
    r = requests.patch(url, json=payload, auth=auth)
    show_response(r)
    return r.json() if r.ok else None

def delete_cat(auth: HTTPBasicAuth, cat_id: int) -> bool:
    """DELETE /api/cats/{id}/ — remove a cat."""
    header(f"DELETE CAT #{cat_id}  (DELETE)")
    url = f"{BASE_URL}{cat_id}/"
    show_request("DELETE", url)
    r = requests.delete(url, auth=auth)
    show_response(r)
    return r.status_code == 204

# ── Main demo ─────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}  🐱  Cats API — CRUD Client{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}")
    print(f"  Target: {CYAN}{BASE_URL}{RESET}\n")

    # ── Credentials ───────────────────────────────────────────────────────────
    username = input(f"{BOLD}Username:{RESET} ").strip()
    password = getpass.getpass(f"{BOLD}Password:{RESET} ")
    auth = HTTPBasicAuth(username, password)

    # ── Quick connectivity check ───────────────────────────────────────────────
    print(f"\n{DIM}Checking connectivity…{RESET}")
    try:
        probe = requests.get(BASE_URL, auth=auth, timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}✗ Could not reach {BASE_URL}{RESET}")
        print("  Make sure the Django dev server is running:\n"
              "    python manage.py runserver")
        sys.exit(1)

    if probe.status_code == 401:
        print(f"\n{RED}✗ Authentication failed (401). Check your credentials.{RESET}")
        sys.exit(1)

    print(f"{GREEN}✓ Connected successfully{RESET}")

    # ══════════════════════════════════════════════════════════════════════════
    # 1. LIST — show what's already in the database
    # ══════════════════════════════════════════════════════════════════════════
    divider()
    cats = list_cats(auth)
    print(f"\n  {BOLD}{len(cats)}{RESET} cat(s) currently in the database.")

    # ══════════════════════════════════════════════════════════════════════════
    # 2. CREATE — add two new cats
    # ══════════════════════════════════════════════════════════════════════════
    divider()
    whiskers = create_cat(auth, {
        "name":       "Whiskers",
        "kind":       "Persian",
        "age":        3,
        "weight":     4.2,
        "vaccinated": True,
    })

    divider()
    luna = create_cat(auth, {
        "name":       "Luna",
        "kind":       "Siamese",
        "age":        1,
        "weight":     3.1,
        "vaccinated": False,
    })

    # ══════════════════════════════════════════════════════════════════════════
    # 3. READ — fetch one cat by ID
    # ══════════════════════════════════════════════════════════════════════════
    if whiskers:
        divider()
        get_cat(auth, whiskers["id"])

    # ══════════════════════════════════════════════════════════════════════════
    # 4. UPDATE (PUT) — fully replace Luna's record
    # ══════════════════════════════════════════════════════════════════════════
    if luna:
        divider()
        update_cat(auth, luna["id"], {
            "name":       "Luna",
            "kind":       "Siamese",
            "age":        2,          # birthday!
            "weight":     3.5,
            "vaccinated": True,       # now vaccinated
        })

    # ══════════════════════════════════════════════════════════════════════════
    # 5. PARTIAL UPDATE (PATCH) — only change Whiskers' weight
    # ══════════════════════════════════════════════════════════════════════════
    if whiskers:
        divider()
        patch_cat(auth, whiskers["id"], {"weight": 4.8})

    # ══════════════════════════════════════════════════════════════════════════
    # 6. LIST again — confirm changes
    # ══════════════════════════════════════════════════════════════════════════
    divider()
    list_cats(auth)

    # ══════════════════════════════════════════════════════════════════════════
    # 7. DELETE — remove both demo cats
    # ══════════════════════════════════════════════════════════════════════════
    for cat in [whiskers, luna]:
        if cat:
            divider()
            deleted = delete_cat(auth, cat["id"])
            status = f"{GREEN}✓ Deleted{RESET}" if deleted else f"{RED}✗ Failed{RESET}"
            print(f"\n  {status}  —  {cat['name']} (id={cat['id']})")

    # ══════════════════════════════════════════════════════════════════════════
    # 8. LIST final — confirm deletions
    # ══════════════════════════════════════════════════════════════════════════
    divider()
    remaining = list_cats(auth)
    print(f"\n  {BOLD}{len(remaining)}{RESET} cat(s) remain after cleanup.")

    print(f"\n{BOLD}{GREEN}{'═' * 60}{RESET}")
    print(f"{BOLD}{GREEN}  All CRUD operations completed.{RESET}")
    print(f"{BOLD}{GREEN}{'═' * 60}{RESET}\n")


if __name__ == "__main__":
    main()
