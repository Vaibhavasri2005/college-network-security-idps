#!/usr/bin/env python3
"""
IDPS Main Monitoring Daemon
Continuously monitors system logs for security threats
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path
from datetime import datetime
import yaml

# Add parent directory to path for database import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import custom modules
from log_analyzer import LogAnalyzer
from threat_detector import ThreatDetector
from alert_sender import AlertSender
from database.models import IDPSDatabase

class IDPSMonitor:
    def __init__(self, config_path='config/idps_config.yaml'):
        """Initialize IDPS Monitor"""
        self.running = False
        self.config = self.load_config(config_path)
        self.setup_logging()
        
        # Initialize database
        self.database = IDPSDatabase('database/idps.db')
        
        self.log_analyzer = LogAnalyzer(self.config)
        self.threat_detector = ThreatDetector(self.config)
        self.alert_sender = AlertSender(self.config)
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("IDPS Monitor initialized with database")
    
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('main_log', 'logs/idps.log')
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Create logs directory if it doesn't exist
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('IDPS-Monitor')
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def start(self):
        """Start the monitoring daemon"""
        self.logger.info("Starting IDPS Monitor...")
        self.running = True
        
        # Load whitelist and blacklist
        self.load_ip_lists()
        
        # Main monitoring loop
        scan_interval = self.config.get('monitoring', {}).get('scan_interval', 5)
        
        while self.running:
            try:
                # Analyze logs for threats
                events = self.log_analyzer.analyze()
                
                if events:
                    self.logger.info(f"Found {len(events)} events to analyze")
                    
                    # Detect threats
                    threats = self.threat_detector.detect(events)
                    
                    if threats:
                        self.logger.warning(f"Detected {len(threats)} threats")
                        
                        # Process each threat
                        for threat in threats:
                            self.handle_threat(threat)
                
                # Sleep before next scan
                time.sleep(scan_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(scan_interval)
    
    def load_ip_lists(self):
        """Load whitelist and blacklist"""
        whitelist_config = self.config.get('whitelist', {})
        if whitelist_config.get('enabled', True):
            whitelist_file = whitelist_config.get('file', 'config/whitelist.txt')
            inline_ips = whitelist_config.get('ips', [])
            self.threat_detector.load_whitelist(whitelist_file, inline_ips)
        
        blacklist_config = self.config.get('blacklist', {})
        if blacklist_config.get('enabled', True):
            blacklist_file = blacklist_config.get('file', 'config/blacklist.txt')
            inline_ips = blacklist_config.get('ips', [])
            self.threat_detector.load_blacklist(blacklist_file, inline_ips)
    
    def handle_threat(self, threat):
        """Handle detected threat"""
        ip = threat.get('ip')
        threat_type = threat.get('type')
        severity = threat.get('severity')
        details = threat.get('details', '')
        offense_count = threat.get('offense_count', 1)
        
        self.logger.warning(
            f"Threat detected - Type: {threat_type}, IP: {ip}, "
            f"Severity: {severity}"
        )
        
        # Log threat to file
        self.log_threat(threat)
        
        # Store threat in database
        blocked = self.should_block(threat)
        threat_id = self.database.add_threat(
            threat_type=threat_type,
            ip_address=ip,
            severity=severity,
            details=details,
            offense_count=offense_count,
            blocked=blocked
        )
        
        # Add system event
        self.database.add_system_event(
            event_type='threat_detected',
            description=f"{threat_type} from {ip}",
            ip_address=ip
        )
        
        # Take prevention action
        if blocked:
            self.block_ip(ip, threat)
        
        # Send alert if configured
        if self.should_alert(threat):
            self.alert_sender.send_alert(threat)
    
    def log_threat(self, threat):
        """Log threat to threats.log"""
        threat_log = self.config.get('logging', {}).get('threat_log', 'logs/threats.log')
        
        try:
            with open(threat_log, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = (
                    f"{timestamp} | {threat.get('severity')} | "
                    f"{threat.get('type')} | {threat.get('ip')} | "
                    f"Details: {threat.get('details', 'N/A')}\n"
                )
                f.write(log_entry)
        except Exception as e:
            self.logger.error(f"Error logging threat: {e}")
    
    def should_block(self, threat):
        """Determine if IP should be blocked"""
        prevention = self.config.get('prevention', {})
        
        # Check if prevention is enabled
        if not (prevention.get('use_fail2ban') or prevention.get('use_ufw') 
                or prevention.get('use_iptables')):
            return False
        
        # Check severity threshold
        severity_order = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        threat_severity = severity_order.get(threat.get('severity'), 0)
        
        # Block MEDIUM and above by default
        return threat_severity >= 2
    
    def block_ip(self, ip, threat):
        """Block an IP address"""
        self.logger.info(f"Blocking IP: {ip}")
        
        prevention = self.config.get('prevention', {})
        ban_time = prevention.get('ban_time', 3600)
        
        # Log the block
        self.log_block(ip, threat, ban_time)
        
        # Use configured blocking methods
        if prevention.get('use_fail2ban', True):
            self.block_with_fail2ban(ip, threat)
        
        if prevention.get('use_ufw', True):
            self.block_with_ufw(ip)
        
        if prevention.get('use_iptables', False):
            self.block_with_iptables(ip)
    
    def log_block(self, ip, threat, ban_time):
        """Log blocked IP"""
        block_log = self.config.get('logging', {}).get('block_log', 'logs/blocks.log')
        
        try:
            with open(block_log, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = (
                    f"{timestamp} | {ip} | {threat.get('type')} | "
                    f"Ban Duration: {ban_time}s | Details: {threat.get('details', 'N/A')}\n"
                )
                f.write(log_entry)
            
            # Store in database
            self.database.add_blocked_ip(
                ip_address=ip,
                reason=f"{threat.get('type')} - {threat.get('details', 'Security threat')}"
            )
            
            # Add system event
            self.database.add_system_event(
                event_type='ip_blocked',
                description=f"Blocked {ip} for {ban_time}s",
                ip_address=ip
            )
            
        except Exception as e:
            self.logger.error(f"Error logging block: {e}")
    
    def block_with_fail2ban(self, ip, threat):
        """Block IP using Fail2Ban"""
        try:
            jail = self.get_appropriate_jail(threat)
            os.system(f"fail2ban-client set {jail} banip {ip}")
            self.logger.info(f"Blocked {ip} using Fail2Ban jail: {jail}")
        except Exception as e:
            self.logger.error(f"Error blocking with Fail2Ban: {e}")
    
    def block_with_ufw(self, ip):
        """Block IP using UFW"""
        try:
            os.system(f"ufw deny from {ip}")
            self.logger.info(f"Blocked {ip} using UFW")
        except Exception as e:
            self.logger.error(f"Error blocking with UFW: {e}")
    
    def block_with_iptables(self, ip):
        """Block IP using iptables"""
        try:
            os.system(f"iptables -A INPUT -s {ip} -j DROP")
            self.logger.info(f"Blocked {ip} using iptables")
        except Exception as e:
            self.logger.error(f"Error blocking with iptables: {e}")
    
    def get_appropriate_jail(self, threat):
        """Get appropriate Fail2Ban jail based on threat type"""
        threat_type = threat.get('type', '').lower()
        
        jail_map = {
            'brute_force': 'idps-brute-force',
            'port_scan': 'idps-port-scan',
            'ssh_attack': 'idps-ssh',
            'invalid_user': 'idps-invalid-user',
            'root_login': 'idps-root-login',
        }
        
        return jail_map.get(threat_type, 'idps-ssh')
    
    def should_alert(self, threat):
        """Determine if alert should be sent"""
        alert_config = self.config.get('alerts', {})
        
        if not alert_config.get('email_enabled', False):
            return False
        
        # Check if threat type is in alert list
        alert_on = alert_config.get('alert_on', [])
        threat_type = threat.get('type', '')
        
        if threat_type not in alert_on and 'all' not in alert_on:
            return False
        
        # Check severity threshold
        min_severity = alert_config.get('min_severity', 'HIGH')
        severity_order = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        
        threat_severity = severity_order.get(threat.get('severity'), 0)
        min_severity_level = severity_order.get(min_severity, 3)
        
        return threat_severity >= min_severity_level

def main():
    """Main entry point"""
    print("=" * 60)
    print("IDPS - Intrusion Detection and Prevention System")
    print("=" * 60)
    
    # Check if running as root
    if os.geteuid() != 0:
        print("Warning: IDPS should be run as root for full functionality")
        print("Some features may not work without root privileges")
    
    # Initialize and start monitor
    try:
        monitor = IDPSMonitor()
        monitor.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
