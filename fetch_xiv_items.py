import requests
import time
import json
import sys

API_URL = "https://xivapi.com/item"
PAGE_SIZE = 3000
OUTPUT_PATH = "src/data.json"

# Argument validation
force = "-y" in sys.argv
if not force:
    confirm = input("This will update the items in src/data.json. Continue? (y/N): ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(0)

# Load current data
with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)
existing_items = {str(item['id']): item for item in db.get("items", []) if item.get("id")}

all_items = []
page = 1
item_count = 0

while True:
    print(f"Fetching page {page}...")
    resp = requests.get(API_URL, params={"limit": PAGE_SIZE, "page": page})
    if resp.status_code != 200:
        print(f"Error fetching page {page}: {resp.status_code}")
        break
    data = resp.json()
    results = data.get("Results", [])
    if not results:
        break
    for item in results:
        item_id = item.get("ID")
        name = item.get("Name")
        # If name is empty or null, try to fetch the item detail
        if not name:
            detail = requests.get(f"https://xivapi.com/item/{item_id}").json()
            name = detail.get("Name")
        # If still no name, keep previous if exists
        if not name and str(item_id) in existing_items:
            name = existing_items[str(item_id)].get("name")
        all_items.append({
            "id": item_id,
            "name": name
        })
        item_count += 1
        if item_count % 100 == 0:
            print(f"Processed {item_count} items...")
    # Validation before next page
    if not data.get("Pagination") or data["Pagination"]["PageNext"] is None:
        break
    page += 1
    time.sleep(20)

# Save to data.json (only items section)
db["items"] = all_items
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
print(f"Saved {len(all_items)} items to {OUTPUT_PATH}")
