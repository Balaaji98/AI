import sqlite3

# Step 1: Connect to SQLite DB (file-based)
conn = sqlite3.connect("mvp_db.sqlite")
cursor = conn.cursor()

# Step 2: Create table (if not exists)
cursor.execute("""
CREATE TABLE IF NOT EXISTS mvp_orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    postcode TEXT,
    street TEXT,
    town TEXT,
    county TEXT,
    country TEXT
);
""")

# Step 3: Clear any existing data (for repeat runs)
cursor.execute("DELETE FROM mvp_orders;")

# Step 4: Insert sample records (10 rows: mix of correct & incorrect)
sample_data = [
    ("SW1A 1AA", "Buckingham Palace Road", "London", "Greater London", "UK"),  # ✅ Correct
    ("M3 1VE", "Mrk St", "MNCHSTR", "Manchstr", "UK")   # ❌ Incorrect postcode
]

cursor.executemany("""
INSERT INTO mvp_orders (postcode, street, town, county, country)
VALUES (?, ?, ?, ?, ?);
""", sample_data)

conn.commit()

# Step 5: Fetch and display inserted records
cursor.execute("SELECT * FROM mvp_orders;")
rows = cursor.fetchall()

print("✅ Sample Orders Loaded into SQLite:")
for row in rows:
    print(row)

cursor.close()
conn.close()
