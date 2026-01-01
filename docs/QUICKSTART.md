# IDPS Quick Start Guide

## What is IDPS?

IDPS (Intrusion Detection and Prevention System) is an automated security tool that:
- Monitors your Ubuntu server for suspicious activity
- Detects attacks like brute-force attempts and port scans
- Automatically blocks malicious IP addresses
- Sends alerts when threats are detected

## Prerequisites

- Ubuntu Server 20.04 or later
- Root/sudo access
- Basic command-line knowledge

## Installation (5 Minutes)

### Quick Install

1. **Download the project:**
   ```bash
   cd ~
   # Download/clone the project files
   cd "IDS project"
   ```

2. **Run installation:**
   ```bash
   sudo chmod +x scripts/install.sh
   sudo ./scripts/install.sh
   ```

3. **Follow prompts and let it install**
   - Will take 2-5 minutes
   - Installs all dependencies automatically

4. **Done!** IDPS is now protecting your server.

## Basic Usage

### Check System Status
```bash
sudo idps-status
```

### View Recent Threats
```bash
sudo idps-alerts
```

### View Blocked IPs
```bash
sudo idps-blocked
```

### Unban an IP (if needed)
```bash
sudo idps-unban 1.2.3.4
```

### Manually Block an IP
```bash
sudo idps-block 1.2.3.4
```

## Initial Configuration

### 1. Whitelist Your IP (Important!)

To avoid locking yourself out:

```bash
# Add your IP to whitelist
echo "YOUR_IP_HERE" | sudo tee -a /opt/idps/config/whitelist.txt

# Restart service
sudo systemctl restart idps-monitor
```

### 2. Configure Email Alerts (Optional)

```bash
# Edit alert config
sudo nano /opt/idps/config/alert_config.yaml
```

Update with your email:
```yaml
email:
  enabled: true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender: your-email@gmail.com
  password: your-app-password  # Use app-specific password
  recipients:
    - admin@example.com
```

Save and restart:
```bash
sudo systemctl restart idps-monitor
```

## Understanding the Output

### When you run `idps-status`:

```
✓ IDPS Monitor: Running
✓ Fail2Ban: Active, 3 jails, 2 banned IPs
✓ UFW: Active, 5 deny rules
✓ Logs: OK
```

All green checkmarks = everything is working!

### When you run `idps-alerts`:

```
⛔ [CRITICAL] brute_force
   Time: 2026-01-01 12:34:56
   IP: 192.0.2.100
   Details: 15 failed authentication attempts
```

This shows detected threats with severity and details.

### When you run `idps-blocked`:

```
[1] UFW Firewall Blocks
  Total Blocked: 2
  ✗ 192.0.2.100
  ✗ 198.51.100.50
```

Shows all currently blocked IPs.

## Common Tasks

### Start/Stop IDPS
```bash
# Start
sudo systemctl start idps-monitor

# Stop
sudo systemctl stop idps-monitor

# Restart
sudo systemctl restart idps-monitor
```

### View Live Logs
```bash
# Main log
sudo tail -f /opt/idps/logs/idps.log

# Threats
sudo tail -f /opt/idps/logs/threats.log
```

### Adjust Security Level

Edit config:
```bash
sudo nano /opt/idps/config/idps_config.yaml
```

**Strict (High Security):**
```yaml
detection:
  failed_login_threshold: 3
  brute_force_threshold: 2
```

**Moderate (Balanced):**
```yaml
detection:
  failed_login_threshold: 5
  brute_force_threshold: 3
```

**Lenient (Fewer False Positives):**
```yaml
detection:
  failed_login_threshold: 10
  brute_force_threshold: 5
```

After changes:
```bash
sudo systemctl restart idps-monitor
```

## Troubleshooting

### Service Won't Start
```bash
# Check status
sudo systemctl status idps-monitor

# View logs
sudo journalctl -u idps-monitor -n 50
```

### Locked Out?

If you can't SSH in:

1. **Access via console** (cloud provider's console or physical access)

2. **Stop IDPS:**
   ```bash
   sudo systemctl stop idps-monitor
   sudo systemctl stop fail2ban
   ```

3. **Unban yourself:**
   ```bash
   sudo fail2ban-client unban YOUR_IP
   sudo ufw delete deny from YOUR_IP
   ```

4. **Add to whitelist:**
   ```bash
   echo "YOUR_IP" | sudo tee -a /opt/idps/config/whitelist.txt
   ```

5. **Restart:**
   ```bash
   sudo systemctl start fail2ban
   sudo systemctl start idps-monitor
   ```

### Not Detecting Threats

Check if service is running:
```bash
sudo idps-status
```

Check logs are being monitored:
```bash
ls -l /var/log/auth.log
```

### Too Many False Positives

Increase thresholds:
```bash
sudo nano /opt/idps/config/idps_config.yaml
```

Change:
```yaml
detection:
  failed_login_threshold: 10  # Increase
  timeframe: 900              # Increase window
```

## Security Best Practices

1. **Always whitelist your admin IPs** - Do this immediately after installation

2. **Start with moderate settings** - Don't go too strict initially

3. **Monitor for a week** - Check for false positives before tightening

4. **Regular reviews** - Check `idps-alerts` weekly

5. **Keep updated** - Update IDPS and system packages regularly

6. **Enable email alerts** - Get notified of critical threats

7. **Backup configuration** - Keep copies of your config files

8. **Test in staging first** - If possible, test changes in a test environment

9. **Keep console access** - Always have backup access method

10. **Document changes** - Note any configuration modifications

## Next Steps

After basic setup:

1. ✓ Whitelist your IPs
2. ✓ Configure email alerts
3. ✓ Test the system (see TESTING.md)
4. ✓ Adjust thresholds based on your needs
5. ✓ Set up regular monitoring
6. ✓ Read full documentation for advanced features

## Getting Help

### Check Documentation
- [README.md](../README.md) - Full overview
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation
- [CONFIGURATION.md](CONFIGURATION.md) - All configuration options
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [TESTING.md](TESTING.md) - How to test

### Check Logs
```bash
sudo idps-status
sudo journalctl -u idps-monitor -n 50
```

### Emergency Disable
```bash
sudo systemctl stop idps-monitor
sudo systemctl stop fail2ban
```

## File Locations

- **Config:** `/opt/idps/config/`
- **Scripts:** `/opt/idps/scripts/`
- **Logs:** `/opt/idps/logs/`
- **Commands:** `/usr/local/bin/idps-*`
- **Service:** `/etc/systemd/system/idps-monitor.service`

## Summary

IDPS provides automated security for your Ubuntu server by:
- Monitoring logs for attacks
- Detecting malicious patterns
- Automatically blocking threats
- Alerting you to problems

Key commands:
- `idps-status` - Check system
- `idps-alerts` - View threats
- `idps-blocked` - View blocked IPs
- `idps-unban <IP>` - Unban an IP

**Important:** Always whitelist your admin IPs to avoid lockout!

For more details, see the full documentation in the `docs/` folder.
