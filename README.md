# Login Page Demo #

## Architecture ##
- Backend
  - Python (Flask) for stateless API and server-side routing (data)
  - Sqlite3 for database and SQL querying
- Frontend
  - React.js for page renderer and client-side routing (URLs)
  - Vite to bundle React.js components and run frontend server

## Initial Setup ##
- There is a file called ```.env.example``` with example admin details
- Rename it to ```.env``` and change the admin username and password to whatever you want
- If ```test_db.db``` doesn't exist, run ```database_init.bat``` batch file to generate the database, and add your admin details to it
 
## Run Backend and Frontend Servers ##
- Run both servers from ```run_app.bat``` batch file
- Vite server renders React.js on ```localhost:5173```
- Flask API server runs on ```localhost:5000```
