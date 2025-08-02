# Kwantum Institute - Authentication System

A comprehensive authentication system for the Kwantum Institute website, featuring Django backend with REST API and React frontend integration.

## Features

### Backend (Django)
- **User Authentication**: Login, registration, logout
- **User Profiles**: Extended user information with bio, avatar, phone number
- **Password Management**: Change password, reset password via email
- **Security Features**: Login attempt tracking, token-based authentication
- **Admin Interface**: Full Django admin integration
- **API Endpoints**: RESTful API for frontend integration
- **CORS Support**: Cross-origin resource sharing for frontend communication

### Frontend (React)
- **Authentication Context**: Global state management for user authentication
- **Login/Register Forms**: Modern, responsive forms with validation
- **Profile Management**: User profile editing and management
- **Protected Routes**: Route protection based on authentication status
- **User Menu**: Dropdown menu with profile and logout options
- **Responsive Design**: Mobile-friendly interface

## Project Structure

```
kwantum-institute.github.io-main/
├── backend/
│   ├── authentication/          # Django authentication app
│   │   ├── models.py           # User models (UserProfile, LoginAttempt, etc.)
│   │   ├── views.py            # API views for authentication
│   │   ├── serializers.py      # Data serialization
│   │   ├── urls.py             # URL routing
│   │   ├── admin.py            # Django admin configuration
│   │   └── signals.py          # Signal handlers
│   ├── backend/                # Django project settings
│   │   ├── settings.py         # Project configuration
│   │   ├── urls.py             # Main URL routing
│   │   └── ...
│   ├── manage.py               # Django management script
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthContext.jsx # Authentication context provider
│   │   │   ├── LoginForm.jsx   # Login form component
│   │   │   ├── RegisterForm.jsx # Registration form component
│   │   │   ├── AuthForms.css   # Authentication form styles
│   │   │   └── Navbar.jsx      # Navigation with auth integration
│   │   ├── pages/
│   │   │   ├── Login.jsx       # Login page
│   │   │   ├── Profile.jsx     # Profile management page
│   │   │   └── Profile.css     # Profile page styles
│   │   └── App.jsx             # Main app with auth routes
│   └── ...
└── README.md                   # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration
- `GET /api/auth/check-auth/` - Check authentication status
- `GET /api/auth/user-info/` - Get current user information

### Profile Management
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile

### Password Management
- `POST /api/auth/password/change/` - Change password
- `POST /api/auth/password/reset/` - Request password reset
- `POST /api/auth/password/reset/confirm/` - Confirm password reset

## Usage

### User Registration
1. Navigate to `/login` and click "Sign up"
2. Fill in the registration form with your details
3. Submit the form to create your account
4. You'll be automatically logged in after successful registration

### User Login
1. Navigate to `/login`
2. Enter your username and password
3. Click "Sign In" to access your account

### Profile Management
1. Click on your user avatar in the navigation bar
2. Select "Profile Settings"
3. Edit your profile information, change password, or manage account settings

### Logout
1. Click on your user avatar in the navigation bar
2. Select "Sign Out" from the dropdown menu

## Security Features

- **Password Validation**: Strong password requirements
- **Login Attempt Tracking**: Monitor failed login attempts
- **Token-based Authentication**: Secure API access
- **CORS Protection**: Configured for secure cross-origin requests
- **Session Management**: Secure session handling
- **Password Reset**: Email-based password reset functionality

## Development

### Adding New Features
1. **Backend**: Add new models, views, and serializers in the `authentication` app
2. **Frontend**: Create new components and integrate with the AuthContext
3. **Testing**: Add tests for new functionality

### Customization
- **Styling**: Modify CSS files in the frontend for custom styling
- **Validation**: Update form validation in both frontend and backend
- **Email Templates**: Customize password reset email templates
- **Admin Interface**: Extend Django admin for additional functionality

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend CORS settings include your frontend URL
2. **Database Errors**: Run migrations if you encounter database-related errors
3. **Authentication Issues**: Check that tokens are being properly stored and sent
4. **Email Issues**: Configure email settings in Django for password reset functionality

### Debug Mode
- Backend: Set `DEBUG = True` in `settings.py` for detailed error messages
- Frontend: Check browser console for JavaScript errors

## Production Deployment

### Backend
1. Set `DEBUG = False` in production settings
2. Configure a production database (PostgreSQL recommended)
3. Set up proper email configuration
4. Use environment variables for sensitive settings
5. Configure static file serving

### Frontend
1. Build the production version: `npm run build`
2. Serve static files from a web server
3. Configure environment variables for API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the Kwantum Institute website. Please refer to the main project license for usage terms.