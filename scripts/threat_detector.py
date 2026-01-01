#!/usr/bin/env python3
"""
Threat Detector Module
Detects security threats from analyzed log events
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
import ipaddress

class ThreatDetector:
    def __init__(self, config):
        """Initialize Threat Detector"""
        self.config = config
        self.logger = logging.getLogger('ThreatDetector')
        
        # Track events per IP
        self.ip_events = defaultdict(list)
        
        # Track offense counts for permanent bans
        self.offense_counts = defaultdict(int)
        
        # Whitelist and blacklist
        self.whitelist = set()
        self.blacklist = set()
        
        self.logger.info("Threat Detector initialized")
    
    def load_whitelist(self, file_path, inline_ips):
        """Load whitelist from file and inline config"""
        # Load from file
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.whitelist.add(line)
        except FileNotFoundError:
            self.logger.warning(f"Whitelist file not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading whitelist: {e}")
        
        # Add inline IPs
        for ip in inline_ips:
            self.whitelist.add(ip)
        
        self.logger.info(f"Loaded {len(self.whitelist)} whitelisted IPs")
    
    def load_blacklist(self, file_path, inline_ips):
        """Load blacklist from file and inline config"""
        # Load from file
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.blacklist.add(line)
        except FileNotFoundError:
            self.logger.warning(f"Blacklist file not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading blacklist: {e}")
        
        # Add inline IPs
        for ip in inline_ips:
            self.blacklist.add(ip)
        
        self.logger.info(f"Loaded {len(self.blacklist)} blacklisted IPs")
    
    def is_whitelisted(self, ip):
        """Check if IP is whitelisted"""
        # Check exact match
        if ip in self.whitelist:
            return True
        
        # Check CIDR ranges
        try:
            ip_obj = ipaddress.ip_address(ip)
            for whitelist_entry in self.whitelist:
                if '/' in whitelist_entry:
                    network = ipaddress.ip_network(whitelist_entry, strict=False)
                    if ip_obj in network:
                        return True
        except Exception:
            pass
        
        return False
    
    def is_blacklisted(self, ip):
        """Check if IP is blacklisted"""
        # Check exact match
        if ip in self.blacklist:
            return True
        
        # Check CIDR ranges
        try:
            ip_obj = ipaddress.ip_address(ip)
            for blacklist_entry in self.blacklist:
                if '/' in blacklist_entry:
                    network = ipaddress.ip_network(blacklist_entry, strict=False)
                    if ip_obj in network:
                        return True
        except Exception:
            pass
        
        return False
    
    def detect(self, events):
        """Detect threats from events"""
        threats = []
        
        # Group events by IP
        ip_events_map = defaultdict(list)
        for event in events:
            ip = event.get('ip')
            if ip:
                ip_events_map[ip].append(event)
        
        # Analyze each IP
        for ip, ip_events in ip_events_map.items():
            # Skip whitelisted IPs
            if self.is_whitelisted(ip):
                continue
            
            # Check if blacklisted
            if self.is_blacklisted(ip):
                threats.append({
                    'type': 'blacklisted_ip',
                    'ip': ip,
                    'severity': 'CRITICAL',
                    'details': 'IP is on permanent blacklist',
                    'timestamp': datetime.now()
                })
                continue
            
            # Store events for this IP
            self.ip_events[ip].extend(ip_events)
            
            # Clean old events (older than timeframe)
            self.clean_old_events(ip)
            
            # Run detection algorithms
            threat = self.detect_brute_force(ip)
            if threat:
                threats.append(threat)
            
            threat = self.detect_failed_logins(ip)
            if threat:
                threats.append(threat)
            
            threat = self.detect_invalid_users(ip)
            if threat:
                threats.append(threat)
            
            threat = self.detect_port_scan(ip)
            if threat:
                threats.append(threat)
            
            threat = self.detect_root_attempts(ip)
            if threat:
                threats.append(threat)
            
            threat = self.detect_connection_flood(ip)
            if threat:
                threats.append(threat)
        
        return threats
    
    def clean_old_events(self, ip):
        """Remove events older than the detection timeframe"""
        detection = self.config.get('detection', {})
        timeframe = detection.get('timeframe', 600)  # seconds
        
        cutoff = datetime.now() - timedelta(seconds=timeframe)
        self.ip_events[ip] = [
            event for event in self.ip_events[ip]
            if event.get('timestamp', datetime.min) >= cutoff
        ]
    
    def detect_brute_force(self, ip):
        """Detect brute-force attacks"""
        detection = self.config.get('detection', {})
        threshold = detection.get('brute_force_threshold', 3)
        
        events = self.ip_events[ip]
        failed_attempts = sum(
            1 for event in events
            if event.get('type') in ['failed_password', 'authentication_failure']
        )
        
        if failed_attempts >= threshold:
            self.offense_counts[ip] += 1
            
            severity = 'HIGH' if failed_attempts < threshold * 2 else 'CRITICAL'
            
            return {
                'type': 'brute_force',
                'ip': ip,
                'severity': severity,
                'details': f'{failed_attempts} failed authentication attempts',
                'attempts': failed_attempts,
                'timestamp': datetime.now(),
                'offense_count': self.offense_counts[ip]
            }
        
        return None
    
    def detect_failed_logins(self, ip):
        """Detect repeated failed login attempts"""
        detection = self.config.get('detection', {})
        threshold = detection.get('failed_login_threshold', 5)
        
        events = self.ip_events[ip]
        failed_logins = sum(
            1 for event in events
            if event.get('type') == 'failed_password'
        )
        
        if failed_logins >= threshold:
            self.offense_counts[ip] += 1
            
            return {
                'type': 'repeated_failures',
                'ip': ip,
                'severity': 'MEDIUM',
                'details': f'{failed_logins} failed login attempts',
                'attempts': failed_logins,
                'timestamp': datetime.now(),
                'offense_count': self.offense_counts[ip]
            }
        
        return None
    
    def detect_invalid_users(self, ip):
        """Detect attempts with invalid usernames"""
        detection = self.config.get('detection', {})
        threshold = detection.get('invalid_user_threshold', 3)
        
        events = self.ip_events[ip]
        invalid_attempts = sum(
            1 for event in events
            if event.get('type') == 'invalid_user'
        )
        
        if invalid_attempts >= threshold:
            self.offense_counts[ip] += 1
            
            return {
                'type': 'invalid_user',
                'ip': ip,
                'severity': 'HIGH',
                'details': f'{invalid_attempts} invalid user attempts',
                'attempts': invalid_attempts,
                'timestamp': datetime.now(),
                'offense_count': self.offense_counts[ip]
            }
        
        return None
    
    def detect_port_scan(self, ip):
        """Detect port scanning activity"""
        detection = self.config.get('detection', {})
        threshold = detection.get('port_scan_threshold', 10)
        
        events = self.ip_events[ip]
        scan_indicators = sum(
            1 for event in events
            if event.get('type') in ['port_scan', 'connection_closed', 'refused_connection']
        )
        
        if scan_indicators >= threshold:
            self.offense_counts[ip] += 1
            
            return {
                'type': 'port_scan',
                'ip': ip,
                'severity': 'CRITICAL',
                'details': f'Port scanning activity detected ({scan_indicators} indicators)',
                'indicators': scan_indicators,
                'timestamp': datetime.now(),
                'offense_count': self.offense_counts[ip]
            }
        
        return None
    
    def detect_root_attempts(self, ip):
        """Detect root login attempts"""
        detection = self.config.get('detection', {})
        detect_root = detection.get('detect_root_attempts', True)
        
        if not detect_root:
            return None
        
        events = self.ip_events[ip]
        root_attempts = sum(
            1 for event in events
            if event.get('type') == 'root_login_attempt' or 
            (event.get('type') == 'failed_password' and event.get('user') == 'root')
        )
        
        if root_attempts > 0:
            self.offense_counts[ip] += 1
            
            return {
                'type': 'root_login',
                'ip': ip,
                'severity': 'CRITICAL',
                'details': f'{root_attempts} root login attempts',
                'attempts': root_attempts,
                'timestamp': datetime.now(),
                'offense_count': self.offense_counts[ip]
            }
        
        return None
    
    def detect_connection_flood(self, ip):
        """Detect connection flooding (potential DDoS)"""
        detection = self.config.get('detection', {})
        threshold = detection.get('connection_threshold', 20)
        timeframe = detection.get('connection_timeframe', 60)
        
        # Get events from specific timeframe
        cutoff = datetime.now() - timedelta(seconds=timeframe)
        recent_events = [
            event for event in self.ip_events[ip]
            if event.get('timestamp', datetime.min) >= cutoff
        ]
        
        if len(recent_events) >= threshold:
            self.offense_counts[ip] += 1
            
            return {
                'type': 'connection_flood',
                'ip': ip,
                'severity': 'HIGH',
                'details': f'{len(recent_events)} connections in {timeframe} seconds',
                'connections': len(recent_events),
                'timestamp': datetime.now(),
                'offense_count': self.offense_counts[ip]
            }
        
        return None
    
    def should_permanent_ban(self, ip):
        """Check if IP should be permanently banned"""
        prevention = self.config.get('prevention', {})
        permanent_threshold = prevention.get('permanent_ban_after', 5)
        
        return self.offense_counts[ip] >= permanent_threshold
