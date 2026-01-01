# IDPS Troubleshooting Guide

## Common Issues and Solutions

### Service Issues

#### IDPS Service Won't Start

**Symptoms:**
- Service fails to start
- Service starts but immediately stops

**Diagnosis:**
```bash
# Check service status
sudo systemctl status idps-monitor

# View recent logs
sudo journalctl -u idps-monitor -n 50

# Check for Python errors
sudo python3 /opt/idps/scripts/monitor.py
```

**Solutions:**

1. **Check Python dependencies:**
   ```bash
   sudo pip3 install -U pyyaml requests
   ```

2. **Verify file permissions:**
   ```bash
   sudo chown -R root:root /opt/idps
   sudo chmod +x /opt/idps/scripts/*.py
   sudo chmod +x /opt/idps/scripts/*.sh
   ```

3. **Check configuration syntax:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('/opt/idps/config/idps_config.yaml'))"
   ```

4. **Verify log directory exists:**
   ```bash
   sudo mkdir -p /opt/idps/logs
   sudo chmod 755 /opt/idps/logs
   ```

#### Service Crashes Frequently

**Diagnosis:**
```bash
# Check crash logs
sudo journalctl -u idps-monitor --since "1 hour ago"

# Monitor resource usage
top -p $(pgrep -f monitor.py)
```

**Solutions:**

1. **Increase resource limits:**
   ```bash
   sudo nano /etc/systemd/system/idps-monitor.service
   ```
   Update:
   ```ini
   MemoryLimit=500M
   CPUQuota=50%
   ```

2. **Reduce scan frequency:**
   ```yaml
   monitoring:
     scan_interval: 30  # Increase from 5
   ```

3. **Disable history analysis:**
   ```yaml
   advanced:
     analyze_history: false
   ```

### Fail2Ban Issues

#### Fail2Ban Not Banning IPs

**Diagnosis:**
```bash
# Check Fail2Ban status
sudo fail2ban-client status

# Check specific jail
sudo fail2ban-client status idps-ssh

# Check logs
sudo tail -f /var/log/fail2ban.log
```

**Solutions:**

1. **Verify jail is enabled:**
   ```bash
   sudo fail2ban-client status | grep idps
   ```

2. **Check filter syntax:**
   ```bash
   sudo fail2ban-regex /var/log/auth.log /etc/fail2ban/filter.d/custom-ssh.conf
   ```

3. **Reload Fail2Ban:**
   ```bash
   sudo systemctl restart fail2ban
   ```

4. **Check log paths:**
   ```bash
   ls -l /var/log/auth.log
   ```
   If missing, check `/var/log/secure` (RHEL-based systems)

#### False Positives - Legitimate IPs Banned

**Immediate Fix:**
```bash
# Unban the IP
sudo idps-unban <IP_ADDRESS>

# Add to whitelist
echo "<IP_ADDRESS>" | sudo tee -a /opt/idps/config/whitelist.txt

# Restart service
sudo systemctl restart idps-monitor
```

**Long-term Solutions:**

1. **Adjust thresholds:**
   ```yaml
   detection:
     failed_login_threshold: 10  # Increase
     timeframe: 900              # Increase window
   ```

2. **Review whitelist:**
   ```bash
   sudo nano /opt/idps/config/whitelist.txt
   ```
   Add:
   - Your office network
   - Admin IPs
   - Monitoring services
   - CI/CD servers

3. **Check for misconfigurations:**
   - Verify SSH service isn't logging normal connections as failures
   - Check for application issues causing authentication failures

### Firewall Issues

#### UFW Not Blocking IPs

**Diagnosis:**
```bash
# Check UFW status
sudo ufw status verbose

# Check if UFW is active
sudo ufw status | grep Status
```

**Solutions:**

1. **Enable UFW:**
   ```bash
   sudo ufw --force enable
   ```

2. **Verify default policies:**
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   ```

3. **Check for conflicting rules:**
   ```bash
   sudo ufw status numbered
   ```

#### Locked Out of Server

**Prevention:**
Always whitelist your IP before enabling strict rules!

**Recovery (via console access):**

1. **Access via cloud provider console or physical access**

2. **Disable IDPS temporarily:**
   ```bash
   sudo systemctl stop idps-monitor
   sudo systemctl stop fail2ban
   ```

3. **Remove blocking rules:**
   ```bash
   # UFW
   sudo ufw delete deny from YOUR_IP

   # iptables
   sudo iptables -D INPUT -s YOUR_IP -j DROP

   # Fail2Ban
   sudo fail2ban-client unban YOUR_IP
   ```

