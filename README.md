# Intrusion Detection and Prevention System (IDPS)

## Project Overview
A comprehensive IDPS solution for Ubuntu servers that monitors, detects, and prevents security threats through automated log analysis, threat detection, and real-time blocking of malicious activities. **Now includes a beautiful web dashboard for real-time visualization!**

## 🆕 New: Web Dashboard
**View all threats, attacks, and statistics in a modern web interface!**

- 📊 Real-time threat statistics and charts
- 🔍 Searchable threat history with filtering
- 🚫 One-click IP unblocking
- 📈 Interactive 24-hour threat timeline
- 👥 Top attackers leaderboard
- 🎨 Modern dark theme design

**Dashboard URL**: http://localhost:5000 (after starting API server)

![Dashboard Preview](See HOW_TO_VISUALIZE.md for details)

## Features
- **Real-time Log Monitoring**: Continuous analysis of `/var/log/auth.log` and other system logs
- **Threat Detection**: Identifies brute-force attacks, unauthorized SSH access, failed authentications, and IP scanning
- **Automated Prevention**: Uses Fail2Ban and UFW/iptables to automatically block malicious IPs
- **Database Storage**: All threats stored in SQLite database for historical analysis
- **RESTful API**: Flask backend for dashboard and integrations
- **Web Dashboard**: Beautiful interface to visualize threats and manage blocks
- **Alert System**: Email, Slack, Telegram, and webhook notifications
- **Custom Rules**: Extensible detection rules for various attack patterns

## System Components

### 1. Log Monitoring Module
- Python-based log analyzer
- Real-time log parsing and pattern matching
- Threat scoring system
- Database integration for threat storage

### 2. Detection Engine
- Brute-force attack detection
- Failed login attempt tracking
- Port scanning detection
- Unusual access pattern identification
- Whitelist/Blacklist IP filtering

### 3. Prevention Layer
- Fail2Ban integration with custom jails
- UFW firewall rule automation
- IP blacklist/whitelist management
- Temporary and permanent bans
- Automatic database logging

### 4. Web Dashboard & API
- **Frontend**: Modern HTML/CSS/JS with Chart.js
- **Backend**: Flask RESTful API
- **Database**: SQLite (upgradeable to PostgreSQL)
- **Features**: Real-time stats, interactive charts, threat management

### 5. Alerting System
- Email notifications for critical events
- Slack webhook integration
- Telegram bot alerts
- Custom webhook support
- Alert cooldown mechanism

## Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    IDPS Architecture                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐      ┌─────────────────┐             │
│  │  System Logs │─────▶│  Log Monitoring │             │
│  │ /var/log/*   │      │     Module      │             │
│  └──────────────┘      └────────┬────────┘             │
│                                  │                       │
│                                  ▼                       │
│                        ┌─────────────────┐              │
│                        │ Threat Detector │              │
│                        │   & Database    │              │
│                        └────────┬────────┘              │
│                                 │                        │
│                    ┌────────────┼────────────┐          │
│                    │            │            │          │
│                    ▼            ▼            ▼          │
│           ┌─────────────┐  ┌────────┐  ┌────────┐      │
│           │  Firewall   │  │Database│  │ Alerts │      │
│           │   Blocking  │  │Storage │  │ System │      │
│           └─────────────┘  └────┬───┘  └────────┘      │
│                                 │                        │
│                                 ▼                        │
│                        ┌─────────────────┐              │
│                        │   Web Dashboard │              │
│                        │  (Flask + API)  │              │
│                        └─────────────────┘              │
│                        │ Detection Engine│              │
│                        │  (Python/Bash)  │              │
│                        └────────┬────────┘              │
│                                 │                        │
│                    ┌────────────┴────────────┐          │
│                    ▼                         ▼          │
│          ┌──────────────────┐     ┌──────────────────┐ │
│          │ Prevention Layer │     │ Alerting System  │ │
│          │  - Fail2Ban      │     │  - Email Alerts  │ │
│          │  - UFW/iptables  │     │  - Dashboard     │ │
│          └──────────────────┘     └──────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites
- Ubuntu Server 20.04 LTS or later (for production)
- OR Windows 10/11 (for testing with demo)
- Root or sudo privileges (Linux)
- Python 3.8+
- Internet connection for initial setup

## 🚀 Quick Start (Windows Demo)

Want to see it in action right now? Run the demo!

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Sample Data
```bash
python windows_demo_with_db.py
```
This creates 48 sample threats in the database.

### 3. Start the API Server
```bash
cd backend
python api.py
```

### 4. Open Dashboard
Navigate to: **http://localhost:5000**

🎉 **You'll see:**
- Real-time threat statistics
- Interactive charts
- Recent threats table
- Top attackers list
- Blocked IPs with unblock capability

**See [HOW_TO_VISUALIZE.md](HOW_TO_VISUALIZE.md) for detailed dashboard guide.**

## 📦 Installation (Ubuntu Production)

### 1. Installation
```bash
# Clone the repository or copy files to your server
sudo chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

### 2. Configuration
```bash
# Edit main configuration
sudo nano config/idps_config.yaml

# Configure email/Slack/Telegram alerts
sudo nano config/alert_config.yaml

# Add your admin IPs to whitelist (IMPORTANT!)
sudo nano config/whitelist.txt
```

### 3. Start the System
```bash
# Start monitoring service
sudo systemctl start idps-monitor
sudo systemctl enable idps-monitor

# Start API server (for dashboard)
cd /opt/idps/backend
python3 api.py
# Or setup as systemd service (see DASHBOARD_GUIDE.md)
```

### 4. Access Dashboard
Navigate to: **http://your-server-ip:5000**

### 5. Monitor Status
```bash
# Check IDPS status
sudo ./scripts/status.sh

# View blocked IPs
sudo ./scripts/view_blocked.sh

# View recent alerts
sudo ./scripts/view_alerts.sh
```

## Directory Structure
```
IDS project/
├── README.md
├── config/
│   ├── idps_config.yaml          # Main configuration
│   ├── alert_config.yaml         # Alert settings
│   ├── whitelist.txt             # Whitelisted IPs
│   └── blacklist.txt             # Permanent blacklist
├── fail2ban/
│   ├── filters/
│   │   ├── custom-ssh.conf       # SSH attack patterns
│   │   ├── brute-force.conf      # Brute-force detection
│   │   └── port-scan.conf        # Port scanning detection
│   └── jails/
│       ├── custom-jail.conf      # Custom jail configuration
│       └── idps-jail.local       # IDPS-specific jails
├── scripts/
│   ├── install.sh                # Complete installation script
│   ├── monitor.py                # Main monitoring daemon
│   ├── log_analyzer.py           # Log analysis engine
│   ├── threat_detector.py        # Threat detection logic
│   ├── ip_blocker.sh             # IP blocking utility
│   ├── alert_sender.py           # Alert notification system
│   ├── status.sh                 # System status checker
│   ├── view_blocked.sh           # View blocked IPs
│   ├── view_alerts.sh            # View recent alerts
│   └── unban_ip.sh               # Manually unban an IP
├── logs/
│   ├── idps.log                  # IDPS system logs
│   ├── threats.log               # Detected threats
│   └── blocks.log                # Blocked IPs log
├── systemd/
│   └── idps-monitor.service      # Systemd service file
└── docs/
    ├── INSTALLATION.md           # Detailed installation guide
    ├── CONFIGURATION.md          # Configuration guide
    ├── TROUBLESHOOTING.md        # Common issues and solutions
    └── ARCHITECTURE.md           # Technical architecture
```

## Configuration

### Main Configuration (`config/idps_config.yaml`)
```yaml
monitoring:
  log_files:
    - /var/log/auth.log
    - /var/log/syslog
  scan_interval: 5  # seconds

detection:
  failed_login_threshold: 5
  timeframe: 600  # 10 minutes
  port_scan_threshold: 10
  brute_force_threshold: 3

prevention:
  ban_time: 3600  # 1 hour
  permanent_ban_after: 5  # offenses
  use_fail2ban: true
  use_ufw: true
```

## Detection Rules

### 1. Brute-Force Detection
- Threshold: 5 failed login attempts in 10 minutes
- Action: Temporary ban (1 hour)
- Escalation: Permanent ban after 5 offenses

### 2. SSH Unauthorized Access
- Pattern: Invalid user attempts, denied access
- Action: Immediate temporary ban
- Alert: High priority notification

### 3. Port Scanning
- Detection: Multiple connection attempts to different ports
- Threshold: 10+ ports in 60 seconds
- Action: Immediate ban + alert

### 4. Failed Password Attempts
- Threshold: 3 failed passwords in 5 minutes
- Action: Temporary ban
- Escalation: Extended ban duration

## Security Best Practices
1. **Whitelist Trusted IPs**: Add your administrative IPs to whitelist
2. **Regular Updates**: Keep the system and rules updated
3. **Monitor Logs**: Regularly review `logs/threats.log`
4. **Test Configuration**: Use test mode before production
5. **Backup Rules**: Keep backup of custom rules

## Monitoring and Maintenance

### Check System Status
```bash
sudo systemctl status idps-monitor
sudo ./scripts/status.sh
```

### View Recent Threats
```bash
sudo tail -f logs/threats.log
```

### View Blocked IPs
```bash
sudo fail2ban-client status
sudo ufw status numbered
```

### Unban an IP
```bash
sudo ./scripts/unban_ip.sh <IP_ADDRESS>
```

## Alert Notifications

### Email Alerts
Configure email settings in `config/alert_config.yaml`:
```yaml
email:
  enabled: true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender: your-email@gmail.com
  password: your-app-password
  recipients:
    - admin@example.com
```

## Testing the System

### Simulate Attacks (Testing Environment Only)
```bash
# Test failed login detection
for i in {1..6}; do ssh invalid_user@localhost; done

# View detection results
sudo tail logs/threats.log
```

## Troubleshooting

### Service Not Starting
```bash
sudo journalctl -u idps-monitor -n 50
```

### Fail2Ban Issues
```bash
sudo fail2ban-client status
sudo systemctl restart fail2ban
```

### False Positives
Add IP to whitelist: `echo "IP_ADDRESS" >> config/whitelist.txt`

## Performance Considerations
- CPU Usage: ~1-2% on average
- Memory: ~50-100 MB
- Disk I/O: Minimal log writing
- Network: No impact

## Compliance and Legal
- Ensure compliance with local laws
- Log retention policies
- Privacy considerations for log data

## Contributing
Contributions are welcome! Please follow the standard GitHub workflow.

## License
MIT License - See LICENSE file for details

## Support
For issues and questions:
- GitHub Issues: [Project Issues]
- Documentation: See `docs/` directory
- Email: support@example.com

## Version History
- v1.0.0 - Initial release
  - Basic monitoring and detection
  - Fail2Ban integration
  - UFW firewall support

## Acknowledgments
- Fail2Ban project
- Ubuntu Security Team
- Python logging community

## Author
Created as part of an IDPS security project demonstrating practical implementation of intrusion detection and prevention on Linux servers.
