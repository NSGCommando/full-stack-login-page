from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import backend_functions as bf
from backend_constants import BackendPaths
db_path = BackendPaths.DATABASE_PATH.value

application = Flask(__name__) # expose the app
CORS(application) # allows the app to receive requests from other IPs, needed because requests will come from the Vite server

# route: flask homepage
@application.route("/")
def index():
    # Just to check Flask API works. Remove after dev is done, reuse the SQL command for admin dashboard (later)
    # users = cursor.execute("select user_name, id from user_data").fetchall()
    return "flask API running"

# route: login, received from fetch URL in LoginPage
@application.route("/login",methods=["POST"])
@bf.data_conn
def login(data,conn):
    username = data.get("username")
    login_password = data.get("password")
    user = bf.get_user(conn, username)
    if not user:
        return jsonify({"error":"invalid credentials, user not found"}), 401 # 401 means unauthorized (Authentication failed or is missing)

    password_hash, is_admin = user
    if not bf.confirm_password(password_hash, login_password):
        return jsonify({"error":"invalid credentials, password wrong"}), 401

    return jsonify({
        "username": username,
        "is_admin": bool(is_admin)
    }), 200

# route: retrieve all users in database
@application.route("/api/users",methods=["POST"])
@bf.data_conn
def get_users(data, conn):
    admin_name = data.get("username")
    try: # try...finally to ensure the conn always closes even if query fails
        admin_checked = bf.admin_check(conn, admin_name)
        match admin_checked:
            case "No Admin":return jsonify({"error":"invalid credentials, user not found"}), 401
            case "No":return jsonify({"error":"invalid credentials, user is not Admin"}), 403 # Unauthorised
            case "Yes":
                user_list = bf.print_db(conn)
                return jsonify({
                    "users":user_list,
                    "user_count":len(user_list),
                    "message":"success fetching all users"
                }), 200
    finally:
        conn.close()

# route: delete an user
@application.route("/api/users",methods=["DELETE"])
@bf.data_conn
def delete_user(data, conn):
    target_user = data.get("target_name")
    admin_name = data.get("admin_username")
    admin_checked = bf.admin_check(conn,admin_name)
    match admin_checked:
        case "No Admin":return jsonify({"error":"invalid credentials, user not found"}), 401
        case "No":return jsonify({"error":"invalid credentials, user is not Admin"}), 403
        case "Yes":
            action_result = bf.del_data(conn,target_user)
            conn.commit()
            if not action_result:return jsonify({"error":"Target user cannot be deleted (admin or no user)"}), 403
            else: return jsonify({"message":"deletion successful"}), 200

# route: signup username check
@application.route("/check_username",methods=["POST"])
def check_user():
    data = request.json
    if not data: return jsonify({"error": "Invalid JSON"}), 400 # status bad request
    conn = bf.db_connect(db_path)
    username = data.get("username")
    try: # try...finally to ensure the conn always closes even if query fails
        user = bf.get_user(conn, username)
    finally:
        conn.close()
    if not user:
        return jsonify({"message":"user doesn't exist"}), 200 # status ok
    else:
        return jsonify({"message":"username already taken", "error":"user exists conflict"}), 409 # status conflict

# route: new user signup, only gets here AFTER username availability has been checked
@application.route("/signup",methods=["POST"])
def signup_user():
    data = request.json
    if not data: return jsonify({"error": "Invalid JSON"}), 400 # status bad request
    conn = bf.db_connect(db_path)
    username = data.get("username")
    password = data.get("password")
    password_hashed=bf.hash_passwords(password)
    try:
        bf.enter_data(conn,username,password_hashed)
        conn.commit()
        return jsonify({"message":"user signed up"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

if __name__=="__main__":
    application.run(debug=True)