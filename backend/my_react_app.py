from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, get_jwt_identity
from datetime import timedelta
from flask_cors import CORS
import os
from dotenv import load_dotenv
import backend_functions as bf
from backend_constants import BackendPaths

# point to database path
db_path = BackendPaths.DATABASE_PATH.value

application = Flask(__name__) # expose the app
# allows the app to receive requests from the Vite server IP, and allow browser to attach cookies
CORS(application, supports_credentials=True,origins=["http://localhost:5173"])

# Secret key for JWT signing
load_dotenv()
# set up application's configs for JWT manager
application.config["JWT_SECRET_KEY"] = os.getenv('SECRET_SIGN_KEY')
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10) # token expires after 10 minutes
application.config["JWT_TOKEN_LOCATION"] = ["cookies"]
application.config["JWT_COOKIE_SECURE"] = False # running on localhost, so no SSH
application.config["JWT_COOKIE_CSRF_PROTECT"] = False # Didn't setup CSF so double token isn't implemented
application.config["JWT_COOKIE_SAMESITE"] = "Lax" # To prevent browser from attaching JWTs to forged requests
jwt = JWTManager(application) # create the JWT manager instance for the exposed application

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
        return jsonify({"error":"invalid credentials, user not found"}), 401 # 401 means unauthorized (Authentication failed or missing)

    password_hash, is_admin = user
    if not bf.confirm_password(password_hash, login_password):
        return jsonify({"error":"invalid credentials, password wrong"}), 401
    
    access_token = create_access_token(identity=username)
    response = jsonify({
        "username": username,
        "is_admin": bool(is_admin)
    })
    set_access_cookies(response, access_token)
    return response, 200

# route: retrieve all users in database
@application.route("/api/users",methods=["GET"])
@jwt_required()
@bf.data_conn
def get_users(data, conn):
    current_user =  get_jwt_identity()
    admin_checked = bf.admin_check(conn, current_user)
    match admin_checked:
        case "No Admin":return jsonify({"error":"invalid credentials, user not found"}), 401
        case "No":return jsonify({"error":"invalid credentials, user is not Admin"}), 403
        case "Yes":
            user_list = bf.print_db(conn)
            return jsonify({
                "users":user_list,
                "user_count":len(user_list),
                "message":"success fetching all users"
            }), 200

# route: delete an user
@application.route("/api/users",methods=["DELETE"])
@jwt_required()
@bf.data_conn
def delete_user(data, conn):
    target_user = data.get("target_name")
    admin_name =  get_jwt_identity()
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
@bf.data_conn
def check_user(data, conn):
    username = data.get("username")
    user = bf.get_user(conn, username)
    if not user:
        return jsonify({"message":"user doesn't exist"}), 200 # status ok
    else:
        return jsonify({"message":"username already taken", "error":"user exists conflict"}), 409 # status conflict

# route: new user signup, only gets here AFTER username availability has been checked
@application.route("/signup",methods=["POST"])
@bf.data_conn
def signup_user(data, conn):
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