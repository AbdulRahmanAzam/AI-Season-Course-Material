"""
THE ENGINE (no AI here on purpose)
==================================
This file does the real work of finding business leads. It has NO LangChain and
NO API key, so you can run it on its own and it will always work:

    python leads_core.py

Where the data comes from (both are 100% free, no key, never blocked):
  1. Nominatim  -> turns a city name ("los angeles") into a map box (bounding box)
  2. Overpass   -> the OpenStreetMap search engine; finds businesses inside that box
                   and gives us their name, phone, website, and sometimes email.

Emails are usually NOT on the map, so for each business that has a website we open
that website and look for an email with a simple pattern (regex).
"""

import csv
import os
import re
import time
import requests
from urllib.parse import urljoin

# Free public services. No sign-up, no key.
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Overpass has several free mirror servers. If one is busy we try the next -
# this is what keeps the tool working reliably (e.g. live in class).
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

# These services ask you to say who you are. Without this header Nominatim replies 403.
HEADERS = {"User-Agent": "leads-agent-teaching-demo/1.0 (educational use)"}

# A business type ("coffee") -> how OpenStreetMap tags it (key, value).
# If the word isn't here, we fall back to searching by the business NAME instead.
CATEGORY_TAGS = {
    "coffee": ("amenity", "cafe"),
    "cafe": ("amenity", "cafe"),
    "restaurant": ("amenity", "restaurant"),
    "bar": ("amenity", "bar"),
    "pub": ("amenity", "pub"),
    "bakery": ("shop", "bakery"),
    "hotel": ("tourism", "hotel"),
    "gym": ("leisure", "fitness_centre"),
    "pharmacy": ("amenity", "pharmacy"),
    "dentist": ("amenity", "dentist"),
    "salon": ("shop", "hairdresser"),
    "supermarket": ("shop", "supermarket"),
    "clothing": ("shop", "clothes"),
    "bookstore": ("shop", "books"),
}

# Simple pattern that matches things that look like an email address.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Junk that also matches the email pattern but isn't a real email.
_BAD_ENDINGS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")   # image file names
_BAD_WORDS = ("sentry", "wixpress", "@2x", "godaddy", "schema.org", ".wix.com")  # tracking / page builders
# Fake "fill-in-the-blank" emails that website templates leave behind.
_PLACEHOLDER_DOMAINS = {"example.com", "example.org", "example.net", "domain.com",
                        "email.com", "yourdomain.com", "yoursite.com", "website.com",
                        "company.com", "test.com", "sentry.io"}
_PLACEHOLDER_NAMES = {"user", "name", "yourname", "email", "example", "firstname.lastname"}


def geocode_city(city):
    """Turn a city name into a map box: (south, west, north, east)."""
    for attempt in range(2):  # retry once if the service hiccups
        try:
            r = requests.get(
                NOMINATIM_URL,
                params={"q": city, "format": "json", "limit": 1},
                headers=HEADERS,
                timeout=15,
            )
            data = r.json()
            if data:
                # Nominatim gives [south, north, west, east]; Overpass wants (south, west, north, east).
                bb = data[0]["boundingbox"]
                return float(bb[0]), float(bb[2]), float(bb[1]), float(bb[3])
        except Exception:
            time.sleep(1)
    raise ValueError(f"Could not find the city: {city}. Try a more specific name.")


def _run_overpass(query):
    """Send a query to Overpass, trying each mirror server until one answers with
    valid JSON. Returns the list of found elements."""
    for attempt in range(2):            # try the whole list of servers twice
        for url in OVERPASS_URLS:
            try:
                resp = requests.post(url, data={"data": query}, headers=HEADERS, timeout=60)
                return resp.json().get("elements", [])  # .json() fails if server is busy
            except Exception:
                continue                # this server is busy - try the next one
        time.sleep(2)                   # all servers busy - wait, then try again
    raise RuntimeError("OpenStreetMap is busy right now. Wait a few seconds and try again.")