4. **Add to whitelist:**
   ```bash
   echo "YOUR_IP" | sudo tee -a /opt/idps/config/whitelist.txt
   ```

5. **Restart services:**
   ```bash
   sudo systemctl start fail2ban
   sudo systemctl start idps-monitor
   ```

**Recovery (no console access):**
- Contact hosting provider
- Use rescue mode
- Restore from backup

### Log Issues

#### Logs Not Being Created

**Diagnosis:**
```bash
# Check log directory
ls -la /opt/idps/logs/

# Check permissions
sudo ls -la /opt/idps/logs/
```

**Solutions:**

1. **Create log directory:**
   ```bash
   sudo mkdir -p /opt/idps/logs
   sudo chmod 755 /opt/idps/logs
   ```

2. **Check disk space:**
   ```bash
   df -h
   ```

3. **Verify log paths in config:**
   ```bash
   sudo nano /opt/idps/config/idps_config.yaml
   ```

#### Logs Growing Too Large

**Solutions:**

1. **Configure log rotation:**
   ```bash
   sudo nano /etc/logrotate.d/idps
   ```
   ```
   /opt/idps/logs/*.log {
       daily
       rotate 7
       compress
       delaycompress
       missingok
       notifempty
   }
   ```

2. **Manually rotate logs:**
   ```bash
   sudo logrotate -f /etc/logrotate.d/idps
   ```

3. **Reduce logging verbosity:**
   ```yaml
   logging:
     level: WARNING  # Instead of DEBUG
   ```

### Alert Issues

#### Email Alerts Not Working

**Diagnosis:**
```bash
# Check alert configuration
sudo cat /opt/idps/config/alert_config.yaml

# Test Python email functionality
python3 << EOF
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-password')
print("SMTP connection successful")
server.quit()
EOF
```

**Solutions:**

1. **Gmail - Use App Password:**
   - Enable 2FA
   - Generate app-specific password
   - Use that password in configuration

2. **Check SMTP settings:**
   ```yaml
   email:
     smtp_server: smtp.gmail.com  # Verify correct server
     smtp_port: 587                # Verify correct port
     use_tls: true                 # Enable TLS
   ```

3. **Verify firewall allows SMTP:**
   ```bash
   sudo ufw allow out 587/tcp
   ```

4. **Check email in spam folder**

5. **Test with simple script:**
   ```python
   python3 /opt/idps/scripts/alert_sender.py --test
   ```

#### Too Many Alerts

**Solutions:**

1. **Increase alert cooldown:**
   ```yaml
   alerts:
     cooldown: 3600  # 1 hour
   ```

2. **Raise severity threshold:**
   ```yaml
   alerts:
     min_severity: CRITICAL  # Only critical alerts
   ```

3. **Limit email rate:**
   ```yaml
   email:
     max_emails_per_hour: 5
   ```

### Detection Issues

#### Not Detecting Attacks

**Diagnosis:**
```bash
# Check if logs are being read
sudo tail -f /opt/idps/logs/idps.log

# Verify log file exists and is accessible
sudo ls -l /var/log/auth.log

# Check recent events
sudo tail -20 /var/log/auth.log
```

**Solutions:**

1. **Verify log paths:**
   ```yaml
   monitoring:
     log_files:
       - /var/log/auth.log  # Verify this exists
   ```

2. **Check scan interval:**
   ```yaml
   monitoring:
     scan_interval: 5  # Should be low for real-time detection
   ```

3. **Lower thresholds (carefully):**
   ```yaml
   detection:
     failed_login_threshold: 3
     brute_force_threshold: 2
   ```

4. **Verify patterns match your logs:**
   ```bash
   # Test regex patterns
   sudo grep "Failed password" /var/log/auth.log
   ```

#### Too Many False Positives

**Solutions:**

1. **Whitelist legitimate sources:**
   ```bash
   sudo nano /opt/idps/config/whitelist.txt
   ```

2. **Increase thresholds:**
   ```yaml
   detection:
     failed_login_threshold: 10
     timeframe: 900
   ```

3. **Review threat log:**
   ```bash
   sudo idps-alerts 50
   ```
   Identify patterns of false positives

4. **Adjust specific detection:**
   ```yaml
   detection:
     detect_root_attempts: false  # If legitimate root logins occur
   ```

### Performance Issues

#### High CPU Usage

**Diagnosis:**
```bash
# Check process CPU
top -p $(pgrep -f monitor.py)

# Check for log file size issues
du -sh /var/log/auth.log
```

**Solutions:**

1. **Increase scan interval:**
   ```yaml
   monitoring:
     scan_interval: 30
   ```

