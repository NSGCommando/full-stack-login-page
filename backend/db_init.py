import os
import sqlite3
from backend_functions import read_data, hash_passwords
from backend_constants import BackendPaths
from dotenv import load_dotenv

load_dotenv()
# admin data
password_hash = hash_passwords(os.getenv('ADMIN_KEY'))
admin_name = os.getenv('ADMIN_USERNAME')

# create the table if it doesn't exist
conn = sqlite3.connect(BackendPaths.DATABASE_PATH.value)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE if not exists user_data(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_name TEXT UNIQUE,
password TEXT,
is_admin INTEGER NOT NULL DEFAULT 0
)
""")

# Insert default admin details from backend
cursor.execute("""
INSERT OR IGNORE INTO user_data (user_name, password, is_admin)
VALUES (?, ?, 1)
""", (admin_name,password_hash))

# read data from any csv files
read_data(conn, BackendPaths.CSV_PATH.value)
conn.commit()
conn.close()