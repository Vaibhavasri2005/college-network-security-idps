# IDPS Project Structure

Complete file structure with frontend, backend, and database:

```
IDS project/
│
├── README.md                          ← Main documentation (UPDATED)
├── LICENSE                            ← MIT License
├── requirements.txt                   ← Python dependencies (NEW)
├── DASHBOARD_GUIDE.md                 ← Dashboard usage guide (NEW)
├── HOW_TO_VISUALIZE.md                ← Visualization explanation (NEW)
│
├── config/                            ← Configuration files
│   ├── idps_config.yaml               ← Main IDPS configuration
│   ├── alert_config.yaml              ← Alert channels config
│   ├── whitelist.txt                  ← Trusted IPs
│   └── blacklist.txt                  ← Known malicious IPs
│
├── database/                          ← Database layer (NEW)
│   ├── schema.sql                     ← Database schema definition
│   ├── models.py                      ← Python ORM models
│   └── idps.db                        ← SQLite database (auto-created)
│
├── backend/                           ← Flask API server (NEW)
│   └── api.py                         ← RESTful API endpoints
│
├── frontend/                          ← Web dashboard (NEW)
│   ├── index.html                     ← Dashboard HTML
│   ├── styles.css                     ← Dashboard styles
│   └── dashboard.js                   ← Dashboard JavaScript
│
├── scripts/                           ← Python monitoring scripts
│   ├── monitor.py                     ← Main daemon (UPDATED with DB)
│   ├── log_analyzer.py                ← Log parsing engine
│   ├── threat_detector.py             ← Threat detection algorithms
│   ├── alert_sender.py                ← Multi-channel alerts
│   ├── ip_blocker.sh                  ← IP blocking utility
│   ├── status.sh                      ← System status checker
│   ├── view_blocked.sh                ← Display blocked IPs
│   ├── view_alerts.sh                 ← Show recent threats
│   ├── unban_ip.sh                    ← Unban IP addresses
│   └── install.sh                     ← Automated installer
│
├── fail2ban/                          ← Fail2Ban integration
│   ├── filters/                       ← Custom attack patterns
│   │   ├── custom-ssh.conf            ← SSH attack patterns
│   │   ├── brute-force.conf           ← Brute-force detection
│   │   └── port-scan.conf             ← Port scan detection
│   └── jails/                         ← Jail configurations
│       └── idps-jail.local            ← IDPS jail settings
│
├── systemd/                           ← Systemd service files
│   └── idps-monitor.service           ← Monitor service unit
│
├── docs/                              ← Detailed documentation
│   ├── INSTALLATION.md                ← Installation guide
│   ├── CONFIGURATION.md               ← Configuration reference
│   ├── TROUBLESHOOTING.md             ← Common issues
│   ├── ARCHITECTURE.md                ← System architecture
│   ├── TESTING.md                     ← Testing guide
│   └── QUICKSTART.md                  ← Quick start guide
│
├── logs/                              ← Log files (auto-created)
│   ├── idps.log                       ← Main activity log
│   ├── threats.log                    ← Detected threats
│   └── blocks.log                     ← Blocked IPs log
│
├── windows_demo.py                    ← Windows demo (original)
├── windows_demo_with_db.py            ← Enhanced demo with DB (NEW)
└── DEPLOYMENT_CHECKLIST.md            ← Deployment guide
```

## File Counts by Category

### Configuration (4 files)
- idps_config.yaml
- alert_config.yaml
- whitelist.txt
- blacklist.txt

### Database (3 files) ⭐ NEW
- schema.sql
- models.py
- idps.db (auto-generated)

### Backend API (1 file) ⭐ NEW
- api.py (Flask server with 12 REST endpoints)

### Frontend (3 files) ⭐ NEW
- index.html (Dashboard UI)
- styles.css (Dark theme design)
- dashboard.js (Interactive charts & tables)

### Python Scripts (9 files)
- monitor.py (Updated with database integration)
- log_analyzer.py
- threat_detector.py
- alert_sender.py
- ip_blocker.sh
- status.sh
- view_blocked.sh
- view_alerts.sh
- unban_ip.sh
- install.sh

### Fail2Ban (4 files)
- custom-ssh.conf
- brute-force.conf
- port-scan.conf
- idps-jail.local

### Documentation (13 files)
- README.md (Updated)
- DASHBOARD_GUIDE.md ⭐ NEW
- HOW_TO_VISUALIZE.md ⭐ NEW
- INSTALLATION.md
- CONFIGURATION.md
- TROUBLESHOOTING.md
- ARCHITECTURE.md
- TESTING.md
- QUICKSTART.md
- DEPLOYMENT_CHECKLIST.md
- requirements.txt ⭐ NEW
- LICENSE

