# IDPS Deployment Checklist

Use this checklist when deploying IDPS to a new server.

## Pre-Deployment

### Server Preparation
- [ ] Ubuntu 20.04 LTS or later installed
- [ ] System fully updated (`apt update && apt upgrade`)
- [ ] Root or sudo access available
- [ ] SSH access working
- [ ] Backup access method available (console)
- [ ] Server has internet connectivity
- [ ] Minimum 1GB RAM available
- [ ] 500MB disk space free

### Network Information
- [ ] Document current IP address: ________________
- [ ] Document admin IP addresses:
  - [ ] IP 1: ________________
  - [ ] IP 2: ________________
  - [ ] Office network: ________________
- [ ] Document VPN gateway (if any): ________________
- [ ] Document monitoring service IPs: ________________

### Pre-Installation Backup
- [ ] Backup current firewall rules: `iptables-save > iptables.backup`
- [ ] Backup current SSH config: `cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup`
- [ ] Document current Fail2Ban config (if installed)
- [ ] Take server snapshot (if cloud provider supports it)

## Installation

### Download and Setup
- [ ] Download/clone IDPS project to server
- [ ] Verify all files present: `ls -R "IDS project/"`
- [ ] Make install script executable: `chmod +x scripts/install.sh`

### Run Installation
- [ ] Run installation as root: `sudo ./scripts/install.sh`
- [ ] Installation completed without errors
- [ ] Service created successfully
- [ ] Command shortcuts work: `which idps-status`

### Post-Installation Verification
- [ ] Service running: `systemctl status idps-monitor`
- [ ] Fail2Ban active: `systemctl status fail2ban`
- [ ] UFW active: `ufw status`
- [ ] Logs created: `ls -l /opt/idps/logs/`
- [ ] Configuration files present: `ls -l /opt/idps/config/`

## Initial Configuration

### Whitelist Configuration
- [ ] Open whitelist: `nano /opt/idps/config/whitelist.txt`
- [ ] Add localhost (should already be there)
- [ ] Add your current IP
- [ ] Add all admin IPs
- [ ] Add office network ranges
- [ ] Add VPN gateway
- [ ] Add monitoring service IPs
- [ ] Save and close

### Security Settings
- [ ] Review detection thresholds: `nano /opt/idps/config/idps_config.yaml`
- [ ] Set appropriate security level (start moderate):
  - [ ] failed_login_threshold: 5
  - [ ] brute_force_threshold: 3
  - [ ] timeframe: 600
- [ ] Set ban duration: ban_time: 3600 (1 hour)
- [ ] Configure permanent ban threshold: permanent_ban_after: 5
- [ ] Save configuration

### Alert Configuration (Optional)
- [ ] Decide if email alerts needed
- [ ] If yes, configure: `nano /opt/idps/config/alert_config.yaml`
  - [ ] SMTP server settings
  - [ ] Sender email
  - [ ] Recipient emails
  - [ ] Enable alerts: email_enabled: true
- [ ] Test alert delivery (optional): `python3 /opt/idps/scripts/alert_sender.py --test`

### Firewall Rules
- [ ] Verify SSH allowed: `ufw status | grep 22`
- [ ] Add any required service ports:
  - [ ] HTTP: `ufw allow 80/tcp`
  - [ ] HTTPS: `ufw allow 443/tcp`
  - [ ] Custom ports: `ufw allow XXXX/tcp`
- [ ] Verify UFW default policies: `ufw status verbose`

### Service Configuration
- [ ] Enable service at boot: `systemctl enable idps-monitor`
- [ ] Start service: `systemctl start idps-monitor`
- [ ] Verify service running: `systemctl status idps-monitor`
- [ ] Check logs for errors: `tail -f /opt/idps/logs/idps.log`

## Testing

### Functional Testing
- [ ] Check system status: `idps-status`
- [ ] Verify all components green
- [ ] Test from external IP (different machine):
  - [ ] Try wrong password 3 times
  - [ ] Wait 30 seconds
  - [ ] Check if detected: `idps-alerts`
  - [ ] Check if blocked: `idps-blocked`
- [ ] Test unban function: `idps-unban <test-ip>`
- [ ] Verify unban worked

### Whitelist Testing
- [ ] From whitelisted IP, try failed logins
- [ ] Verify NOT blocked
- [ ] Check event still logged: `tail /opt/idps/logs/idps.log`

### Alert Testing (if configured)
- [ ] Trigger high-severity threat
- [ ] Check email received
- [ ] Verify alert format correct
- [ ] Test alert cooldown working

## Monitoring Setup

