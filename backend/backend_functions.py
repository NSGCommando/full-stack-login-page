from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.query_handler import get_user
import os

### Define helper functions ###
def confirm_password(hash, password)->bool:
    """
    Wrapper function to ensure the password hash stored and received password match
    Currently uses check_password_hash(hash,password) from werkzeug
    """
    return check_password_hash(hash,password)

def hash_passwords(password_passed)->str:
    """Wrapper to generate and return password hash
    Currently uses scrypt with work factor of 600,000 from werkzeug for production
    Uses PBKDF2 with work factor of only 1000 to test database bottlenecking"""
    if os.getenv('TESTING_MODE') == 'True':
        password_hashed = generate_password_hash(password_passed, method='pbkdf2:sha256:1000')
    else:
        # Production gets full security
        password_hashed = generate_password_hash(password_passed)
    return password_hashed

# check admin
def admin_check(session:Session, user_id:int):
    """
    Checks for existence of user and whether user is admin or not
    """
    user = get_user(session, id=user_id)
    if not user:
             return "No Admin"
    return "Yes" if user.is_admin else "No"