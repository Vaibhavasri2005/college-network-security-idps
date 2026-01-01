# IDPS Installation Guide

## Overview
This guide provides detailed instructions for installing and configuring the Intrusion Detection and Prevention System (IDPS) on Ubuntu Server.

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04 LTS or later (Debian-based systems supported)
- **RAM**: Minimum 1GB, Recommended 2GB+
- **Disk Space**: Minimum 500MB free space
- **CPU**: Any modern processor
- **Network**: Internet connection for initial installation

### Access Requirements
- Root or sudo privileges
- SSH access (if remote)
- Basic Linux command-line knowledge

## Installation Methods

### Method 1: Quick Installation (Recommended)

1. **Download or clone the project**
   ```bash
   cd ~
   git clone <repository-url>
   cd IDS\ project/
   ```

2. **Run the installation script**
   ```bash
   sudo chmod +x scripts/install.sh
   sudo ./scripts/install.sh
   ```

3. **Follow the prompts**
   - The script will install all dependencies
   - Configure Fail2Ban and firewall
   - Set up the monitoring service
   - Create command shortcuts

4. **Verify installation**
   ```bash
   sudo idps-status
   ```

### Method 2: Manual Installation

#### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### Step 2: Install Dependencies
```bash
# Install core packages
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-yaml \
    fail2ban \
    ufw \
    iptables \
    iptables-persistent \
    rsyslog

# Install Python packages
sudo pip3 install pyyaml requests
```

#### Step 3: Create Installation Directory
```bash
sudo mkdir -p /opt/idps
sudo mkdir -p /opt/idps/{logs,config,scripts}
sudo mkdir -p /opt/idps/fail2ban/{filters,jails}
```

#### Step 4: Copy Project Files
```bash
# Copy all files to /opt/idps
sudo cp -r config/* /opt/idps/config/
sudo cp -r scripts/* /opt/idps/scripts/
sudo cp -r fail2ban/* /opt/idps/fail2ban/

# Make scripts executable
sudo chmod +x /opt/idps/scripts/*.sh
sudo chmod +x /opt/idps/scripts/*.py
```

#### Step 5: Configure Fail2Ban
```bash
# Install custom filters
sudo cp /opt/idps/fail2ban/filters/*.conf /etc/fail2ban/filter.d/

# Install custom jails
sudo cp /opt/idps/fail2ban/jails/*.local /etc/fail2ban/jail.d/

# Enable and start Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### Step 6: Configure UFW Firewall
```bash
# Enable UFW
sudo ufw --force enable

# Allow SSH (IMPORTANT!)
sudo ufw allow 22/tcp

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Reload firewall
sudo ufw reload
```

#### Step 7: Install Systemd Service
```bash
# Copy service file
sudo cp systemd/idps-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable idps-monitor

# Start service
sudo systemctl start idps-monitor
```

#### Step 8: Configure Log Rotation
```bash
sudo tee /etc/logrotate.d/idps > /dev/null << 'EOF'
/opt/idps/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
}
EOF
```

## Post-Installation Configuration

### 1. Configure Whitelist
Add your trusted IPs to prevent accidental lockout:

```bash
sudo nano /opt/idps/config/whitelist.txt
```

Add your IPs:
```
# Your admin IP
203.0.113.10

# Your office network
192.168.1.0/24

# VPN gateway
10.0.0.1
```

### 2. Configure Alert Settings
Set up email alerts:

```bash
sudo nano /opt/idps/config/alert_config.yaml
```

Update email settings:
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

### 3. Adjust Detection Thresholds
Customize detection sensitivity:

```bash
sudo nano /opt/idps/config/idps_config.yaml
```

Adjust thresholds:
```yaml
detection:
  failed_login_threshold: 5      # Lower = stricter
  brute_force_threshold: 3
  port_scan_threshold: 10
```

### 4. Configure Firewall Rules
Add any services you want to allow:

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow custom port
sudo ufw allow 8080/tcp
```

## Verification

### Check Service Status
```bash
sudo systemctl status idps-monitor
```

### Check IDPS Status
```bash
sudo idps-status
```

### View Logs
```bash
# Main log
sudo tail -f /opt/idps/logs/idps.log

# Threats
sudo tail -f /opt/idps/logs/threats.log

# Blocks
sudo tail -f /opt/idps/logs/blocks.log
```

### Verify Fail2Ban
```bash
sudo fail2ban-client status
sudo fail2ban-client status idps-ssh
```

### Verify Firewall
```bash
sudo ufw status verbose
```

## Testing

### Test Detection (Safe Environment Only!)
```bash
# From another machine, try to SSH with wrong password multiple times
ssh wronguser@your-server-ip

# Check if detected
sudo idps-alerts

# Check if blocked
sudo idps-blocked
```

### Unban Test IP
```bash
sudo idps-unban <test-ip>
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u idps-monitor -n 50

# Check Python syntax
python3 /opt/idps/scripts/monitor.py

# Check permissions
sudo chown -R root:root /opt/idps
sudo chmod +x /opt/idps/scripts/*.py
```

### Fail2Ban Not Working
```bash
# Check Fail2Ban status
sudo fail2ban-client status

# Check jail configuration
sudo fail2ban-client status idps-ssh

# Restart Fail2Ban
sudo systemctl restart fail2ban
```

### UFW Issues
```bash
# Check UFW status
sudo ufw status verbose

# Reset UFW (WARNING: Will remove all rules!)
sudo ufw --force reset
sudo ufw --force enable
```

### Locked Out of Server
If you accidentally locked yourself out:

1. Access via console (physical or cloud provider's console)
2. Disable IDPS temporarily:
   ```bash
   sudo systemctl stop idps-monitor
   sudo systemctl stop fail2ban
   ```
3. Add your IP to whitelist:
   ```bash
   echo "YOUR_IP" >> /opt/idps/config/whitelist.txt
   ```
4. Restart services:
   ```bash
   sudo systemctl start fail2ban
   sudo systemctl start idps-monitor
   ```

## Uninstallation

If you need to remove IDPS:

```bash
# Stop services
sudo systemctl stop idps-monitor
sudo systemctl disable idps-monitor

# Remove service file
sudo rm /etc/systemd/system/idps-monitor.service
sudo systemctl daemon-reload

# Remove Fail2Ban custom configurations
sudo rm /etc/fail2ban/filter.d/custom-*.conf
sudo rm /etc/fail2ban/filter.d/brute-force.conf
sudo rm /etc/fail2ban/filter.d/port-scan.conf
sudo rm /etc/fail2ban/jail.d/idps-jail.local
sudo systemctl restart fail2ban

# Remove IDPS installation
sudo rm -rf /opt/idps

# Remove command shortcuts
sudo rm /usr/local/bin/idps-*

# Optional: Remove packages (be careful!)
# sudo apt-get remove fail2ban ufw
```

## Security Considerations

1. **Always maintain whitelist** - Keep your admin IPs whitelisted
2. **Test in staging** - Test configuration changes in a safe environment first
3. **Monitor logs** - Regularly review threat and block logs
4. **Keep updated** - Update IDPS and system packages regularly
5. **Backup configuration** - Keep backups of your configuration files

## Next Steps

After installation:
1. Read [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options
2. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. Set up email alerts for critical threats
4. Customize detection rules for your environment
5. Schedule regular reviews of blocked IPs and threats

## Support

For issues and questions:
- Check the documentation in the `docs/` folder
- Review logs for error messages
- Consult the troubleshooting guide

## Updates

To update IDPS:
```bash
cd ~/IDS\ project/
git pull
sudo ./scripts/install.sh
```

The installation script will update all components while preserving your configuration.
