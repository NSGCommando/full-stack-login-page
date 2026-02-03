from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from backend_functions import db_connect, get_user, hash_passwords, confirm_password
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
    conn = db_connect(db_path)
    user = get_user(conn, username)
    if not user:
        return jsonify({"error":"invalid credentials"}), 401 # 401 means unauthorized (Authentication failed or is missing)

    password_hash, is_admin = user
    if not confirm_password(password_hash, password):
        return jsonify({"error":"invalid credentials"}), 401

    return jsonify({
        "username": username,
        "is_admin": bool(is_admin)
    }), 200

# route: show all users
@application.route("/")
def index():
    conn = db_connect(db_path)
    cursor = conn.cursor()
    users = cursor.execute("select user_name, id, password from user_data").fetchall()
    conn.close() # close connection to DB after work done
    return "flask API running"

# route: add new user, HTML form has action = "/add", 
# so flask will listen for POST requests from the "/add" url
@application.route("/add",methods=["POST"])
def add_user():
    name = request.form.get("user_name")
    password_hash = hash_passwords(request.form.get("password")) # always comes as string from HTML, hash first
    conn = db_connect(db_path)
    enter_data(conn, name, password_hash)
    conn.commit()
    conn.close()
    return redirect("/")

if __name__=="__main__":
    application.run(debug=True)