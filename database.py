import sqlite3
from datetime import datetime

DB_NAME = "kringloop.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        photo_path TEXT,
        cropped_photo_path TEXT,
        qr_path TEXT,
        base_price REAL,
        avg_market_price REAL,
        damage_percent INTEGER,
        final_price REAL,
        status TEXT,
        created_at TEXT,
        sold_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_product(title, category, photo_path, cropped_photo_path, qr_path,
                base_price, avg_market_price, damage_percent, final_price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO products (
        title, category, photo_path, cropped_photo_path, qr_path,
        base_price, avg_market_price, damage_percent, final_price,
        status, created_at, sold_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, category, photo_path, cropped_photo_path, qr_path,
        base_price, avg_market_price, damage_percent, final_price,
        "in_stock",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        None
    ))

    conn.commit()
    conn.close()


def get_products(status=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if status:
        cur.execute("SELECT * FROM products WHERE status = ?", (status,))
    else:
        cur.execute("SELECT * FROM products")

    products = cur.fetchall()
    conn.close()
    return products


def mark_as_sold(product_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    UPDATE products
    SET status = ?, sold_at = ?
    WHERE id = ?
    """, ("sold", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))

    conn.commit()
    conn.close()