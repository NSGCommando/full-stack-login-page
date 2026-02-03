@echo off
REM: Works only for Windows, for now
REM: Start Backend (Flask) server in new terminal:
start cmd /k ".venv\Scripts\activate.bat && flask --app backend/my_react_app:application run"
REM: Start Frontend (Vite) server this terminal:
npm run dev --prefix frontend