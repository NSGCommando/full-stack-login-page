import os, sys
from locust import HttpUser, between, task, events
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)
from backend.backend_constants import CustomHeaders
from backend.query_handler import shutdown_sessions

TRUE_HEADER = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
TRUE_HEADER_RESPONSE = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value

class User(HttpUser):
    wait_time = between(3,6)
    def on_start(self) -> None:
        """Setup the custom header for the user session"""
        self.client.headers.update({TRUE_HEADER: TRUE_HEADER_RESPONSE})
    
    @task(1)
    def signup_login_logout(self):
        """Test complete user signup and login-logout flow"""
        self.username = f"user_{os.urandom(4).hex()}"
        self.password = f"test_password{os.urandom(2).hex()}"
        # check name availability
        self.client.post("/check_username",json={"username":self.username})
        # signup user
        res_body = {"username":self.username,"password":self.password}
        self.client.post("/signup",json=res_body)
        # login
        self.client.post("/login",json=res_body)
        # logout
        self.client.get("/logout")

    @events.test_stop.add_listener
    def cleanup_database_engines(environment, **kwargs):
        """
        This runs ONCE on the Locust master process after the set
        test duration is over and all users have stopped
        """
        print("\n[CLEANUP] Load test finished. Disposing cached engines...")
        try:
            shutdown_sessions() 
            print("[CLEANUP] All test engines disposed successfully.")
        except Exception as e:
            print(f"[CLEANUP] Error during engine disposal: {e}")