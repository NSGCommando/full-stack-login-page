# Login Page Demo #

## Architecture ##
- Backend
  - Python (Flask) for stateless API and server-side routing (data)
  - Sqlite3 for database and SQL querying
  - Queries are parameterized to prevent arbitrary SQL injection
- Frontend
  - React.js for page renderer and client-side routing (URLs)
  - Vite to bundle React.js components and run frontend server
- Authentication and Authorisation
  - User authentication done via JWT stored client-side for stateless backend
  - JWTs are stored in HTTP only cookies to prevent token theft via cross-site scripting(XSS) attacks
  - Tokens set the cookie's SameSite setting to Lax to ensure the cookie isn't attached to cross-site request forgery(CSRF) attacks
  - Authorisation is database-backed
  - In the case of Admin aactions, even if user is authenticated, backend will query database for role data to ensure authorisation for the action
  - Trades off some performance for up-to-date role data and prevents stale authorisation data

## Initial Setup ##
- There is a file called ```.env.example``` with example admin details
- Rename it to ```.env``` and change the admin username and password to whatever you want
- Since ```test_db.db``` doesn't exist at first, run ```database_init.bat``` batch file to generate the database; the script adds your admin details to the database

## Testing The Backend API ##
- There is now a batch file in root called ```test_API.bat```
- Run the file to test sign-up, login, and unauthorised delete calls to the API
- The environment for normal running was cloned and configured to point to a testing database
- The batch file explicitly sets ```TESTING_MODE``` to True, and the ```data_conn``` decorator reads the value to change the filepath to the testing database, so any actual data isn't impacted
 
## Run Backend and Frontend Servers ##
- Run both servers from ```run_app.bat``` batch file
- Vite server renders React.js on ```localhost:5173```
- Flask API server runs on ```localhost:5000```

## Future Plans ##
- Switch Database from SQLite3 to PostGreSQL (runs on another server like Vite and Flask)
