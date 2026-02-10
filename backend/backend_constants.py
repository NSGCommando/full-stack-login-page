# file paths, using Enum as super to enforce immutability, prevents overwriting
from enum import Enum
import os

class BackendPaths(Enum):
    """
    Class to store all path constants related to Backend
    """
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database.db") # save the database path
    TEST_DATABASE_PATH = os.path.join(os.path.dirname(__file__), "test_db.db") # save the test database file

class CustomHeaders(Enum):
    """
    Class to store all custom headers/custom tags
    Must match with the frontend constants
    """
    CUSTOM_HEADER_FRONTEND="R-Application-Service"
    CUSTOM_HEADER_FRONTEND_RESPONSE="Frontend-Service-R"