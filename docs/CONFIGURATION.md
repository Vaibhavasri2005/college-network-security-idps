# IDPS Configuration Guide

## Overview
This guide explains all configuration options available in the IDPS system.

## Configuration Files

### Main Configuration: `config/idps_config.yaml`

#### Monitoring Settings
```yaml
monitoring:
  # Log files to monitor
  log_files:
    - /var/log/auth.log       # Ubuntu/Debian
    - /var/log/syslog
    - /var/log/secure         # For RHEL-based systems
  
  # How often to scan logs (seconds)
  scan_interval: 5
  
  # Debug mode (verbose logging)
  debug: false
```

**Recommendations:**
- `scan_interval`: 5-10 seconds for active servers, 30-60 for low-traffic servers
- Add custom application logs as needed

#### Detection Settings
```yaml
detection:
  # Failed login attempts before triggering alert
  failed_login_threshold: 5
  
  # Time window for counting events (seconds)
  timeframe: 600  # 10 minutes
  
  # Port scanning detection
  port_scan_threshold: 10
  
  # Brute force detection
  brute_force_threshold: 3
  
  # Invalid username attempts
  invalid_user_threshold: 3
  
  # Detect root login attempts
  detect_root_attempts: true
  
  # Connection flood detection
  connection_threshold: 20
  connection_timeframe: 60
```

**Security Levels:**

*Strict (High Security):*
```yaml
failed_login_threshold: 3
brute_force_threshold: 2
port_scan_threshold: 5
timeframe: 300
```

*Moderate (Balanced):*
```yaml
failed_login_threshold: 5
brute_force_threshold: 3
port_scan_threshold: 10
timeframe: 600
```

*Lenient (Low False Positives):*
```yaml
failed_login_threshold: 10
brute_force_threshold: 5
port_scan_threshold: 20
timeframe: 900
```

#### Prevention Settings
```yaml
prevention:
  # Ban duration in seconds
  ban_time: 3600  # 1 hour
  
  # Permanent ban after N offenses
  permanent_ban_after: 5
  
  # Enable/disable blocking methods
  use_fail2ban: true
  use_ufw: true
  use_iptables: false
  
  # Auto-unban when ban time expires
  auto_unban: true
```

**Ban Time Examples:**
- `300` = 5 minutes (testing)
- `3600` = 1 hour (moderate)
- `86400` = 24 hours (strict)
- `604800` = 1 week (very strict)

#### Whitelist Configuration
```yaml
whitelist:
  enabled: true
  file: config/whitelist.txt
  ips:
    - 127.0.0.1
    - ::1
    # Add trusted IPs here
```

**Important:** Always whitelist:
- Your admin/management IPs
- Office network ranges
- VPN gateway IPs
- Monitoring service IPs

#### Blacklist Configuration
```yaml
blacklist:
  enabled: true
  file: config/blacklist.txt
  ips: []
    # Add known malicious IPs
```

#### Logging Configuration
```yaml
logging:
  main_log: logs/idps.log
  threat_log: logs/threats.log
  block_log: logs/blocks.log
  
  # Log level
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  
  # Log rotation
  max_size: 100  # MB
  backup_count: 5
  rotate: true
```

**Log Levels:**
- `DEBUG`: Everything (very verbose)
- `INFO`: Normal operations and detections
- `WARNING`: Potential issues
- `ERROR`: Actual problems
- `CRITICAL`: Severe problems

#### Alert Configuration
```yaml
alerts:
  email_enabled: false
  email_config: config/alert_config.yaml
  
  # What to alert on
  alert_on:
    - brute_force
    - port_scan
    - repeated_failures
    - permanent_ban
  
  # Minimum severity
  min_severity: HIGH
  
  # Alert cooldown (seconds)
  cooldown: 300
```

### Alert Configuration: `config/alert_config.yaml`

#### Email Alerts
```yaml
email:
  enabled: false
  smtp_server: smtp.gmail.com
  smtp_port: 587
  use_tls: true
  sender: your-email@gmail.com
  password: your-app-password
  recipients:
    - admin@example.com
  max_emails_per_hour: 10
```

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate app-specific password
3. Use app password in configuration

**Other SMTP Providers:**
- **Outlook:** smtp.office365.com:587
- **Yahoo:** smtp.mail.yahoo.com:587
- **Custom:** Check your provider's documentation

#### Slack Integration
```yaml
slack:
  enabled: false
  webhook_url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  channel: "#security-alerts"
  username: IDPS Bot
```

**Setup:**
1. Create Slack app: https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Add webhook URL to configuration

#### Telegram Integration
```yaml
telegram:
  enabled: false
  bot_token: YOUR_BOT_TOKEN
  chat_id: YOUR_CHAT_ID
```

**Setup:**
1. Create bot via @BotFather
2. Get bot token
3. Get chat ID from @userinfobot

### Fail2Ban Configuration

