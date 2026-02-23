from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, get_jwt_identity, unset_access_cookies
from datetime import timedelta
from flask_cors import CORS
import os, backend.backend_functions as bf, backend.backend_constants as bc, backend.query_handler as qh
from dotenv import load_dotenv

# extract string for custom header
frontend_header = bc.CustomHeaders.CUSTOM_HEADER_FRONTEND.value
frontend_header_response = bc.CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value
application = Flask(__name__) # expose the app
# allows the app to receive requests from the Vite server IP, and allow browser to attach cookies
CORS(application, supports_credentials=True,origins=["http://localhost:5173"], allow_headers=["Content-Type",frontend_header])

# Secret key for JWT signing
load_dotenv()
# set up application's configs for JWT manager
application.config["JWT_SECRET_KEY"] = os.getenv('SECRET_SIGN_KEY')
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10) # token expires after 10 minutes
application.config["JWT_TOKEN_LOCATION"] = ["cookies"]
application.config["JWT_COOKIE_SECURE"] = False # running on localhost, so no SSH
application.config["JWT_COOKIE_CSRF_PROTECT"] = False # Didn't setup CSRF so double token security isn't implemented
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
@qh.data_conn
def login(data,session):
    username = data.get("username")
    login_password = data.get("password")
    user = qh.get_user(session, username=username)
    if not user:
        return jsonify({"error":"invalid credentials, user not found"}), 401 # 401 means unauthorized (Authentication failed or missing)

    if not bf.confirm_password(user.password, login_password):
        return jsonify({"error":"invalid credentials, password wrong"}), 401
    
    access_token = create_access_token(identity=str(user.id))
    response = jsonify({
        "username": username,
        "is_admin": user.is_admin
    })
    set_access_cookies(response, access_token)
    return response, 200

# route: logout and disable cookie
@application.route("/logout",methods=["GET"])
def logout_user():
    response = jsonify({"message":"Logout successful"})
    unset_access_cookies(response)
    return response,200

# route: verify current user token validity and return username, admin status if valid
@application.route("/verify_token", methods=['GET'])
@jwt_required()
@qh.data_conn
def verify(session,**kwargs):
    # If the code gets here, the token is valid
    current_user_id = get_jwt_identity()
    user = qh.get_user(session,id=current_user_id)
    if not user:
        return jsonify({"error":"invalid credentials, user not found"}), 401
    return {"message": "Token is valid", "username": user.user_name, "is_admin": user.is_admin}, 200

# route: retrieve all users in database
@application.route("/api/users",methods=["GET"])
@jwt_required()
@qh.data_conn
def get_users(session,**kwargs):
    current_user =  get_jwt_identity()
    admin_checked = bf.admin_check(session, current_user)
    match admin_checked:
        case "No Admin":return jsonify({"error":"invalid credentials, user not found"}), 401
        case "No":return jsonify({"error":"invalid credentials, user is not Admin"}), 403
        case "Yes":
            user_list = qh.print_db(session)
            return jsonify({
                "users":user_list,
                "user_count":len(user_list),
                "message":"success fetching all users"
            }), 200

# route: delete an user
@application.route("/api/users",methods=["DELETE"])
@jwt_required()
@qh.data_conn
def delete_user(data, session):
    """
    Delete user by id
    Returns a json message and status code
    """
    target_user_id = data.get("target_id")
    admin_id =  get_jwt_identity()
    admin_checked = bf.admin_check(session,admin_id)
    match admin_checked:
        case "No Admin":return jsonify({"error":"invalid credentials, user not found"}), 401
        case "No":return jsonify({"error":"invalid credentials, user is not Admin"}), 403
        case "Yes":
            action_result = qh.del_data(session,target_user_id)
            session.commit()
            if not action_result:return jsonify({"error":"Target user cannot be deleted (admin or no user)"}), 403
            else: return jsonify({"message":"deletion successful"}), 200

# route: signup username check
@application.route("/check_username",methods=["POST"])
@qh.data_conn
def check_username_taken(data, session):
    username = data.get("username")
    user = qh.get_user(session, username=username)
    if not user:
        return jsonify({"message":"user doesn't exist"}), 200 # status ok
    else:
        return jsonify({"message":"username already taken", "error":"user exists conflict"}), 409 # status conflict

# route: new user signup, only gets here AFTER username availability has been checked
@application.route("/signup",methods=["POST"])
@qh.data_conn
def signup_user(data, session):
    username = data.get("username")
    password = data.get("password")
    password_hashed=bf.hash_passwords(password)
    try:
        qh.enter_data(session,username,password_hashed)
        session.commit()
        return jsonify({"message":"user signed up"}), 201 # request successfully created new user resource
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@application.teardown_appcontext
def remove_session(exception=None):
    """
    Cleans up all scoped sessions created during the request.
    """
    # obtain the request cache from the query handler and wipe all factory sessions for this thread
    qh.remove_cached_sessions()

if __name__=="__main__":
    application.run(debug=True)