# Quick Start Guide

## Option 1: Automatic Startup (Recommended)

Double-click `start-dev.bat` to automatically start both servers.

## Option 2: Manual Startup

### Backend (Django)

1. **Open Command Prompt/Terminal**
2. **Navigate to backend folder:**
   ```bash
   cd "D:\KwantumInstitute\kwantum-institute.github.io-main\kwantum-institute.github.io-main\backend"
   ```

3. **Activate virtual environment:**
   ```bash
   venv\Scripts\activate
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

**Backend will be available at:** `http://localhost:8000`

### Frontend (React)

1. **Open a NEW Command Prompt/Terminal**
2. **Navigate to frontend folder:**
   ```bash
   cd "D:\KwantumInstitute\kwantum-institute.github.io-main\kwantum-institute.github.io-main\frontend"
   ```

3. **Install dependencies (first time only):**
   ```bash
   npm install
   ```

4. **Start React server:**
   ```bash
   npm start
   ```

**Frontend will be available at:** `http://localhost:3000` or `http://localhost:5173`

## Testing the System

1. **Open your browser** and go to `http://localhost:3000` (or `http://localhost:5173`)
2. **Click "Sign In"** in the top-right corner
3. **Register a new account** or login with existing credentials
4. **Test the authentication system**

## Troubleshooting

### If Django shows "No module named 'rest_framework'":
- Make sure you're in the virtual environment: `venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

### If npm shows "Missing script: start":
- Make sure you're in the frontend directory
- Run: `npm install` first

### If ports are already in use:
- Django: Change port in `python manage.py runserver 8001`
- React: It will automatically suggest an alternative port

## Admin Access

- **Django Admin:** `http://localhost:8000/admin/`
- **Create superuser:** `python manage.py createsuperuser`

## API Endpoints

- **Login:** `POST http://localhost:8000/api/auth/login/`
- **Register:** `POST http://localhost:8000/api/auth/register/`
- **Profile:** `GET http://localhost:8000/api/auth/profile/`
- **Check Auth:** `GET http://localhost:8000/api/auth/check-auth/` 