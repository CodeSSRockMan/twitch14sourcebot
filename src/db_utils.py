import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')
JSON_PATH = os.path.join(os.path.dirname(__file__), 'data.json')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS expansions (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    )''')
    conn.commit()
    conn.close()

def load_json_to_db():
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Insert expansions
    for exp in data.get('expansions', []):
        c.execute('INSERT OR IGNORE INTO expansions (id, name) VALUES (?, ?)', (exp['id'], exp['name']))
    # Insert cities
    for city in data.get('cities', []):
        c.execute('INSERT OR IGNORE INTO cities (id, name) VALUES (?, ?)', (city['id'], city['name']))
    # Insert items
    for item in data.get('items', []):
        c.execute('INSERT OR IGNORE INTO items (id, name, description) VALUES (?, ?, ?)', (item['id'], item['name'], item['description']))
    conn.commit()
    conn.close()

def get_expansions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM expansions')
    result = c.fetchall()
    conn.close()
    return result

def get_cities():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM cities')
    result = c.fetchall()
    conn.close()
    return result

def get_items():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    result = c.fetchall()
    conn.close()
    return result

def get_item_by_name(item_name: str):
    """
    Search for an item by name (case-insensitive) in the items table.
    Returns a formatted message if found, else None.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, description FROM items WHERE LOWER(name) = LOWER(?)', (item_name,))
    row = c.fetchone()
    conn.close()
    if row:
        name, description = row
        return f"Item found: {name} - {description}"
    else:
        return None

def handle_isearch_command(item_name: str):
    """
    Search for an item by name (case-insensitive) and return a well-formatted English message for Twitch chat.
    Shows item name, type, and for gathered items, the specific aetheryte and cardinal direction.
    """
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return f"[Error] Could not read the database: {e}"

    items = data.get('items', [])
    item = next((i for i in items if i['name'].lower() == item_name.lower()), None)
    if not item:
        return f"[Not found] No item named '{item_name}' was found."

    # Basic info
    msg = f"[Item] {item['name']} (Level {item.get('level_requirement', '?')}, Rarity: {item.get('rarity', '?')})\nDescription: {item.get('description', '')}"

    sources = [s for s in data.get('item_sources', []) if s['item_id'] == item['id']]
    if not sources:
        return msg + "\n[Source] No acquisition info found."

    # Vendor
    vendor = next((s for s in sources if s['source_type'] == 'Vendor'), None)
    if vendor:
        npc = next((n for n in data.get('npcs', []) if n['id'] == vendor['source_id']), None)
        location = next((l for l in data.get('locations', []) if l['id'] == vendor['location_id']), None)
        coords = vendor.get('coordinates', {})
        if npc and location and coords:
            return (f"[Shop] {item['name']} can be purchased from {npc['name']} at {location['name']} "
                    f"(X: {coords.get('x', '?')}, Y: {coords.get('y', '?')}).")
        else:
            return msg + "\n[Shop] Vendor source incomplete."

    # Drop
    s = sources[0]
    if s['source_type'] == 'Drop':
        mob = next((n for n in data.get('npcs', []) if n['id'] == s['source_id']), None)
        location = next((l for l in data.get('locations', []) if l['id'] == s['location_id']), None)
        coords = s.get('coordinates', {})
        if mob and location and coords:
            return (f"[Drop] {item['name']} is dropped by {mob['name']} in {location['name']} "
                    f"(X: {coords.get('x', '?')}, Y: {coords.get('y', '?')}). {s.get('details','')}")
        else:
            return msg + "\n[Drop] Drop source incomplete."
    # Crafted
    if s['source_type'] == 'Crafted':
        recipe = next((r for r in data.get('recipes', []) if r['item_id'] == item['id']), None)
        if recipe:
            return (f"[Craft] {item['name']} can be crafted by {recipe['job']} (required level: {recipe['required_level']}).")
        else:
            return msg + "\n[Craft] Crafted source missing recipe."
    # Gathered
    if s['source_type'] == 'Gathered' or any(ri.get('method') == 'Gathered' for ri in data.get('recipe_ingredients', []) if ri.get('ingredient_item_id') == item['id']):
        item_loc = next((il for il in data.get('item_locations', []) if il['item_id'] == item['id']), None)
        if item_loc:
            location = next((l for l in data.get('locations', []) if l['id'] == item_loc['location_id']), None)
            aetheryte = next((a for a in data.get('aetherytes', []) if a['id'] == item_loc.get('aetheryte_id')), None)
            direction = item_loc.get('cardinal_direction')
            if location and aetheryte and direction:
                return (f"[Gather] {item['name']} can be found in {location['name']}.\n"
                        f"Use the aetheryte '{aetheryte['name']}' and head {direction} to coordinates X: {aetheryte['coordinates']['x']}, Y: {aetheryte['coordinates']['y']}.")
            elif location:
                return f"[Gather] {item['name']} can be found in {location['name']}."
            else:
                return f"[Gather] {item['name']} can be gathered, but location is unknown."
        else:
            return f"[Gather] {item['name']} can be gathered, but no location data available."
    return msg + "\n[Source] Unknown source."

if __name__ == "__main__":
    init_db()
    load_json_to_db()
    print("Expansions:", get_expansions())
    print("Cities:", get_cities())
    print("Items:", get_items())
