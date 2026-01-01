# IDPS Testing Guide

## Overview
This guide explains how to test the IDPS system safely and effectively.

## Testing Environment Setup

### 1. Create a Test Environment

**Option A: Local VM**
```bash
# Use VirtualBox, VMware, or similar
# Install Ubuntu Server 20.04+
# Install IDPS following installation guide
```

**Option B: Cloud Instance**
```bash
# Use AWS, DigitalOcean, Linode, etc.
# Spin up Ubuntu instance
# Install IDPS
```

**Important:** Never test in production!

### 2. Configure for Testing

Edit `/opt/idps/config/idps_config.yaml`:
```yaml
detection:
  failed_login_threshold: 3  # Lower for easier testing
  timeframe: 300             # 5 minutes

prevention:
  ban_time: 300             # 5 minutes for quick testing
  
logging:
  level: DEBUG              # Verbose logging
```

## Test Scenarios

### Test 1: Failed Login Detection

**Purpose:** Verify detection of repeated failed login attempts

**Steps:**
1. From a different machine:
   ```bash
   ssh wronguser@test-server-ip
   ```

2. Enter wrong password 3+ times

3. On test server, check detection:
   ```bash
   sudo idps-alerts
   ```

4. Verify IP is blocked:
   ```bash
   sudo idps-blocked
   ```

**Expected Result:**
- Threat logged in `threats.log`
- IP blocked by Fail2Ban and/or UFW
- Alert sent (if configured)

### Test 2: Invalid User Detection

**Purpose:** Test detection of invalid username attempts

**Steps:**
1. Try to SSH with random usernames:
   ```bash
   ssh invaliduser123@test-server-ip
   ssh hacker@test-server-ip
   ssh admin@test-server-ip
   ```

2. Check detection:
   ```bash
   sudo tail -f /opt/idps/logs/threats.log
   ```

**Expected Result:**
- Multiple "invalid_user" threats detected
- IP blocked after threshold reached

### Test 3: Port Scanning Detection

**Purpose:** Detect port scanning activity

**Steps:**
1. From testing machine, run nmap:
   ```bash
   nmap -p 1-100 test-server-ip
   ```

2. Check detection:
   ```bash
   sudo idps-alerts
   ```

**Expected Result:**
- Port scan detected
- High/Critical severity
- IP blocked

### Test 4: Whitelist Functionality

**Purpose:** Verify whitelisted IPs are never blocked

**Steps:**
1. Add test IP to whitelist:
   ```bash
   echo "TEST_IP" | sudo tee -a /opt/idps/config/whitelist.txt
   sudo systemctl restart idps-monitor
   ```

2. Attempt failed logins from that IP

3. Verify not blocked:
   ```bash
   sudo idps-blocked | grep TEST_IP
   ```

**Expected Result:**
- Events detected but not blocked
- IP not in blocked list

### Test 5: Blacklist Functionality

**Purpose:** Verify blacklisted IPs are immediately blocked

**Steps:**
1. Add test IP to blacklist:
   ```bash
   echo "TEST_IP" | sudo tee -a /opt/idps/config/blacklist.txt
   sudo systemctl restart idps-monitor
   ```

2. Try to connect from that IP

**Expected Result:**
- Immediate block
- No threshold checking

### Test 6: Auto-Unban Functionality

**Purpose:** Test automatic unbanning after ban period

**Steps:**
1. Set short ban time:
   ```yaml
   prevention:
     ban_time: 60  # 1 minute
   ```

2. Trigger a ban

3. Wait 60+ seconds

4. Check if unbanned:
   ```bash
   sudo idps-blocked
   ```

**Expected Result:**
- IP banned initially
- IP automatically unbanned after 60 seconds

### Test 7: Alert System

**Purpose:** Verify alerts are sent correctly

**Steps:**
1. Configure email alerts:
   ```yaml
   alerts:
     email_enabled: true
     min_severity: MEDIUM
   ```

2. Trigger a high-severity threat

3. Check email inbox

**Expected Result:**
- Email received with threat details
- Proper formatting
- Correct severity level

### Test 8: Multiple Simultaneous Attacks

**Purpose:** Test system under load

**Steps:**
1. From multiple IPs simultaneously:
   - Failed login attempts
   - Port scans
   - Invalid user attempts

2. Monitor system:
   ```bash
   sudo idps-status
   top -p $(pgrep -f monitor.py)
   ```

**Expected Result:**
- All threats detected
- All malicious IPs blocked
- System remains stable
- Reasonable resource usage

