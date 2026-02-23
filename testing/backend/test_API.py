import requests, unittest
import os, sys
os.environ['TESTING_MODE'] = 'True'
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)
from backend.backend_constants import BackendPaths,CustomHeaders
from backend.database_init import initialize_database
from backend.query_handler import shutdown_sessions
# constants
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
        initialize_database(test_mode=True)
        
    def tearDown(self):
        """Destructor hook, called after each test"""
        shutdown_sessions()

    def test_signup_login_auth_flow(self):
        self.dummy_user_data = {"username":"dummyuser","password":"testPassword"}
        signup_data = self.dummy_user_data
        signup_request = self.session.post(f"{API_URL}/signup",json=signup_data)
        self.assertion_wrapper(signup_request,201)

        # login test
        login_data = self.dummy_user_data
        login_request = self.session.post(f"{API_URL}/login",json=login_data)
        self.assertion_wrapper(login_request,200)

        # auth test for delete action
        user_data = {"username":self.dummy_user_data['username']}
        delete_request = self.session.delete(f"{API_URL}/api/users",json=user_data)
        self.assertion_wrapper(delete_request,403)

        # logout test for users
        logout_request = self.session.get(f"{API_URL}/logout")
        self.assertion_wrapper(logout_request,200)

        # print custom responses to track test run
        print("\nSignup response:",signup_request.json())
        print("Login response:",login_request.json())
        print("Delete response:",delete_request.json())
        print("Logout response:",logout_request.json())

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