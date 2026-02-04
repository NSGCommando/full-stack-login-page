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
- Since ```test_db.db``` doesn't exist at first, run ```database_init.bat``` batch file to generate the database, and add your admin details to it
 
## Run Backend and Frontend Servers ##
- Run both servers from ```run_app.bat``` batch file
- Vite server renders React.js on ```localhost:5173```
- Flask API server runs on ```localhost:5000```

## Future Plans ##
- Implement Admin Dashboard showing user ids and names with ability to delete users or reset password for users
- Switch Database from SQLite3 to PostGreSQL (runs on another server like Vite and Flask)
- Look into JWTs for auth
