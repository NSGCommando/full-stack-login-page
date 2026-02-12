import csv, sqlite3, os
from typing import Optional, Any
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import request, jsonify
from backend_constants import BackendPaths, CustomHeaders
# extract strings from constants file
db_path = BackendPaths.DATABASE_PATH.value
test_path = BackendPaths.TEST_DATABASE_PATH.value
frontend_header = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
frontend_header_response = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value

### Define helper functions ###
def confirm_password(hash, password)->bool:
    """
    Wrapper function to ensure the password hash stored and received password match
    Currently uses check_password_hash(hash,password) from werkzeug
    """
    return check_password_hash(hash,password)

def hash_passwords(password_passed)->str:
    """Wrapper to generate and return password hash
    Currently uses generate_password_hash(password) from werkzeug"""
    password_hashed = generate_password_hash(password_passed)
    return password_hashed

def get_user(conn:sqlite3.Connection, **kwargs)->Optional[sqlite3.Row]:
    user_id = kwargs.get("id")
    username = kwargs.get("username")
    cursor = conn.cursor()
    if user_id:
        cursor.execute(
            # 'password' is the hashed password stored in database
            "SELECT id, user_name, password, is_admin FROM user_data WHERE id = ?",
            (user_id,)
        )
    elif username:
        cursor.execute(
            # 'password' is the hashed password stored in database
            "SELECT id, user_name, password, is_admin FROM user_data WHERE user_name = ?",
            (username,)
        )
    user = cursor.fetchone()
    return user

def enter_data(conn:sqlite3.Connection, name:str, password:str)->None:
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
        raise # we want calling functions to get the exception

# delete sql data
def del_data(conn:sqlite3.Connection, id:int)->int:
    """
    Delete data of users
    Commit and closure handled by calling fn
    """
    cursor = conn.cursor()
    admin_status = cursor.execute("select is_admin from user_data where id=?",(id,)).fetchone()
    # (id,) is needed for sqlite3 to recognise it as a list of arguments; (name) is just a string
    if admin_status is None or admin_status[0]==1: # fetchone packs data into tuple so admin_status is (1,)
        return False
    else:
        cursor.execute("delete from user_data where id = ?",(id,))
        return cursor.rowcount > 0 # return True if rowcount is positive (deletion happened)
    

def read_data(conn:sqlite3.Connection, path:str)->None:
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

def print_db(conn:sqlite3.Connection)->list[dict[str, Any]]:
    """
    Function to print all data in a database
    Database location sent along with 'conn' object
    calling function owns the connector and it's closure
    """
    cursor = conn.cursor()
    # Select via query execution
    cursor.execute("select id, user_name, is_admin from user_data")
    # retrieve all results
    user_list = cursor.fetchall()
    return [dict(user) for user in user_list] # convert Row objects into list of dictionaries

# check admin
def admin_check(conn:sqlite3.Connection, user_id:int):
    """
    Checks for existence of user and whether user is admin or not
    """
    user = get_user(conn, id=user_id)
    if not user:
             return "No Admin"
    return "Yes" if user['is_admin'] else "No"

# decorator for boilerplate conn and data check
def data_conn(f):
    """
    decorator to confirm data validity, return data and connection objects
    DB connection opened and closed by decorated function
    """
    @wraps(f)
    def edited_f(*args,**kwargs):
        data = request.get_json(silent=True)
        if request.headers.get(frontend_header) != frontend_header_response:
            return jsonify({"error": "Unauthorised Access"}), 403 # reject the request if the custom header value is wrong
        # GET requests don't need a body, everyone else DOES, as per frontend schema
        if not data and request.method in ["POST","PUT", "DELETE"]:
            return jsonify({"error": "Invalid JSON"}), 400 # using decorator ensures I don't have to raise the error higher
        # test path management
        if os.environ.get('TESTING_MODE') == 'True':
            path=test_path # ensure testing path is included
        else:
            path=db_path
        
        conn = None # default value in case database is locked/cannot be read for whatever reason
        try:
            conn = db_connect(path)
            return f(data, conn, *args,**kwargs) # call original fn for object injection here
        finally:
            if conn:conn.close() # close after the route fn is finished, decorator handles connection closing even if route crashes
    return edited_f

# databse connector def
def db_connect(path):
    """
    Opens a connection to database, adding a convertor from raw data to Row Objects
    These can be used to access via column names, like dictionaries
    """
    connector = sqlite3.connect(path)
    # WAL mode opens a temp file to store all edits, merging into main db sequentially later
    connector.execute('PRAGMA journal_mode=WAL;')
    connector.execute('PRAGMA busy_timeout = 5000;') # wait 5 seconds for edit lock to clear befire throwing error
    connector.row_factory = sqlite3.Row # Row object allows value indexing
    return connector