@echo off
echo Starting Kwantum Institute Development Environment...
echo.

echo Starting Django Backend Server...
cd backend
start "Django Backend" cmd /k "python manage.py runserver"

echo.
echo Starting React Frontend Server...
cd ..\frontend
start "React Frontend" cmd /k "npm start"

echo.
echo Development servers are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to exit this script...
pause > nul 