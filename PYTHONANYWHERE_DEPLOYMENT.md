# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (Free or Paid)
- Git installed on PythonAnywhere
- Your GitHub repository URL

## Step-by-Step Deployment

### 1. Sign Up / Login to PythonAnywhere
- Go to https://www.pythonanywhere.com/
- Create a free account or login
- Go to Dashboard

### 2. Open a Bash Console
- Click on "Consoles" tab
- Start a new "Bash" console

### 3. Clone Your Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git college-network-security-idps
cd college-network-security-idps
```

### 4. Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Initialize Database and Admin User

```bash
python init_admin.py
```

This will create:
- Database at `database/idps.db`
- Admin user (username: admin, password: admin123)

### 7. Configure Web App

Go to the "Web" tab in PythonAnywhere Dashboard:

#### A. Create New Web App
- Click "Add a new web app"
- Choose "Manual configuration"
- Select "Python 3.10"

#### B. Configure Source Code
- **Source code:** `/home/YOUR_USERNAME/college-network-security-idps`
- **Working directory:** `/home/YOUR_USERNAME/college-network-security-idps`

#### C. Configure WSGI File
- Click on the WSGI configuration file link
- **Delete** all existing content
- **Paste** the following:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/college-network-security-idps'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from backend.api import app as application

# Configure session secret (generate a random one)
application.secret_key = 'REPLACE_WITH_RANDOM_SECRET_KEY'
```

**Replace:**
- `YOUR_USERNAME` with your PythonAnywhere username
- `REPLACE_WITH_RANDOM_SECRET_KEY` with a random string (generate one below)

#### D. Generate Secret Key
In Bash console, run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and use it as your secret key.

#### E. Configure Virtual Environment
In the "Web" tab, under "Virtualenv" section:
- **Virtualenv path:** `/home/YOUR_USERNAME/college-network-security-idps/venv`

#### F. Configure Static Files
In the "Web" tab, under "Static files" section, add:

| URL | Directory |
|-----|-----------|
| /static/ | /home/YOUR_USERNAME/college-network-security-idps/frontend |

### 8. Set Working Directory Permissions

```bash
chmod -R 755 ~/college-network-security-idps
chmod 666 ~/college-network-security-idps/database/idps.db
```

### 9. Reload Web App
- In the "Web" tab
- Click the green "Reload" button at the top

### 10. Access Your Application
- Your app will be available at: `https://YOUR_USERNAME.pythonanywhere.com`
- Login page: `https://YOUR_USERNAME.pythonanywhere.com/login`
- Use credentials: admin / admin123

## Important URLs

### Your Deployed Application
- **Landing Page:** `https://YOUR_USERNAME.pythonanywhere.com/`
- **Login:** `https://YOUR_USERNAME.pythonanywhere.com/login`
- **Dashboard:** `https://YOUR_USERNAME.pythonanywhere.com/dashboard`

## Configuration Updates Needed

### 1. Update Frontend API URLs
Since you're deploying to production, update `frontend/dashboard.js`:

```javascript
// Change this line:
const API_BASE_URL = 'http://localhost:5000/api';

// To:
const API_BASE_URL = '/api';
```

This makes the API calls relative to your domain.

### 2. Update CORS Settings
In `backend/api.py`, update CORS to allow your PythonAnywhere domain:

```python
# Update this line:
CORS(app, supports_credentials=True)

# To:
CORS(app, supports_credentials=True, origins=['https://YOUR_USERNAME.pythonanywhere.com'])
```

## Troubleshooting

### Error Logs
View error logs in PythonAnywhere:
- Go to "Web" tab
- Click on "Error log" link

### Common Issues

#### 1. 502 Bad Gateway
- Check WSGI file configuration
- Ensure virtual environment path is correct
- Reload the web app

#### 2. Database Errors
- Check database file permissions: `chmod 666 database/idps.db`
- Ensure database directory exists and is writable

#### 3. Static Files Not Loading
- Verify static files mapping in Web tab
- Check file paths are correct
- Clear browser cache

#### 4. Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment before installing
- Check Python version compatibility

#### 5. Session Errors
- Ensure secret_key is set in WSGI file
- Check session cookie settings

## Update Application

To update your deployed application:

```bash
cd ~/college-network-security-idps
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

Then reload the web app in the "Web" tab.

## Security Recommendations

### 1. Change Default Password
After first login, create a new admin user:
```bash
cd ~/college-network-security-idps
source venv/bin/activate
python
>>> from database.models import IDPSDatabase
>>> db = IDPSDatabase()
>>> db.create_user('newadmin', 'STRONG_PASSWORD', 'Admin Name', 'admin@example.com', 'admin')
>>> exit()
```

### 2. Use Environment Variables
For production, use environment variables for sensitive data:
```bash
export SECRET_KEY='your-secret-key'
export DATABASE_PATH='/path/to/database'
```

### 3. Enable HTTPS
PythonAnywhere automatically provides HTTPS for your domain.

### 4. Regular Backups
Backup your database regularly:
```bash
cp ~/college-network-security-idps/database/idps.db ~/backups/idps-$(date +%Y%m%d).db
```

## PythonAnywhere Free Account Limitations

- **Always-on tasks:** Not available (background processes won't run)
- **CPU seconds:** Limited per day
- **Bandwidth:** Limited
- **Custom domain:** Not available (use pythonanywhere.com subdomain)

For production use with background monitoring, consider upgrading to a paid account.

## Monitoring & Maintenance

### Check Application Status
```bash
# View recent access logs
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.access.log

# View error logs
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log
```

### Database Maintenance
```bash
cd ~/college-network-security-idps
source venv/bin/activate
python
>>> from database.models import IDPSDatabase
>>> db = IDPSDatabase()
>>> # Check database stats
>>> stats = db.get_dashboard_stats()
>>> print(stats)
```

## Production Checklist

- [ ] Repository cloned to PythonAnywhere
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Database initialized with admin user
- [ ] WSGI file configured with correct paths
- [ ] Secret key generated and set
- [ ] Static files mapped correctly
- [ ] Web app reloaded
- [ ] Application accessible at pythonanywhere.com URL
- [ ] Login working with admin credentials
- [ ] Dashboard loading correctly
- [ ] Default admin password changed
- [ ] Error logs checked for issues

## Support

If you encounter issues:
1. Check PythonAnywhere error logs
2. Verify all configuration files
3. Ensure virtual environment is activated
4. Review PythonAnywhere forums
5. Check application logs

## Next Steps

After successful deployment:
1. Change the default admin password
2. Add more admin users if needed
3. Populate with real threat data (if applicable)
4. Share your URL: `https://YOUR_USERNAME.pythonanywhere.com`
5. Monitor error logs regularly

---

**Your College Network Security IDPS is now deployed! 🎓🔒**
