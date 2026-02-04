import csv
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def confirm_password(hash, password):
    """
    Wrapper function to ensure the password hash stored and received password match
    Currently uses check_password_hash(hash,password) from werkzeug
    """
    return check_password_hash(hash,password)

def hash_passwords(password_passed):
    """Wrapper to generate and return password hash
    Currently uses generate_password_hash(password) from werkzeug"""
    password_hashed = generate_password_hash(password_passed)
    return password_hashed

def get_user(conn, username):
    cursor = conn.cursor()
    cursor.execute(
        # 'password' is the hashed password stored in database
        "SELECT password, is_admin FROM user_data WHERE user_name = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def enter_data(conn, name:str, password:str):
    """
    Enter data for users
    Users cannot be admin via this input
    arguments: database_connection, username, password_hash
    """
    cursor = conn.cursor()
    # SQLite is statement-level atomic so exception raising rows are skipped
    try:
        cursor.execute("INSERT INTO user_data (user_name,password) values(?,?)" ,(name,password))
    except sqlite3.IntegrityError:
        print(f'Duplicate entry skipped: {name}')
        raise # we want calling functions to get the exception
    

def read_data(conn, path):
    """
    Imports user data from data at 'path'
    enters each entry via 'conn' connector object
    Does not commit, the calling fn owns transaction
    """
    # 'with' tells python this has standard __enter__ and __exit__ actions, on entering and leaving the block
    # So this is a context manager
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for entry in reader:
            enter_data(conn, entry["name"],entry["password"])

def print_db(conn):
    """
    Function to print all data in a database
    Database location sent along with 'conn' object
    calling function owns the connector and it's closure
    """
    cursor = conn.cursor()
    # Select via query execution
    cursor.execute("select * from user_data")
    # print database
    results = cursor.fetchall()
    for i in results:
        print(i)

# databse connector def
def db_connect(path):
    connector = sqlite3.connect(path)
    connector.row_factory = sqlite3.Row
    return connector