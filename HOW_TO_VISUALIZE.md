# IDPS Web Dashboard - Complete Visualization System

## 🎨 What You Can See Now

Your IDPS project now includes a **beautiful web dashboard** where you can visualize all threats, attacks, and security events in real-time!

### Dashboard URL
```
http://localhost:5000
```

## 📊 Dashboard Features

### 1. **Real-Time Statistics Cards**
At the top of the dashboard, you'll see 4 key metrics:
- **Threats Today**: Number of threats detected in the last 24 hours
- **Blocked IPs**: Currently active IP blocks
- **Critical Threats**: High/Critical severity threats today
- **Total Threats**: All-time threat count

### 2. **Interactive Charts**

**Threat Timeline (24 Hours)**
- Line chart showing threat frequency over the last 24 hours
- Color-coded by severity (Green=Low, Orange=Medium, Red=High, Dark Red=Critical)
- Updates automatically every 30 seconds

**Threats by Severity**
- Pie/Donut chart showing distribution of threat severities
- Helps identify if you're under heavy attack or just normal probing

### 3. **Recent Threats Table**
- Shows the 50 most recent threats
- Filterable by severity level
- Displays:
  - Timestamp
  - Threat type (brute_force, port_scan, etc.)
  - Attacker IP address
  - Severity badge with color coding
  - Threat details
  - Block status (Blocked/Detected)

### 4. **Top Attackers Section**
- Lists the 10 most active attacker IPs
- Shows:
  - Total attack count per IP
  - Maximum severity reached
  - Last time they were seen
- Helps identify persistent threats

### 5. **Blocked IPs Management**
- Shows all currently blocked IPs
- Displays block reason and timestamp
- **Unblock Button**: Click to remove IP from block list
- Real-time updates when IPs are blocked/unblocked

## 🗄️ Database Structure

All data is stored in **SQLite database** at `database/idps.db`:

```
📁 database/
  ├── idps.db          ← SQLite database file
  ├── schema.sql       ← Database schema definition
  └── models.py        ← Python ORM models
```

### Tables Created:
1. **threats** - All detected threats
2. **blocked_ips** - Currently blocked IP addresses
3. **system_events** - System activity log
4. **alert_history** - Alert delivery tracking
5. **statistics** - Aggregated statistics
6. **ip_lists** - Whitelist/Blacklist management

## 🔄 How It Works (Complete Flow)

### Visual Flow Diagram:

```
Attacker
   ↓
[1] Login Attempt Logged → /var/log/auth.log
   ↓
[2] monitor.py reads logs → log_analyzer.py parses events
   ↓
[3] threat_detector.py detects pattern → Identifies brute force
   ↓
[4] monitor.py stores in DATABASE
   │   - Adds to threats table
   │   - Creates system event
   │   - Updates statistics
   ↓
[5] If threshold exceeded → IP gets blocked
   │   - Added to blocked_ips table
   │   - Firewall rule applied
   │   - System event logged
   ↓
[6] alert_sender.py sends notifications
   │   - Email to admin
   │   - Slack message
   │   - Telegram alert
   │   - Logged in alert_history table
   ↓
[7] DASHBOARD displays everything in real-time
   │   - Statistics update
   │   - Charts refresh
   │   - Threat table updates
   │   - Blocked IPs list updated
   ↓
[8] Admin sees attack → Can unblock IP if false positive
```

### Real-Time Visualization Flow:

```
Frontend (Browser)
   ↓ (HTTP GET requests every 30s)
Backend API (Flask)
   ↓ (SQL queries)
Database (SQLite)
   ↓ (Returns JSON data)
Backend API
   ↓ (JSON response)
Frontend renders charts & tables
```

## 🚀 How to Use

### Step 1: Generate Demo Data (Already Done!)
```bash
python windows_demo_with_db.py
```
This populates the database with sample threats.

### Step 2: Start API Server (Already Running!)
```bash
cd backend
python api.py
```

### Step 3: Open Dashboard (Already Open!)
Navigate to: http://localhost:5000

### Step 4: Explore the Dashboard
- ✅ See real-time statistics at the top
- ✅ Examine the threat timeline chart
- ✅ Filter threats by severity
- ✅ Identify top attackers
- ✅ Try unblocking an IP

## 🎮 Interactive Features

### Filter Threats by Severity
1. Click the "All Severities" dropdown in the threats section
2. Select: Low, Medium, High, or Critical
3. Table updates instantly

### Unblock an IP Address
1. Scroll to "Currently Blocked IPs" section
2. Find the IP you want to unblock
3. Click the red "Unblock" button
4. Confirm the action
5. IP is removed from block list
6. Statistics update automatically

### Manual Refresh
Click the "🔄 Refresh" button anytime to update all data immediately.

### Auto-Refresh
Dashboard refreshes automatically every 30 seconds (can be customized in `frontend/dashboard.js`).

