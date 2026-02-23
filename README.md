# Web App Demo #

## Architecture ##
- Built as a Single Page Application (SPA) using a Flask REST API backend
- Backend
  - Python (Flask) for stateless API and server-side routing (data)
  - Sqlite3 for database and SQL querying via SQLAlchemy
- Frontend
  - React.js for page renderer and client-side routing (URLs)
  - Vite to bundle React.js components and run frontend server
- Authentication and Authorisation
  - User authentication done via JWT stored client-side for stateless backend
  - JWTs are stored in HTTP only cookies to prevent token theft via cross-site scripting(XSS) attacks
  - Logout request from client-side prompts the server to delete the associated JWT cookie
  - Tokens set the cookie's SameSite setting to Lax to ensure the cookie isn't attached to cross-site request forgery(CSRF) attacks
  - Backend also expects a custom header and header value (set inside ```backend_constants.py```) to accept any requests; this further hardens the app against CSRF attacks.
  - CORS is set up to accept that particular custom header alongside the default ```Content-Type``` header
  - In the case of Admin actions, even if user is authenticated, backend will query database for role data to ensure authorisation for the action
  - Trades off some performance for up-to-date role data and prevents stale authorisation data
  - On frontend, basic username and password restrictions have been set up using HTML5 regex patterns
  - App.jsx is handler for client-side auth and the source of truth for relevant user data, no data is additionally passed to navigation objects
  - SQLAlchemy is used to ensure the app is database-agnostic and allows easy switching of database platforms, as well as query abstraction (for type safety and forced parameterization to prevent SQL Injection
  - Uses SQLite's Write Ahead Logging (WAL) mode to allow concurrent database access, significantly reducing errors during future high-load situations and allowing easy scalability

## Initial Setup ##
- There is a file called ```.env.example``` with example admin details
- Rename it to ```.env``` and change the admin username and password to whatever you want
- Since the database doesn't exist at first, run ```database_init.bat``` batch file to generate the database; the script adds your admin details to the database

## Testing The Backend API ##
- ```test_API.bat``` is the Backend API integration tester
  - Run the file to test sign-up, login, logout and unauthorised delete calls to the API
- ```test_API_load.bat``` is the Backend API load tester
  - Run the file to do initial load test for baseline stats, with 10 peak users, ramp up of 2 users and each user creating and logging into a new account every 3-6 seconds
- The environment for normal running is cloned and configured to point to a testing database
- The batch files explicitly set ```TESTING_MODE``` to True, and the ```data_conn``` decorator reads the value to change the filepath to the testing database, so any actual data isn't impacted
- Integration test file consists of a "normal" session, with correct headers and requests, and an "attacker" session where the header is fake
 
## Run Backend and Frontend Servers ##
- Run both servers from ```run_app.bat``` batch file
- Vite server renders React.js on ```localhost:5173```
- Flask API server runs on ```localhost:5000```

## Future Plans ##
- Switch Database from SQLite3 to PostGreSQL (Easier now that SQLAlchemy is used to decouple backend API from database platform)
