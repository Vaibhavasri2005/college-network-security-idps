# IDPS Security Dashboard - Authentication Guide

## Overview

Your IDPS project has been transformed into a college-style website with **admin-only authentication**. The security dashboard is now protected and only accessible to authorized administrators.

## 🎓 College Website Features

### Landing Page (http://localhost:5000)
- **Professional college theme** with security-focused branding
- Information about the IDPS system capabilities
- "Administrator Access" button to login
- Features showcase and statistics

### Login System (http://localhost:5000/login)
- **Modern, secure login page** with college branding
- Beautiful gradient design with animations
- Real-time form validation
- Error handling with user-friendly messages
- **Admin-only access** - Only users with admin role can access dashboard

### Security Dashboard (http://localhost:5000/dashboard)
- **Protected by authentication** - Requires admin login
- Shows logged-in user's name in header
- Logout button with proper session termination
- All existing features (threat monitoring, charts, etc.)

## 🔐 Default Admin Credentials

**Username:** `admin`  
**Password:** `admin123`

⚠️ **IMPORTANT:** Change the default password after first login!

## 🚀 How to Use

### 1. Start the Server

```powershell
cd "C:\Users\vaibhava sri\Documents\IDS project"
python backend\api.py
```

The server will start on http://localhost:5000

### 2. Access the System

1. **Open your browser** and navigate to: http://localhost:5000
2. You'll see the **college landing page** with information about the IDPS
3. Click **"Administrator Access"** button
4. **Login** with the default credentials:
   - Username: `admin`
   - Password: `admin123`
5. You'll be redirected to the **security dashboard**

### 3. Using the Dashboard

- View real-time security threats and statistics
- Monitor blocked IPs and attacker activities
- See your username displayed in the header
- Click **"Logout"** button to end your session

## 🔒 Security Features

### Authentication System

1. **Session-Based Authentication**
   - Secure Flask sessions with secret key
   - Sessions persist across page refreshes
   - Auto-redirects to login if not authenticated

2. **Role-Based Access Control**
   - Only users with `admin` role can access dashboard
   - Non-admin users see "Admin access required" error
   - All API endpoints protected with `@admin_required` decorator

3. **Access Protection**
   - `/dashboard` - Requires admin login
   - `/api/*` - All API endpoints require admin authentication
   - `/login` - Public access (redirects to dashboard if already logged in)
   - `/` - Public landing page

### Database Security

- Passwords are hashed using SHA-256
- User table stores: username, password_hash, role, email, full_name
- Session cookies are HTTPOnly and secure

## 📊 User Management

### Creating Additional Admin Users

Run this Python script to create new admin users:

```python
from database.models import IDPSDatabase

db = IDPSDatabase()
db.create_user(
    username="newadmin",
    password="securepassword",
    full_name="Admin Name",
    email="admin@college.edu",
    role="admin"
)
```

### Creating Regular Users

Regular users can be created but **cannot access the dashboard**:

```python
db.create_user(
    username="user1",
    password="userpass",
    full_name="Regular User",
    email="user@college.edu",
    role="user"  # Regular users can't access dashboard
)
```

## 🎨 UI Design

### College Website Theme

- **Colors:**
  - Primary Blue: #1e40af
  - Purple Accent: #7c3aed
  - Gold Accent: #f59e0b
  - Dark Background: #0f172a

- **Features:**
  - Gradient backgrounds
  - Floating animations
  - Smooth transitions
  - Modern card designs
  - Responsive layout

### Login Page

- Professional authentication form
- College branding with shield logo
- Information cards about system features
- Error/success message handling
- Loading states during login

### Dashboard

- Updated header with user info
- Styled logout button
- Maintains all original IDPS features
- Modern indigo/purple theme from before

## 🔄 Authentication Flow

```
User visits http://localhost:5000
    ↓
Landing Page displayed
    ↓
Click "Administrator Access"
    ↓
Redirected to /login
    ↓
Enter credentials (admin/admin123)
    ↓
Server validates credentials
    ↓
[If invalid] Show error message
[If valid but not admin] Show "Admin access required"
[If valid admin] Create session → Redirect to /dashboard
    ↓
Dashboard accessible with all features
    ↓
Click "Logout" → Clear session → Back to /login
```

## 🛠️ Technical Details

### New Files Added

1. **frontend/login.html** - Admin login page
2. **frontend/login-styles.css** - Login page styling
3. **frontend/login.js** - Login form handler
4. **frontend/home.html** - College landing page
5. **init_admin.py** - Script to create default admin user

### Modified Files

1. **database/schema.sql** - Added users table
2. **database/models.py** - Added authentication methods
3. **backend/api.py** - Added session management, auth routes, protected endpoints
4. **frontend/index.html** - Added logout button and user info
5. **frontend/styles.css** - Added logout button styling
6. **frontend/dashboard.js** - Added auth check and logout functionality

### New Database Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 📝 API Endpoints

### Public Endpoints
- `GET /` - Landing page
- `GET /login` - Login page
- `POST /api/auth/login` - Login endpoint
- `GET /api/health` - Health check

### Protected Endpoints (Admin Only)
- `GET /dashboard` - Security dashboard
- `GET /api/auth/check` - Check authentication
- `POST /api/auth/logout` - Logout
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/threats` - Get threats
- `GET /api/threats/timeline` - Threat timeline
- `GET /api/threats/statistics` - Threat statistics
- `GET /api/threats/top-attackers` - Top attackers
- `GET /api/blocked-ips` - Blocked IPs
- `DELETE /api/blocked-ips/<ip>` - Unblock IP
- `GET /api/events` - System events
- `GET /api/search` - Search threats

## 🎯 Next Steps

1. **Change Default Password**
   - Login as admin
   - Use the create_user method to update password

2. **Deploy to Production**
   - Use a production WSGI server (gunicorn, waitress)
   - Enable HTTPS for secure connections
   - Use stronger secret key for sessions
   - Implement password reset functionality

3. **Enhance Security**
   - Add password complexity requirements
   - Implement account lockout after failed attempts
   - Add two-factor authentication
   - Implement password change functionality

## 🆘 Troubleshooting

### Can't Login
- Verify admin user exists: Run `python init_admin.py` again
- Check credentials: Username: `admin`, Password: `admin123`
- Check browser console for error messages

### Session Issues
- Clear browser cookies/cache
- Restart the Flask server
- Check if secret_key is set in api.py

### Authorization Errors
- Ensure user has `admin` role in database
- Check server logs for authentication errors
- Verify session is being created properly

## 📧 Support

For issues or questions, check the server logs for detailed error messages.

---

**Your IDPS is now a professional college-style security dashboard with admin-only access!** 🎓🔒
