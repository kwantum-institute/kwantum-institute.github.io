#!/bin/bash

echo "Starting Kwantum Institute Development Environment..."
echo

echo "Starting Django Backend Server..."
cd backend
gnome-terminal --title="Django Backend" -- bash -c "python manage.py runserver; exec bash" &

echo
echo "Starting React Frontend Server..."
cd ../frontend
gnome-terminal --title="React Frontend" -- bash -c "npm start; exec bash" &

echo
echo "Development servers are starting..."
echo "Backend will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:3000"
echo
echo "Press Ctrl+C to stop all servers"
wait 