## Automated Test Script

```bash
#!/bin/bash
# IDPS Automated Test Suite

TEST_SERVER="test-server-ip"
TEST_USER="testuser"

echo "===== IDPS Test Suite ====="
echo ""

# Test 1: Failed Login
echo "[Test 1] Testing failed login detection..."
for i in {1..5}; do
    sshpass -p "wrongpassword" ssh -o StrictHostKeyChecking=no $TEST_USER@$TEST_SERVER 2>/dev/null
done
echo "Waiting for detection..."
sleep 10

# Check if blocked
ssh -o StrictHostKeyChecking=no $TEST_USER@$TEST_SERVER "sudo idps-blocked | grep $(curl -s ifconfig.me)"
if [ $? -eq 0 ]; then
    echo "✓ Test 1 PASSED: IP was blocked"
else
    echo "✗ Test 1 FAILED: IP was not blocked"
fi

echo ""
echo "===== Test Suite Complete ====="
```

## Load Testing

### Test System Limits

```bash
#!/bin/bash
# Generate load to test performance

# Simulate 100 failed login attempts
for i in {1..100}; do
    echo "$(date) Failed password for user$i from 192.0.2.$((i % 255))" >> /var/log/auth.log
done

# Monitor performance
sudo idps-status
```

### Measure Detection Latency

```bash
#!/bin/bash
# Measure time from log entry to detection

start_time=$(date +%s)
echo "$(date) Failed password for testuser from 192.0.2.1" >> /var/log/auth.log
sleep 1

# Wait for detection
while ! grep "192.0.2.1" /opt/idps/logs/threats.log &>/dev/null; do
    sleep 0.1
done

end_time=$(date +%s)
latency=$((end_time - start_time))
echo "Detection latency: ${latency}s"
```

## Validation Checklist

After testing, verify:

- [ ] Failed logins detected
- [ ] Invalid users detected
- [ ] Port scans detected
- [ ] IPs blocked correctly
- [ ] Whitelist working
- [ ] Blacklist working
- [ ] Auto-unban working (if enabled)
- [ ] Alerts sent
- [ ] No false positives
- [ ] Logs created properly
- [ ] Service stable under load
- [ ] Resource usage acceptable
- [ ] Configuration changes applied
- [ ] Commands work (idps-status, idps-alerts, etc.)
- [ ] Systemd service starts/stops correctly

## Cleanup After Testing

```bash
# Unban all test IPs
sudo idps-unban TEST_IP

# Clear test data
sudo rm /opt/idps/logs/*.log
sudo touch /opt/idps/logs/{idps.log,threats.log,blocks.log}

# Reset configuration to production values
sudo nano /opt/idps/config/idps_config.yaml

# Restart service
sudo systemctl restart idps-monitor
```

## Best Practices

1. **Use isolated test environment**
2. **Document test results**
3. **Test incrementally** - one feature at a time
4. **Monitor resource usage**
5. **Test edge cases**
6. **Verify logs are accurate**
7. **Test rollback procedures**
8. **Time-bound tests** (set short ban times)
9. **Keep production whitelist** safe
10. **Document any failures**

## Common Test Issues

### Issue: Tests Not Triggering Detection

**Solutions:**
- Lower thresholds temporarily
- Check log files are being monitored
- Verify service is running
- Check debug logs

### Issue: Can't Connect After Test

**Solution:**
```bash
# Emergency unban
sudo systemctl stop idps-monitor
sudo fail2ban-client unban --all
sudo ufw --force reset
sudo systemctl start idps-monitor
```

### Issue: Alerts Not Sending

**Solution:**
- Verify SMTP settings
- Check spam folder
- Test SMTP connection manually
- Review alert cooldown settings

## Reporting Test Results

Document test results:
```markdown
## Test Report

**Date:** 2026-01-01
**Tester:** Your Name
**Environment:** Ubuntu 20.04 VM

### Test Results
- Failed Login Detection: ✓ PASSED
- Port Scan Detection: ✓ PASSED
- Whitelist Function: ✓ PASSED
- Alert System: ✗ FAILED (SMTP issue)

### Issues Found
1. SMTP authentication failing
   - Solution: Updated to app password

### Performance
- CPU Usage: 3%
- Memory Usage: 75MB
- Detection Latency: < 2s

### Recommendations
1. Increase ban_time in production
2. Configure email alerts properly
3. Add monitoring IPs to whitelist
```
