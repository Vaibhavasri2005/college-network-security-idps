# 🚀 Quick Start Guide - IDPS College Security Dashboard

## What You Have Now

Your IDPS project is now a **college-style website** with **admin-only security dashboard**!

## 🎯 3-Step Setup

### Step 1: Start the Server
```powershell
cd "C:\Users\vaibhava sri\Documents\IDS project"
python backend\api.py
```

### Step 2: Open Browser
Navigate to: **http://localhost:5000**

### Step 3: Login as Admin
- Click **"Administrator Access"** on the landing page
- **Username:** `admin`
- **Password:** `admin123`

## 🎨 What You'll See

### 1️⃣ Landing Page (http://localhost:5000)
- Professional college-themed homepage
- Shield logo with floating animation
- "College Network Security System" branding
- Features showcase with icons
- Statistics bar (24/7, Real-time, Auto)
- "Administrator Access" button

### 2️⃣ Login Page (http://localhost:5000/login)
- Modern gradient design
- College logo and branding
- Username and password fields
- Sign In button with loading animation
- Security warning footer
- Information cards about features

### 3️⃣ Security Dashboard (http://localhost:5000/dashboard)
- **Header:** Shows "College Network Security - IDPS Dashboard"
- **User Info:** Displays "System Administrator"
- **Logout Button:** Red gradient button with icon
- **All IDPS Features:**
  - Threat statistics cards
  - Timeline chart
  - Severity distribution chart
  - Recent threats table
  - Top attackers list
  - Blocked IPs table

## 🔒 Security Features

✅ **Admin-Only Access** - Only administrators can view the dashboard  
✅ **Session Management** - Secure login sessions  
✅ **Auto-Redirect** - Redirects to login if not authenticated  
✅ **Protected API** - All endpoints require authentication  
✅ **Logout Function** - Properly terminates sessions  

## 📱 Testing the System

### Test Authentication
1. Try accessing http://localhost:5000/dashboard directly
   - **Result:** Should redirect to login page
2. Login with wrong credentials
   - **Result:** Shows error message
3. Login with correct credentials (admin/admin123)
   - **Result:** Redirects to dashboard
4. Click Logout button
   - **Result:** Returns to login page

### Test Dashboard
1. After logging in, view all statistics
2. Check threat charts are loading
3. Verify recent threats table
4. Check blocked IPs list
5. Confirm auto-refresh works (every 30 seconds)

## 📊 Default Data

The database already has **48 sample threats** from the previous demo:
- Various threat types (SQL Injection, Port Scan, DDoS, etc.)
- Different severity levels (Critical, High, Medium, Low)
- 10 blocked IPs
- Timestamps spread across last 24 hours

## 🎓 College Theme Design

**Colors:**
- Primary Blue (#1e40af) - Professional & trustworthy
- Purple Accent (#7c3aed) - Modern & tech-savvy
- Gold Accent (#f59e0b) - Academic excellence
- Dark Background (#0f172a) - Security-focused

**Animations:**
- Floating shield logo
- Bouncing feature icons
- Hover effects on buttons
- Gradient transitions
- Loading spinners

## ⚠️ Important Notes

1. **Default Password**
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ Change this after first login!

2. **Development Server**
   - Currently using Flask development server
   - For production, use gunicorn or waitress

3. **Database**
   - SQLite database at `database/idps.db`
   - Contains 48 sample threats
   - 1 admin user account

## 🆘 Troubleshooting

**Can't access localhost:5000?**
- Check if server is running: `python backend\api.py`
- Look for "Running on http://127.0.0.1:5000"

**Login not working?**
- Verify credentials: admin / admin123
- Run `python init_admin.py` again if needed
- Check browser console (F12) for errors

**Dashboard showing errors?**
- Clear browser cache (Ctrl+F5)
- Check server terminal for error messages
- Restart the server

**API returning 401 errors?**
- You're not logged in
- Login again at http://localhost:5000/login

## 📖 More Information

- **AUTHENTICATION_GUIDE.md** - Complete authentication documentation
- **TRANSFORMATION_SUMMARY.md** - All changes made to the project
- **DASHBOARD_GUIDE.md** - Original dashboard usage guide

## 🎉 You're Ready!

Your college-style IDPS security dashboard is now fully operational with:
- ✅ Professional landing page
- ✅ Secure admin login
- ✅ Protected dashboard
- ✅ Modern UI design
- ✅ Real-time threat monitoring

**Open http://localhost:5000 and explore your new security system!** 🎓🔒