2. **Limit threads:**
   ```yaml
   performance:
     max_threads: 2
   ```

3. **Disable history analysis:**
   ```yaml
   advanced:
     analyze_history: false
   ```

#### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage
ps aux | grep monitor.py
```

**Solutions:**

1. **Limit cache size:**
   ```yaml
   performance:
     enable_cache: false
   ```

2. **Set memory limit:**
   ```bash
   sudo nano /etc/systemd/system/idps-monitor.service
   ```
   ```ini
   MemoryLimit=100M
   ```

3. **Reduce event buffer:**
   Edit `scripts/log_analyzer.py`:
   ```python
   self.event_buffer = deque(maxlen=1000)  # Reduce from 10000
   ```

### Integration Issues

#### Conflict with Existing Fail2Ban Configuration

**Solution:**
```bash
# Backup existing configuration
sudo cp -r /etc/fail2ban /etc/fail2ban.backup

# Merge configurations carefully
sudo nano /etc/fail2ban/jail.local

# Test configuration
sudo fail2ban-client -t
```

#### UFW Rules Conflicting

**Solution:**
```bash
# List all rules
sudo ufw status numbered

# Remove conflicting rules
sudo ufw delete <rule-number>

# Add IDPS rules after other critical rules
```

## Diagnostic Commands

### System Health Check
```bash
# Complete system status
sudo idps-status

# Check all components
sudo systemctl status idps-monitor fail2ban ufw

# Check recent threats
sudo idps-alerts 20

# Check blocked IPs
sudo idps-blocked
```

### Log Analysis
```bash
# IDPS main log
sudo tail -f /opt/idps/logs/idps.log

# Threats detected
sudo tail -f /opt/idps/logs/threats.log

# Blocked IPs
sudo tail -f /opt/idps/logs/blocks.log

# System auth log
sudo tail -f /var/log/auth.log

# Fail2Ban log
sudo tail -f /var/log/fail2ban.log
```

### Network Diagnostics
```bash
# Check active connections
sudo netstat -an | grep ESTABLISHED

# Check for suspicious connections
sudo ss -tunap

# Check firewall rules
sudo iptables -L -n -v
sudo ufw status verbose
```

## Getting Help

### Collect Diagnostic Information
```bash
#!/bin/bash
# Save diagnostic information

echo "=== IDPS Status ===" > idps-diagnostics.txt
sudo idps-status >> idps-diagnostics.txt

echo -e "\n=== Service Status ===" >> idps-diagnostics.txt
sudo systemctl status idps-monitor >> idps-diagnostics.txt

echo -e "\n=== Recent Logs ===" >> idps-diagnostics.txt
sudo journalctl -u idps-monitor -n 50 >> idps-diagnostics.txt

echo -e "\n=== Configuration ===" >> idps-diagnostics.txt
sudo cat /opt/idps/config/idps_config.yaml >> idps-diagnostics.txt

echo -e "\n=== System Info ===" >> idps-diagnostics.txt
uname -a >> idps-diagnostics.txt
cat /etc/os-release >> idps-diagnostics.txt

echo "Diagnostics saved to idps-diagnostics.txt"
```

### Reset to Defaults
```bash
#!/bin/bash
# Reset IDPS to default configuration

# Backup current configuration
sudo cp -r /opt/idps/config /opt/idps/config.backup

# Stop services
sudo systemctl stop idps-monitor

# Reset to default configuration
# (Re-run installation or restore default configs)

# Restart services
sudo systemctl start idps-monitor
```

## Emergency Procedures

### Complete System Disable
```bash
# Stop all IDPS components
sudo systemctl stop idps-monitor
sudo systemctl stop fail2ban

# Disable at boot
sudo systemctl disable idps-monitor
sudo systemctl disable fail2ban

# Remove all firewall rules
sudo ufw --force disable
```

### Emergency Unban All IPs
```bash
#!/bin/bash
# Unban all currently banned IPs

# Fail2Ban
for jail in $(sudo fail2ban-client status | grep "Jail list" | sed "s/.*://;s/,//g"); do
    sudo fail2ban-client set $jail unbanall
done

# UFW
sudo ufw --force reset
sudo ufw default allow incoming
sudo ufw --force enable

# iptables
sudo iptables -F INPUT
```

## Prevention Best Practices

1. **Always test in staging first**
2. **Whitelist admin IPs before deploying**
3. **Start with lenient settings**
4. **Monitor for 1 week before tightening**
5. **Keep console access available**
6. **Document all configuration changes**
7. **Regular backups of configuration**
8. **Set up monitoring alerts**
9. **Review logs weekly**
10. **Keep software updated**