#### Custom Jails: `fail2ban/jails/idps-jail.local`

**SSH Protection:**
```ini
[idps-ssh]
enabled  = true
port     = ssh
filter   = custom-ssh
logpath  = /var/log/auth.log
maxretry = 3
findtime = 600
bantime  = 3600
```

**Parameters:**
- `enabled`: Activate/deactivate jail
- `maxretry`: Attempts before ban
- `findtime`: Time window (seconds)
- `bantime`: Ban duration (seconds)

**Common Configurations:**

*Strict SSH:*
```ini
maxretry = 2
findtime = 300
bantime  = 7200
```

*Moderate SSH:*
```ini
maxretry = 5
findtime = 600
bantime  = 3600
```

*Lenient SSH:*
```ini
maxretry = 10
findtime = 900
bantime  = 1800
```

## Environment-Specific Configuration

### Development/Testing Environment
```yaml
detection:
  failed_login_threshold: 10
  timeframe: 600

prevention:
  ban_time: 300  # 5 minutes
  permanent_ban_after: 10
  auto_unban: true

alerts:
  email_enabled: false
  min_severity: MEDIUM

logging:
  level: DEBUG
```

### Production Environment
```yaml
detection:
  failed_login_threshold: 3
  timeframe: 300

prevention:
  ban_time: 7200  # 2 hours
  permanent_ban_after: 3
  auto_unban: false

alerts:
  email_enabled: true
  min_severity: HIGH

logging:
  level: INFO
```

### High-Security Environment
```yaml
detection:
  failed_login_threshold: 2
  timeframe: 180
  detect_root_attempts: true

prevention:
  ban_time: 86400  # 24 hours
  permanent_ban_after: 2
  use_fail2ban: true
  use_ufw: true
  use_iptables: true

alerts:
  email_enabled: true
  min_severity: MEDIUM
  alert_on:
    - brute_force
    - port_scan
    - repeated_failures
    - permanent_ban
    - invalid_user
    - root_login
```

## Whitelist Management

### File Format: `config/whitelist.txt`
```
# Comments start with #
# One IP or CIDR range per line

# Localhost
127.0.0.1
::1

# Single IPs
203.0.113.10
198.51.100.5

# CIDR ranges
192.168.1.0/24
10.0.0.0/8

# IPv6
2001:db8::/32
```

### Dynamic Whitelist Management
```bash
# Add IP to whitelist
echo "1.2.3.4" | sudo tee -a /opt/idps/config/whitelist.txt

# Remove IP from whitelist
sudo sed -i '/1.2.3.4/d' /opt/idps/config/whitelist.txt

# Reload configuration (restart service)
sudo systemctl restart idps-monitor
```

## Blacklist Management

### File Format: `config/blacklist.txt`
Same format as whitelist.

### Automated Blacklist Updates
Create a script to update from threat intelligence feeds:

```bash
#!/bin/bash
# Update blacklist from threat feeds

# Example: Abuse.ch SSL Blacklist
curl -s https://sslbl.abuse.ch/blacklist/sslipblacklist.csv \
    | grep -v "^#" | cut -d',' -f2 \
    >> /opt/idps/config/blacklist.txt

# Deduplicate
sort -u /opt/idps/config/blacklist.txt -o /opt/idps/config/blacklist.txt

# Restart service
systemctl restart idps-monitor
```

## Performance Tuning

### Low-Resource Servers
```yaml
monitoring:
  scan_interval: 30  # Scan less frequently

performance:
  max_threads: 2
  memory_limit: 50
  enable_cache: true

advanced:
  analyze_history: false
```

### High-Traffic Servers
```yaml
monitoring:
  scan_interval: 2  # Scan more frequently

performance:
  max_threads: 8
  memory_limit: 500
  enable_cache: true
  cache_ttl: 600
```

## Configuration Validation

### Test Configuration
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('/opt/idps/config/idps_config.yaml'))"

# Test email alerts
python3 /opt/idps/scripts/alert_sender.py --test

# Dry run
python3 /opt/idps/scripts/monitor.py --dry-run
```

### Best Practices
1. **Backup before changes**:
   ```bash
   sudo cp /opt/idps/config/idps_config.yaml /opt/idps/config/idps_config.yaml.backup
   ```

2. **Test in staging** before production

3. **Start lenient**, tighten gradually

4. **Monitor false positives** in first week

5. **Document changes** in comments

## Reload Configuration

After changing configuration:
```bash
# Restart IDPS service
sudo systemctl restart idps-monitor

# Restart Fail2Ban (if changed Fail2Ban configs)
sudo systemctl restart fail2ban

# Reload firewall (if changed UFW rules)
sudo ufw reload
```

## Configuration Templates

Templates for common scenarios are available in `config/templates/`:
- `strict.yaml` - High security
- `moderate.yaml` - Balanced
- `lenient.yaml` - Low false positives
- `development.yaml` - For testing

Copy and customize as needed.