## 📡 API Endpoints (For Developers)

The backend exposes these REST API endpoints:

```
GET /api/health
    ↳ Returns: {"status": "healthy", "service": "IDPS API"}

GET /api/dashboard/stats
    ↳ Returns: Dashboard statistics (threats_today, blocked_ips, etc.)

GET /api/threats?limit=50&severity=HIGH
    ↳ Returns: List of threats (filterable)

GET /api/threats/timeline?hours=24
    ↳ Returns: Hourly threat counts for charts

GET /api/threats/top-attackers?limit=10
    ↳ Returns: Most active attacker IPs

GET /api/blocked-ips
    ↳ Returns: All currently blocked IPs

DELETE /api/blocked-ips/<ip_address>
    ↳ Unblocks the specified IP address

GET /api/events?limit=100
    ↳ Returns: Recent system events

GET /api/search?q=192.168.1.100
    ↳ Searches threats by IP or keywords
```

### Example API Call:
```bash
# Get dashboard stats
curl http://localhost:5000/api/dashboard/stats

# Get recent threats
curl http://localhost:5000/api/threats?limit=10

# Unblock an IP
curl -X DELETE http://localhost:5000/api/blocked-ips/192.168.1.100
```

## 🎨 Customization

### Change Colors
Edit `frontend/styles.css`:
```css
:root {
    --primary-color: #2563eb;    /* Blue */
    --danger-color: #dc2626;     /* Red */
    --warning-color: #f59e0b;    /* Orange */
    --success-color: #10b981;    /* Green */
}
```

### Change Refresh Rate
Edit `frontend/dashboard.js` line 9:
```javascript
setInterval(refreshData, 30000);  // 30 seconds
```

### Add More Charts
Add new Chart.js visualizations in `frontend/dashboard.js`:
```javascript
// Example: Add attack types pie chart
function loadAttackTypesChart() {
    const ctx = document.getElementById('attackTypesChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: { /* your data */ }
    });
}
```

## 📱 Screenshots (What You'll See)

### Dashboard View
```
┌─────────────────────────────────────────────────────┐
│  🛡️  IDPS Security Dashboard      ● System Active  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐            │
│  │ 🚨 48│  │ 🚫 10│  │ ⚠️ 21 │  │ 📊 48│            │
│  │Threats│  │Blocked│  │Critical│ │Total │            │
│  └──────┘  └──────┘  └──────┘  └──────┘            │
│                                                       │
│  📈 Threat Timeline        📊 Severity Distribution  │
│  ┌────────────────┐        ┌────────────────┐       │
│  │  [Line Chart]  │        │  [Pie Chart]   │       │
│  └────────────────┘        └────────────────┘       │
│                                                       │
│  Recent Threats                          [🔄 Refresh]│
│  ┌───────────────────────────────────────────────┐  │
│  │Time     │Type        │IP           │Severity  │  │
│  │15:02:23 │brute_force │192.168.1.100│🔴 HIGH   │  │
│  │15:02:21 │invalid_user│192.168.1.100│🟡 MEDIUM │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 🔧 Troubleshooting

### Dashboard shows "No threats detected"
**Solution**: Run the demo to generate data:
```bash
python windows_demo_with_db.py
```

### API not responding
**Solution**: Check if the API server is running:
```bash
curl http://localhost:5000/api/health
```

### Port 5000 already in use
**Solution**: Change the port in `backend/api.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Charts not displaying
**Solution**: 
1. Check browser console for errors (F12)
2. Verify Chart.js CDN is loaded
3. Ensure API is returning data

### CORS errors in browser
**Solution**: Make sure flask-cors is installed:
```bash
pip install flask-cors
```

## 🎯 Production Deployment

For deploying to Ubuntu server:

1. **Install packages**:
```bash
pip3 install -r requirements.txt
```

2. **Use Gunicorn** (production WSGI server):
```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.api:app
```

3. **Setup Nginx** reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Add authentication** (recommended):
- Use Flask-Login for session management
- Add JWT tokens for API security
- Implement user roles (admin/viewer)

## 🎓 Learning Points

**Database Storage**: All threats are permanently stored and queryable
**RESTful API**: Clean API design for future integrations
**Responsive Design**: Dashboard works on mobile/tablet/desktop
**Real-time Updates**: Auto-refresh keeps data current
**Interactive**: Click to unblock IPs, filter threats, etc.

## 🔐 Security Recommendations

For production use:
1. ✅ Add user authentication
2. ✅ Use HTTPS (SSL certificates)
3. ✅ Restrict API access by IP
4. ✅ Use PostgreSQL for better performance
5. ✅ Enable rate limiting on API endpoints
6. ✅ Regular database backups

---

**You now have a complete IDPS with full visualization!** 🎉

The dashboard at http://localhost:5000 shows you exactly what threats are detected, when they happen, and lets you manage blocked IPs with just a click!