### Initial Monitoring
- [ ] Set calendar reminder to check daily for first week
- [ ] Set calendar reminder to check weekly after that
- [ ] Create monitoring script (optional):
```bash
#!/bin/bash
idps-status
echo ""
idps-alerts 10
echo ""
idps-blocked
```
- [ ] Save as `/usr/local/bin/daily-idps-check`
- [ ] Make executable: `chmod +x /usr/local/bin/daily-idps-check`

### Log Rotation
- [ ] Verify log rotation configured: `cat /etc/logrotate.d/idps`
- [ ] Test log rotation: `logrotate -f /etc/logrotate.d/idps`

## Documentation

### Server Documentation
- [ ] Document IDPS version installed
- [ ] Document installation date
- [ ] Document initial configuration settings
- [ ] Document any customizations made
- [ ] Document whitelisted IPs
- [ ] Document emergency procedures
- [ ] Share with team members

### Create Runbook
Create a quick reference card with:
- [ ] How to check status
- [ ] How to view alerts
- [ ] How to unban an IP
- [ ] Emergency disable procedure
- [ ] Contact information

## First Week Checklist

### Daily Checks (Days 1-7)
- [ ] Day 1: Check status, review threats
- [ ] Day 2: Check status, review threats
- [ ] Day 3: Check status, review threats
- [ ] Day 4: Check status, review threats
- [ ] Day 5: Check status, review threats
- [ ] Day 6: Check status, review threats
- [ ] Day 7: Full review and tuning

### Week 1 Review
- [ ] Review all detected threats
- [ ] Check for false positives
- [ ] Verify legitimate IPs not blocked
- [ ] Check resource usage: `top`, `free -h`
- [ ] Review logs for any errors
- [ ] Adjust thresholds if needed
- [ ] Update whitelist if needed

## Tuning (After 1 Week)

### Performance Review
- [ ] Check CPU usage: `top -p $(pgrep -f monitor.py)`
- [ ] Check memory usage: `ps aux | grep monitor.py`
- [ ] Check disk usage: `du -sh /opt/idps/logs/`
- [ ] Verify acceptable performance

### Security Review
- [ ] Count total threats detected: `wc -l /opt/idps/logs/threats.log`
- [ ] Count IPs blocked: `wc -l /opt/idps/logs/blocks.log`
- [ ] Review false positive rate
- [ ] Decide if thresholds need adjustment

### Threshold Adjustment (if needed)
If too many false positives:
- [ ] Increase thresholds
- [ ] Extend timeframes
- [ ] Add more IPs to whitelist

If missing real threats:
- [ ] Decrease thresholds
- [ ] Reduce timeframes
- [ ] Enable more detection rules

### Configuration Update
- [ ] Apply threshold changes
- [ ] Restart service: `systemctl restart idps-monitor`
- [ ] Monitor for another week
- [ ] Repeat tuning as needed

## Ongoing Maintenance

### Weekly Tasks
- [ ] Check system status
- [ ] Review threat alerts
- [ ] Check blocked IPs
- [ ] Review resource usage
- [ ] Check for system updates

### Monthly Tasks
- [ ] Review all logs
- [ ] Update whitelist if needed
- [ ] Check for IDPS updates
- [ ] Review and clean old logs
- [ ] Test backup/recovery procedures
- [ ] Review and update documentation

### Quarterly Tasks
- [ ] Full security audit
- [ ] Review and update detection rules
- [ ] Test all alert channels
- [ ] Review false positive trends
- [ ] Performance optimization review
- [ ] Team training/refresh

## Emergency Procedures

### If Server Becomes Unresponsive
1. [ ] Access via console
2. [ ] Check if IDPS causing issue: `systemctl status idps-monitor`
3. [ ] Temporarily disable: `systemctl stop idps-monitor`
4. [ ] Investigate root cause
5. [ ] Fix and re-enable

### If Legitimate User Blocked
1. [ ] Verify identity
2. [ ] Unban: `idps-unban <IP>`
3. [ ] Add to whitelist if appropriate
4. [ ] Investigate why blocked

### If System Compromised
1. [ ] Stop IDPS: `systemctl stop idps-monitor`
2. [ ] Preserve logs: `tar -czf idps-logs-backup.tar.gz /opt/idps/logs/`
3. [ ] Perform incident response
4. [ ] After cleanup, update rules
5. [ ] Re-enable IDPS

## Completion

### Final Verification
- [ ] All checklist items completed
- [ ] System running smoothly
- [ ] No errors in logs
- [ ] Team trained
- [ ] Documentation complete
- [ ] Monitoring established

### Sign-Off
- **Deployed by:** ________________
- **Date:** ________________
- **Server:** ________________
- **Version:** ________________
- **Reviewed by:** ________________

## Additional Notes

Record any issues, customizations, or important information:

_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________

---

**Deployment Status:** [ ] Complete [ ] In Progress [ ] Pending

**Next Review Date:** ________________
