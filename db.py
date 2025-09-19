import sqlite3, os

DB_PATH = "data/users.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, city TEXT, goal TEXT, calories INTEGER)")
    conn.commit()
    conn.close()

def save_order(uid, name, phone, city, calories):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (id,name,phone,city,calories) VALUES (?,?,?,?,?)",
              (uid,name,phone,city,calories))
    conn.commit()
    conn.close()
