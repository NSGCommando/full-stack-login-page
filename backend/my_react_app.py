from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from werkzeug.wrappers import response
from backend_functions import db_connect, get_user, hash_passwords, confirm_password, enter_data
from backend_constants import BackendPaths
db_path = BackendPaths.DATABASE_PATH.value

application = Flask(__name__) # expose the app
CORS(application) # allows the app to receive requests from other IPs, needed because requests will come from the Vite server

# route: login, received from fetch URL in LoginPage
@application.route("/login",methods=["POST"])
def login():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400 # 400 means bad request

    username = data.get("username")
    password = data.get("password")
    password_hashed=hash_passwords(password)
    conn = db_connect(db_path)
    try: # try...finally to ensure the conn always closes even if query fails
        user = get_user(conn, username)
    finally:
        conn.close()
    if not user:
        return jsonify({"error":"invalid credentials"}), 401 # 401 means unauthorized (Authentication failed or is missing)

    password_hash, is_admin = user
    if not confirm_password(password_hash, password_hashed):
        return jsonify({"error":"invalid credentials"}), 401

    return jsonify({
        "username": username,
        "is_admin": bool(is_admin)
    }), 200

# route: show all users
@application.route("/")
def index():
    # Just to check Flask API works. Remove after dev is done, reuse the SQL command for admin dashboard (later)
    # users = cursor.execute("select user_name, id from user_data").fetchall()
    return "flask API running"

# check if username exists already for signup handling
@application.route("/check_username",methods=["POST"])
def check_user():
    data = request.json
    if not data: return jsonify({"error": "Invalid JSON"}), 400 # status bad request
    username = data.get("username")
    conn = db_connect(db_path)
    try: # try...finally to ensure the conn always closes even if query fails
        user = get_user(conn, username)
    finally:
        conn.close()
    if not user:
        return jsonify({"message":"user doesn't exist"}), 200 # status ok
    else:
        return jsonify({"message":"username already taken", "error":"user exists conflict"}), 409 # status conflict

# new user signup, only gets here AFTER username availability has been checked
@application.route("/signup",methods=["POST"])
def signup_user():
    data = request.json
    if not data: return jsonify({"error": "Invalid JSON"}), 400 # status bad request
    username = data.get("username")
    password = data.get("password")
    password_hashed=hash_passwords(password)
    conn = db_connect(db_path)
    try:
        enter_data(conn,username,password_hashed)
        conn.commit()
        return jsonify({"message":"user signed up"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

if __name__=="__main__":
    application.run(debug=True)