def _build_address(tags):
    """Glue the separate address tags into one readable string."""
    street = (tags.get("addr:housenumber", "") + " " + tags.get("addr:street", "")).strip()
    town = (tags.get("addr:city", "") + " " + tags.get("addr:postcode", "")).strip()
    return ", ".join(part for part in (street, town) if part)


def _is_real_email(email):
    """Filter out fake/junk matches: image files, tracking, template placeholders."""
    e = email.lower()
    if e.endswith(_BAD_ENDINGS):
        return False
    if any(bad in e for bad in _BAD_WORDS):
        return False
    local, _, domain = e.partition("@")
    return domain not in _PLACEHOLDER_DOMAINS and local not in _PLACEHOLDER_NAMES


def find_email_on_website(url):
    """Open a business website and return the first real email found, else ''.
    Never raises - if anything goes wrong we just return an empty string."""
    if not url.startswith("http"):
        url = "http://" + url
    # Try the homepage first, then the usual contact pages.
    for page in (url, urljoin(url, "/contact"), urljoin(url, "/contact-us")):
        try:
            html = requests.get(page, headers=HEADERS, timeout=10).text
            for match in EMAIL_RE.findall(html):
                if _is_real_email(match):
                    return match
        except Exception:
            pass  # site down, timeout, bad SSL... just move on
    return ""


def find_places(category, city, max_email_lookups=25):
    """Find businesses of a type in a city. Returns a list of dicts with
    name, phone, email, website, address."""
    south, west, north, east = geocode_city(city)
    bbox = f"({south},{west},{north},{east})"

    # Pick an OpenStreetMap tag for the category, or fall back to a name search.
    selector = None
    cat = category.lower().strip()
    for word, (key, value) in CATEGORY_TAGS.items():
        if word in cat:
            selector = f'nwr["{key}"="{value}"]{bbox};'
            break
    if selector is None:
        selector = f'nwr["name"~"{category}",i]{bbox};'

    # Ask Overpass. "nwr" = nodes + ways + relations. "out tags 80" = up to 80 results.
    query = f"[out:json][timeout:25];\n{selector}\nout tags 80;"
    elements = _run_overpass(query)

    leads = []
    seen = set()
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name or name in seen:
            continue  # skip unnamed places and duplicates
        seen.add(name)
        leads.append({
            "name": name,
            "phone": tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or "",
            "email": tags.get("email") or tags.get("contact:email") or "",
            "website": tags.get("website") or tags.get("contact:website") or tags.get("url") or "",
            "address": _build_address(tags),
        })

    # Emails are rarely on the map, so visit websites to find them (capped for speed).
    lookups = 0
    for lead in leads:
        if lookups >= max_email_lookups:
            break
        if lead["website"] and not lead["email"]:
            lead["email"] = find_email_on_website(lead["website"])
            lookups += 1

    return leads


def save_leads_csv(leads, filename):
    """Save the leads to a CSV file inside the output/ folder. Returns the path."""
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)

    filename = re.sub(r"[^A-Za-z0-9_.-]", "_", filename)  # make it a safe file name
    if not filename.endswith(".csv"):
        filename += ".csv"
    path = os.path.join(out_dir, filename)

    columns = ["name", "phone", "email", "website", "address"]
    # utf-8-sig so accented names open correctly when double-clicked in Excel.
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(leads)
    return path


# ---------- Run this file directly to test everything WITHOUT any AI ----------
if __name__ == "__main__":
    category, city = "coffee", "los angeles"
    print(f"Searching for '{category}' in '{city}'  (pure Python, no AI)...")

    leads = find_places(category, city)
    print(f"Found {len(leads)} places.")

    path = save_leads_csv(leads, f"{category}_{city.replace(' ', '-')}")
    print("Saved to:", path)

    print("\nFirst few results:")
    for lead in leads[:5]:
        print(f" - {lead['name']} | {lead['phone'] or 'no phone'} | {lead['email'] or 'no email'}")