### Demo (2 files)
- windows_demo.py
- windows_demo_with_db.py ⭐ NEW

## Total Files: 42 files

### New Files Added (13):
1. database/schema.sql
2. database/models.py
3. backend/api.py
4. frontend/index.html
5. frontend/styles.css
6. frontend/dashboard.js
7. requirements.txt
8. DASHBOARD_GUIDE.md
9. HOW_TO_VISUALIZE.md
10. windows_demo_with_db.py
11. PROJECT_STRUCTURE.md (this file)

### Updated Files (2):
1. README.md (Added dashboard info)
2. scripts/monitor.py (Database integration)

## Key Technologies Used

### Backend
- **Python 3.8+**: Core monitoring and detection
- **Flask**: RESTful API framework
- **SQLite**: Database for threat storage
- **PyYAML**: Configuration parsing
- **Requests**: HTTP client for webhooks

### Frontend
- **HTML5**: Dashboard structure
- **CSS3**: Responsive dark theme
- **JavaScript**: Interactive functionality
- **Chart.js**: Data visualization library
- **Fetch API**: REST API communication

### Linux Integration
- **Fail2Ban**: Intrusion prevention
- **UFW/iptables**: Firewall management
- **systemd**: Service orchestration
- **rsyslog**: Log aggregation

### Monitoring
- **Log Analysis**: Real-time log parsing
- **Pattern Matching**: Regex-based detection
- **Threat Scoring**: Multi-factor threat assessment
- **Rate Limiting**: Attack frequency tracking

## Data Flow

```
System Logs → monitor.py → Database → API → Dashboard
              ↓                ↓        ↓
         Detector          Storage   JSON
              ↓                       ↓
         Blocker                   Frontend
              ↓                       ↓
         Alerts                    Charts
```

## API Endpoints (12 total)

1. `GET /api/health` - Health check
2. `GET /api/dashboard/stats` - Dashboard statistics
3. `GET /api/threats` - List threats
4. `GET /api/threats/timeline` - Timeline data
5. `GET /api/threats/statistics` - Statistics
6. `GET /api/threats/top-attackers` - Top attackers
7. `GET /api/blocked-ips` - Blocked IPs list
8. `DELETE /api/blocked-ips/<ip>` - Unblock IP
9. `GET /api/events` - System events
10. `GET /api/search` - Search threats
11. `GET /` - Serve dashboard
12. Error handlers (404, 500)

## Database Tables (6 total)

1. **threats** - All detected threats
2. **blocked_ips** - Currently blocked IPs
3. **system_events** - System activity log
4. **alert_history** - Alert delivery tracking
5. **statistics** - Aggregated statistics
6. **ip_lists** - Whitelist/Blacklist

## Dashboard Features (8 sections)

1. **Header** - Status indicator
2. **Statistics Cards** - 4 key metrics
3. **Timeline Chart** - 24-hour threat graph
4. **Severity Chart** - Pie chart distribution
5. **Threats Table** - Searchable/filterable
6. **Top Attackers** - Leaderboard
7. **Blocked IPs** - Management interface
8. **Auto-refresh** - 30-second updates

## Dependencies

### Python Packages (5 required)
```
pyyaml>=6.0
requests>=2.31.0
flask>=3.0.0
flask-cors>=4.0.0
python-dateutil>=2.8.2
```

### Linux Packages (Ubuntu)
```
fail2ban
ufw
iptables
python3
python3-pip
sqlite3
```

### Optional Enhancements
```
gunicorn (production WSGI)
nginx (reverse proxy)
postgresql (database upgrade)
redis (caching layer)
```

## Lines of Code (Approximate)

- Python scripts: ~2,500 lines
- JavaScript: ~400 lines
- CSS: ~350 lines
- HTML: ~200 lines
- SQL: ~100 lines
- Shell scripts: ~300 lines
- Configuration: ~200 lines
- Documentation: ~3,000 lines

**Total: ~7,000+ lines of code and documentation**

## Browser Compatibility

✅ Chrome 90+
✅ Firefox 88+
✅ Edge 90+
✅ Safari 14+
✅ Opera 76+

## Mobile Responsive

✅ Desktop (1920x1080)
✅ Laptop (1366x768)
✅ Tablet (768x1024)
✅ Mobile (375x667)

---

**Complete IDPS with visualization, database storage, and RESTful API!**
