# IDPS System Architecture

## Overview
This document describes the technical architecture of the Intrusion Detection and Prevention System (IDPS).

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         IDPS System                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐                                           │
│  │  Data Sources    │                                           │
│  │  /var/log/*      │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────┐      ┌────────────────┐                  │
│  │  Log Analyzer    │─────▶│ Event Queue    │                  │
│  │  (Python)        │      └───────┬────────┘                  │
│  └──────────────────┘              │                            │
│           │                         │                            │
│           ▼                         ▼                            │
│  ┌──────────────────┐      ┌────────────────┐                  │
│  │ Threat Detector  │◀─────│ Historical DB  │                  │
│  │ (Python)         │      └────────────────┘                  │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────────────────────────┐                       │
│  │     Decision Engine                  │                       │
│  │  - Whitelist Check                   │                       │
│  │  - Blacklist Check                   │                       │
│  │  - Threat Scoring                    │                       │
│  │  - Action Determination              │                       │
│  └────────┬─────────────────────────────┘                       │
│           │                                                      │
│           ├──────────────┬──────────────┬──────────────┐        │
│           ▼              ▼              ▼              ▼        │
│  ┌─────────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Fail2Ban   │  │    UFW    │  │ iptables │  │  Alerts  │   │
│  │Integration  │  │Integration│  │Integration│  │  System  │   │
│  └─────────────┘  └───────────┘  └──────────┘  └──────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Log Monitoring Layer

#### Log Analyzer (`scripts/log_analyzer.py`)

**Purpose:** Continuously monitors and parses system logs

**Key Features:**
- Real-time log tailing with position tracking
- Efficient regex-based pattern matching
- Event buffering with sliding window
- Multiple log file support

**Data Flow:**
```
System Logs → File Reader → Pattern Matcher → Event Parser → Event Queue
```

**Key Methods:**
- `analyze()`: Main analysis loop
- `analyze_log_file()`: Processes individual log files
- `parse_log_line()`: Extracts structured data from log lines
- `get_events_by_ip()`: Retrieves events for specific IP

**Performance Optimizations:**
- Compiled regex patterns (cached)
- File position tracking (avoids re-reading)
- Bounded event buffer (prevents memory overflow)
- Efficient timestamp extraction

### 2. Detection Engine

#### Threat Detector (`scripts/threat_detector.py`)

**Purpose:** Analyzes events to identify security threats

**Detection Algorithms:**

1. **Brute Force Detection**
   - Counts failed authentication attempts
   - Considers time window
   - Threshold-based triggering

2. **Failed Login Detection**
   - Tracks failed password attempts
   - Distinguishes from brute force by pattern
   - Lower threshold for invalid users

3. **Port Scan Detection**
   - Identifies multiple connection attempts
   - Detects rapid port probing
   - Recognizes scan signatures

4. **Root Login Detection**
   - Zero-tolerance for root attempts
   - Immediate flagging
   - High severity assignment

5. **Connection Flood Detection**
   - Monitors connection rate
   - Detects DDoS patterns
   - Adaptive thresholds

**Threat Scoring:**
```python
Severity Levels:
- LOW: 1 point    (unusual activity)
- MEDIUM: 2 points (suspicious activity)
- HIGH: 3 points   (likely attack)
- CRITICAL: 4 points (confirmed attack)
```

**State Management:**
- IP-based event tracking
- Offense count tracking
- Whitelist/blacklist caching

### 3. Prevention Layer

#### IP Blocker (`scripts/ip_blocker.sh`)

**Purpose:** Implements IP blocking across multiple systems

**Blocking Methods:**

1. **Fail2Ban Integration**
   - Dynamic jail assignment
   - Temporary and permanent bans
   - Automatic unban support

2. **UFW (Uncomplicated Firewall)**
   - Deny rules for malicious IPs
   - Persistent across reboots
   - Easy management

3. **iptables**
   - Low-level packet filtering
   - High performance
   - Maximum flexibility

**Block Decision Logic:**
```
IF IP in whitelist THEN
    Skip blocking
ELSIF IP in blacklist THEN
    Permanent block
ELSIF threat severity >= threshold THEN
    Temporary block
    IF offense count > permanent_threshold THEN
        Permanent block
```

### 4. Alert System

#### Alert Sender (`scripts/alert_sender.py`)

**Purpose:** Sends security notifications via multiple channels

**Supported Channels:**
- Email (SMTP)
- Slack (Webhooks)
- Telegram (Bot API)
- Generic Webhooks

**Alert Flow:**
```
Threat Detected → Severity Check → Cooldown Check → Template Selection
                                                   ↓
                                        Format Message → Send Alert
```

**Features:**
- Template-based messaging
- HTML email support
- Alert cooldown (prevents spam)
- Multiple recipient support
- Severity-based filtering

### 5. Main Controller

#### IDPS Monitor (`scripts/monitor.py`)

**Purpose:** Orchestrates all system components

**Main Loop:**
```python
while running:
    # 1. Analyze logs
    events = log_analyzer.analyze()
    
    # 2. Detect threats
    threats = threat_detector.detect(events)
    
    # 3. Handle threats
    for threat in threats:
        if should_block(threat):
            block_ip(threat['ip'])
        
        if should_alert(threat):
            send_alert(threat)
    
    # 4. Sleep
    time.sleep(scan_interval)
```

**Lifecycle Management:**
- Graceful shutdown handling
- Configuration reloading
- State persistence
- Error recovery

## Data Structures

### Event Object
```python
{
    'type': str,              # Event type (failed_password, etc.)
    'timestamp': datetime,     # When it occurred
    'ip': str,                # Source IP address
    'user': str,              # Username (if applicable)
    'port': int,              # Port number (if applicable)
    'raw_log': str,           # Original log line
    'source_file': str        # Which log file
}
```

### Threat Object
```python
{
    'type': str,              # Threat type
    'ip': str,                # Attacking IP
    'severity': str,          # LOW, MEDIUM, HIGH, CRITICAL
    'details': str,           # Human-readable description
    'attempts': int,          # Number of attempts
    'timestamp': datetime,     # When detected
    'offense_count': int      # Total offenses by this IP
}
```

## Integration Points

### Fail2Ban Integration

**Files:**
- Filters: `/etc/fail2ban/filter.d/custom-*.conf`
- Jails: `/etc/fail2ban/jail.d/idps-jail.local`

**API:**
```bash
fail2ban-client set <jail> banip <ip>
fail2ban-client set <jail> unbanip <ip>
fail2ban-client status <jail>
```

### UFW Integration

**Commands:**
```bash
ufw deny from <ip>
ufw delete deny from <ip>
ufw status numbered
```

### System Logs

**Monitored Logs:**
- `/var/log/auth.log` (Ubuntu/Debian)
- `/var/log/secure` (RHEL/CentOS)
- `/var/log/syslog` (General system logs)
- Custom application logs (configurable)

## Security Considerations

### Whitelist/Blacklist Management

**Whitelist Priority:**
1. Exact IP match
2. CIDR range match
3. Always bypass all checks

**Blacklist Handling:**
1. Loaded at startup
2. Checked before any processing
3. Immediate permanent block

### Attack Surface

**Potential Vulnerabilities:**
- Log injection attacks (mitigated by input validation)
- Regex DoS (mitigated by compiled patterns and timeouts)
- Configuration tampering (requires root access)
- Resource exhaustion (mitigated by limits)

**Mitigations:**
- Run as root only (necessary for firewall control)
- Strict file permissions
- Input validation and sanitization
- Resource limits (CPU, memory)
- Bounded data structures

## Performance Characteristics

### Resource Usage

**CPU:**
- Idle: ~1%
- Active monitoring: 2-5%
- Under attack: 5-15%

**Memory:**
- Base: ~50 MB
- With cache: ~100 MB
- Maximum: ~200 MB (configurable limit)

**Disk I/O:**
- Log reading: Sequential, minimal
- Log writing: Append-only, buffered
- Configuration: Rarely accessed

### Scalability

**Horizontal Scaling:**
Not supported (single-server design)

**Vertical Scaling:**
- Supports multiple CPU cores (threading)
- Memory usage scales with event buffer size
- Can handle high-traffic servers

**Throughput:**
- Can process 1000+ log entries per second
- Detection latency: <1 second
- Blocking latency: <2 seconds

## Failure Modes

### Graceful Degradation

1. **Log File Unavailable:**
   - Skip that log file
   - Continue monitoring others
   - Log warning

2. **Fail2Ban Down:**
   - Fall back to UFW/iptables
   - Continue detection
   - Alert administrator

3. **Alert System Failed:**
   - Log locally
   - Continue protection
   - Retry alerts periodically

### Recovery Mechanisms

- Automatic service restart (systemd)
- State recovery from logs
- Configuration validation on startup
- Graceful shutdown on errors

## Extension Points

### Custom Detection Rules

Add to `idps_config.yaml`:
```yaml
advanced:
  custom_patterns:
    - pattern: "regex pattern here"
      action: block
      threshold: 3
```

### Custom Alert Channels

Extend `alert_sender.py`:
```python
def send_custom_alert(self, threat):
    # Your implementation
    pass
```

### Custom Blocking Methods

Extend `ip_blocker.sh`:
```bash
block_with_custom() {
    # Your implementation
}
```

## Future Enhancements

### Planned Features
- Machine learning anomaly detection
- GeoIP-based blocking
- Distributed deployment support
- Web dashboard for monitoring
- API for external integrations
- Threat intelligence feed integration

### Extensibility
- Plugin architecture for custom detectors
- Modular alert channels
- Configurable detection algorithms
- External database support

## Maintenance

### Regular Tasks
- Log rotation (automatic)
- Configuration backup (manual)
- Whitelist updates (as needed)
- Software updates (monthly)
- Performance monitoring (weekly)

### Monitoring Points
- Service uptime
- Detection accuracy
- False positive rate
- Resource usage
- Alert delivery

## Compliance

### Logging Standards
- Structured logging format
- Timestamp precision
- Audit trail preservation
- Log retention policies

### Security Standards
- Follows OWASP guidelines
- Implements defense in depth
- Maintains least privilege
- Regular security updates
