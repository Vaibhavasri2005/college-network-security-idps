# IDPS Dashboard - Quick Start Guide

## 🚀 Running the Dashboard

The IDPS now includes a beautiful web dashboard to visualize all threats, blocked IPs, and system statistics in real-time!

### Prerequisites

1. **Install Python packages:**
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install flask flask-cors pyyaml requests
```

### Starting the Dashboard

#### Option 1: Using the Windows Demo (For Testing)

1. **Generate Demo Data:**
```bash
python windows_demo_with_db.py
```
This will simulate attacks and populate the database with sample data.

2. **Start the API Server:**
```bash
cd backend
python api.py
```

3. **Open Dashboard:**
Open your browser and navigate to:
```
http://localhost:5000
```

#### Option 2: On Ubuntu Server (Production)

1. **Install IDPS (if not already done):**
```bash
sudo ./scripts/install.sh
```

2. **Start the API server:**
```bash
cd /opt/idps/backend
python3 api.py
```

Or run as a service (recommended):
```bash
sudo systemctl start idps-api
sudo systemctl enable idps-api
```

3. **Access Dashboard:**
```
http://your-server-ip:5000
```

### Dashboard Features

✅ **Real-Time Statistics**
- Threats detected today
- Currently blocked IPs
- Critical threats count
- Total threats all-time

✅ **Interactive Charts**
- 24-hour threat timeline
- Threats by severity (pie chart)
- Hourly attack patterns

✅ **Threat Management**
- View all recent threats
- Filter by severity (Low/Medium/High/Critical)
- Search by IP address
- Auto-refresh every 30 seconds

✅ **Blocked IP Management**
- See all currently blocked IPs
- Unblock IPs with one click
- View block reason and timestamp

✅ **Top Attackers**
- Most active attacker IPs
- Attack frequency statistics
- Maximum severity levels

### API Endpoints

The backend provides a REST API:

```
GET  /api/health                 - Health check
GET  /api/dashboard/stats        - Dashboard statistics
GET  /api/threats                - List all threats
GET  /api/threats/timeline       - Threat timeline data
GET  /api/threats/top-attackers  - Top attacking IPs
GET  /api/blocked-ips            - Currently blocked IPs
DELETE /api/blocked-ips/<ip>     - Unblock an IP
GET  /api/events                 - System events
GET  /api/search?q=<query>       - Search threats
```

### Database

The system uses SQLite by default:
- Database location: `database/idps.db`
- Stores threats, blocked IPs, events, and statistics
- No external database server required

For production with high traffic, consider PostgreSQL:
1. Uncomment `psycopg2-binary` in requirements.txt
2. Modify `database/models.py` connection string

### Troubleshooting

**Port 5000 already in use?**
```bash
# Change port in backend/api.py line 168
app.run(host='0.0.0.0', port=8080)
```

**CORS errors?**
- Ensure flask-cors is installed
- Check browser console for errors
- Verify API_BASE_URL in frontend/dashboard.js

**No data showing?**
- Run the demo to generate test data
- Check database file exists: `database/idps.db`
- Verify API is running: `curl http://localhost:5000/api/health`

### Customization

**Change refresh interval:**
Edit `frontend/dashboard.js` line 9:
```javascript
setInterval(refreshData, 30000);  // 30 seconds (change as needed)
```

**Customize colors/theme:**
Edit `frontend/styles.css` CSS variables at the top

**Add more charts:**
Add new Chart.js visualizations in `frontend/dashboard.js`

### Security Notes

⚠️ **For production:**
1. Add authentication (consider Flask-Login or JWT tokens)
2. Use HTTPS (setup nginx reverse proxy)
3. Restrict API access to trusted IPs
4. Change default ports
5. Enable firewall rules

### Screenshot

Once running, you'll see:
- 📊 4 statistic cards at the top
- 📈 2 interactive charts (timeline & severity distribution)
- 📋 Recent threats table with filtering
- 👥 Top attackers list
- 🚫 Blocked IPs with unblock functionality

**Everything updates automatically every 30 seconds!**
