import requests, unittest, sqlite3
import os, sys
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)
from backend.backend_constants import BackendPaths,CustomHeaders

TRUE_HEADER = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
TRUE_HEADER_RESPONSE = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value
TEST_PATH = BackendPaths.TEST_DATABASE_PATH.value

API_URL = "http://127.0.0.1:5000"

class TestAPI(unittest.TestCase):
    # helper to wrap assert call and print response body in case of failure
    def assertion_wrapper(self, response,expected_status:int):
        try:
            self.assertEqual(response.status_code,expected_status)
        except AssertionError as e:
            print("Response:",response.json())
            raise e
            
    def setUp(self): # standard naming for "unittest"
        self.session = requests.session()
        self.session.headers.update({TRUE_HEADER: TRUE_HEADER_RESPONSE})

        # setUp for attacker session
        self.hacker_session = requests.session()
        self.hacker_session.headers.update({TRUE_HEADER: "Fake-Header-Hacker"})

        conn = sqlite3.connect(TEST_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE if not exists user_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE,
        password TEXT,
        is_admin INTEGER NOT NULL DEFAULT 0
        )
        """)
        cursor.execute("DELETE FROM user_data") # start fresh
        conn.commit()
        conn.close()

    def test_signup_login_auth_flow(self):
        self.dummy_user_data = {"username":"dummyuser","password":"testPassword"}
        signup_data = self.dummy_user_data
        signup_request = self.session.post(f"{API_URL}/signup",json=signup_data)
        self.assertion_wrapper(signup_request,201)

        # login test
        login_data = self.dummy_user_data
        login_request = self.session.post(f"{API_URL}/login",json=login_data)
        self.assertion_wrapper(login_request,200)

        # extract the JWT
        login_response_data = login_request.json()
        token = login_response_data.get('access_token') # check if your key is 'token' or 'access_token'
        
        auth_headers = {"Authorization": f"Bearer {token}"}

        # auth test for delete
        user_data = {"username":self.dummy_user_data['username']}
        delete_request = self.session.delete(f"{API_URL}/api/users",json=user_data,headers=auth_headers)
        self.assertion_wrapper(delete_request,403)     

        # print custom responses to track test run
        print("\nSignup response:",signup_request.json())
        print("Login response:",login_request.json())
        print("Delete response:",delete_request.json())

    def test_malicious_attacker(self):
        # try signup with fake header
        self.dummy_user_data = {"username":"dummyuser","password":"testPassword"}
        signup_data = self.dummy_user_data
        signup_request = self.hacker_session.post(f"{API_URL}/signup",json=signup_data)
        self.assertion_wrapper(signup_request,403)

        # print custom responses to track test run
        print("Hacker Signup response:",signup_request.json())

if __name__ == "__main__":
    unittest.main()