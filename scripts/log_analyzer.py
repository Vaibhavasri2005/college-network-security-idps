#!/usr/bin/env python3
"""
Log Analyzer Module
Analyzes system logs for security events
"""

import re
import os
from datetime import datetime, timedelta
from collections import deque
import logging

class LogAnalyzer:
    def __init__(self, config):
        """Initialize Log Analyzer"""
        self.config = config
        self.logger = logging.getLogger('LogAnalyzer')
        
        # Log file positions (for tracking where we left off)
        self.file_positions = {}
        
        # Event buffer
        self.event_buffer = deque(maxlen=10000)
        
        # Compiled regex patterns for performance
        self.patterns = self.compile_patterns()
        
        self.logger.info("Log Analyzer initialized")
    
    def compile_patterns(self):
        """Compile regex patterns for log parsing"""
        patterns = {
            'failed_password': re.compile(
                r'Failed password for (?:invalid user )?(\S+) from ([\d\.]+) port (\d+)'
            ),
            'invalid_user': re.compile(
                r'Invalid user (\S+) from ([\d\.]+) port (\d+)'
            ),
            'authentication_failure': re.compile(
                r'authentication failure.*rhost=([\d\.]+).*user=(\S+)'
            ),
            'root_login_attempt': re.compile(
                r'ROOT LOGIN REFUSED.*FROM ([\d\.]+)'
            ),
            'accepted_password': re.compile(
                r'Accepted password for (\S+) from ([\d\.]+) port (\d+)'
            ),
            'connection_closed': re.compile(
                r'Connection closed by (?:authenticating user )?(?:\S+ )?([\d\.]+)'
            ),
            'disconnect': re.compile(
                r'Received disconnect from ([\d\.]+):'
            ),
            'max_auth_attempts': re.compile(
                r'maximum authentication attempts exceeded.*from ([\d\.]+)'
            ),
            'pam_failure': re.compile(
                r'PAM.*authentication failure.*rhost=([\d\.]+)'
            ),
            'refused_connection': re.compile(
                r'refused connect from.*\[([\d\.]+)\]'
            ),
            'port_scan': re.compile(
                r'Did not receive identification string from ([\d\.]+)'
            ),
        }
        
        return patterns
    
    def analyze(self):
        """Analyze configured log files"""
        events = []
        
        monitoring = self.config.get('monitoring', {})
        log_files = monitoring.get('log_files', ['/var/log/auth.log'])
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    file_events = self.analyze_log_file(log_file)
                    events.extend(file_events)
                except Exception as e:
                    self.logger.error(f"Error analyzing {log_file}: {e}")
            else:
                self.logger.warning(f"Log file not found: {log_file}")
        
        return events
    
    def analyze_log_file(self, log_file):
        """Analyze a single log file"""
        events = []
        
        try:
            # Get last position
            last_position = self.file_positions.get(log_file, 0)
            
            with open(log_file, 'r') as f:
                # Seek to last position
                f.seek(last_position)
                
                # Read new lines
                for line in f:
                    event = self.parse_log_line(line, log_file)
                    if event:
                        events.append(event)
                        self.event_buffer.append(event)
                
                # Update position
                self.file_positions[log_file] = f.tell()
        
        except Exception as e:
            self.logger.error(f"Error reading {log_file}: {e}")
        
        return events
    
    def parse_log_line(self, line, log_file):
        """Parse a single log line"""
        # Extract timestamp
        timestamp = self.extract_timestamp(line)
        
        # Try each pattern
        for event_type, pattern in self.patterns.items():
            match = pattern.search(line)
            if match:
                event = {
                    'type': event_type,
                    'timestamp': timestamp,
                    'raw_log': line.strip(),
                    'source_file': log_file
                }
                
                # Extract matched groups
                if event_type in ['failed_password', 'invalid_user', 'accepted_password']:
                    event['user'] = match.group(1)
                    event['ip'] = match.group(2)
                    event['port'] = match.group(3)
                elif event_type == 'authentication_failure':
                    event['ip'] = match.group(1)
                    event['user'] = match.group(2)
                else:
                    # Most patterns have IP as first group
                    event['ip'] = match.group(1)
                
                return event
        
        # Check for custom patterns
        custom_events = self.check_custom_patterns(line, timestamp, log_file)
        if custom_events:
            return custom_events
        
        return None
    
    def extract_timestamp(self, line):
        """Extract timestamp from log line"""
        try:
            # Try common syslog format: "Jan 1 12:00:00"
            match = re.match(r'(\w+\s+\d+\s+\d+:\d+:\d+)', line)
            if match:
                timestamp_str = match.group(1)
                # Add current year
                year = datetime.now().year
                timestamp_str = f"{year} {timestamp_str}"
                return datetime.strptime(timestamp_str, '%Y %b %d %H:%M:%S')
        except Exception:
            pass
        
        return datetime.now()
    
    def check_custom_patterns(self, line, timestamp, log_file):
        """Check for custom user-defined patterns"""
        advanced = self.config.get('advanced', {})
        custom_patterns = advanced.get('custom_patterns', [])
        
        for pattern_config in custom_patterns:
            try:
                pattern = re.compile(pattern_config['pattern'])
                match = pattern.search(line)
                
                if match:
                    event = {
                        'type': 'custom_pattern',
                        'timestamp': timestamp,
                        'raw_log': line.strip(),
                        'source_file': log_file,
                        'action': pattern_config.get('action', 'log')
                    }
                    
                    # Extract named groups
                    event.update(match.groupdict())
                    
                    return event
            except Exception as e:
                self.logger.error(f"Error in custom pattern: {e}")
        
        return None
    
    def get_recent_events(self, minutes=10):
        """Get events from the last N minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [
            event for event in self.event_buffer
            if event.get('timestamp', datetime.min) >= cutoff
        ]
        return recent
    
    def get_events_by_ip(self, ip, minutes=10):
        """Get all events from a specific IP in the last N minutes"""
        recent = self.get_recent_events(minutes)
        ip_events = [event for event in recent if event.get('ip') == ip]
        return ip_events
    
    def get_events_by_type(self, event_type, minutes=10):
        """Get all events of a specific type in the last N minutes"""
        recent = self.get_recent_events(minutes)
        type_events = [event for event in recent if event.get('type') == event_type]
        return type_events
