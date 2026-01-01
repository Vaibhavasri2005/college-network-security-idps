#!/usr/bin/env python3
"""
Database Models for IDPS
Handles all database operations
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
import secrets

class IDPSDatabase:
    def __init__(self, db_path='database/idps.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.logger = logging.getLogger('IDPSDatabase')
        
        # Create database directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        self.logger.info(f"Database initialized at {db_path}")
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        try:
            # Read and execute schema
            schema_file = Path(__file__).parent / 'schema.sql'
            
            if schema_file.exists():
                with open(schema_file, 'r') as f:
                    schema = f.read()
                
                conn = self.get_connection()
                conn.executescript(schema)
                conn.commit()
                conn.close()
            else:
                self.logger.warning("Schema file not found, creating basic schema")
                self.create_basic_schema()
        
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    def create_basic_schema(self):
        """Create basic schema if schema.sql not found"""
        conn = self.get_connection()
        
        # Create threats table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_type VARCHAR(50) NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                details TEXT,
                offense_count INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                blocked BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create blocked_ips table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address VARCHAR(45) UNIQUE NOT NULL,
                reason VARCHAR(100),
                blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== THREAT OPERATIONS ====================
    
    def add_threat(self, threat_type, ip_address, severity, details, offense_count=1, blocked=False):
        """Add a new threat to database"""
        try:
            conn = self.get_connection()
            cursor = conn.execute('''
                INSERT INTO threats (threat_type, ip_address, severity, details, offense_count, blocked)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (threat_type, ip_address, severity, details, offense_count, blocked))
            
            threat_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Threat added: {threat_type} from {ip_address}")
            return threat_id
        
        except Exception as e:
            self.logger.error(f"Error adding threat: {e}")
            return None
    
    def get_recent_threats(self, limit=50):
        """Get recent threats"""
        try:
            conn = self.get_connection()
            cursor = conn.execute('''
                SELECT * FROM threats
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            threats = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return threats
        
        except Exception as e:
            self.logger.error(f"Error getting threats: {e}")
            return []
    
    def get_threats_by_severity(self, severity):
        """Get threats by severity level"""
        try:
            conn = self.get_connection()
            cursor = conn.execute('''
                SELECT * FROM threats
                WHERE severity = ?
                ORDER BY timestamp DESC
            ''', (severity,))
            
            threats = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return threats
        
        except Exception as e:
            self.logger.error(f"Error getting threats by severity: {e}")
            return []
    
    def get_threat_statistics(self, days=7):
        """Get threat statistics for the last N days"""
        try:
            conn = self.get_connection()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor = conn.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as count,
                    threat_type,
                    severity
                FROM threats
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp), threat_type, severity
                ORDER BY date DESC
            ''', (cutoff_date,))
            
            stats = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error getting threat statistics: {e}")
            return []
    
    # ==================== BLOCKED IP OPERATIONS ====================
    
    def add_blocked_ip(self, ip_address, reason):
        """Add an IP to blocked list"""
        try:
            conn = self.get_connection()
            conn.execute('''
                INSERT OR REPLACE INTO blocked_ips (ip_address, reason, blocked_at, is_active)
                VALUES (?, ?, ?, ?)
            ''', (ip_address, reason, datetime.now(), True))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Blocked IP added: {ip_address}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error adding blocked IP: {e}")
            return False
    
    def get_blocked_ips(self):
        """Get all currently blocked IPs"""
        try:
            conn = self.get_connection()
            cursor = conn.execute('''
                SELECT * FROM blocked_ips
                WHERE is_active = TRUE
                ORDER BY blocked_at DESC
            ''')
            
            blocked_ips = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return blocked_ips
        
        except Exception as e:
            self.logger.error(f"Error getting blocked IPs: {e}")
            return []
    
    def unblock_ip(self, ip_address):
        """Remove IP from blocked list"""
        try:
            conn = self.get_connection()
            conn.execute('''
                UPDATE blocked_ips
                SET is_active = FALSE, unblocked_at = ?
                WHERE ip_address = ?
            ''', (datetime.now(), ip_address))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"IP unblocked: {ip_address}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error unblocking IP: {e}")
            return False
    
    # ==================== SYSTEM EVENTS ====================
    
    def add_system_event(self, event_type, description, ip_address=None, username=None):
        """Add a system event"""
        try:
            conn = self.get_connection()
            conn.execute('''
                INSERT INTO system_events (event_type, description, ip_address, username)
                VALUES (?, ?, ?, ?)
            ''', (event_type, description, ip_address, username))
            
            conn.commit()
            conn.close()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error adding system event: {e}")
            return False
    
    def get_recent_events(self, limit=100):
        """Get recent system events"""
        try:
            conn = self.get_connection()
            cursor = conn.execute('''
                SELECT * FROM system_events
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            events = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return events
        
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
            return []
    
    # ==================== DASHBOARD STATISTICS ====================
    
    def get_dashboard_stats(self):
        """Get statistics for dashboard"""
        try:
            conn = self.get_connection()
            
            # Total threats today
            cursor = conn.execute('''
                SELECT COUNT(*) as count FROM threats
                WHERE DATE(timestamp) = DATE('now')
            ''')
            threats_today = cursor.fetchone()['count']
            
            # Active blocked IPs
            cursor = conn.execute('''
                SELECT COUNT(*) as count FROM blocked_ips
                WHERE is_active = TRUE
            ''')
            blocked_ips = cursor.fetchone()['count']
            
            # Critical threats
            cursor = conn.execute('''
                SELECT COUNT(*) as count FROM threats
                WHERE severity IN ('HIGH', 'CRITICAL')
                AND DATE(timestamp) = DATE('now')
            ''')
            critical_threats = cursor.fetchone()['count']
            
            # Total threats
            cursor = conn.execute('SELECT COUNT(*) as count FROM threats')
            total_threats = cursor.fetchone()['count']
            
            conn.close()
            
            return {
                'threats_today': threats_today,
                'blocked_ips': blocked_ips,
                'critical_threats': critical_threats,
                'total_threats': total_threats
            }
        
        except Exception as e:
            self.logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    def get_threat_timeline(self, hours=24):
        """Get threat timeline for charts"""
        try:
            conn = self.get_connection()
            cutoff = datetime.now() - timedelta(hours=hours)
            
            cursor = conn.execute('''
                SELECT 
                    strftime('%Y-%m-%d %H:00', timestamp) as hour,
                    COUNT(*) as count,
                    severity
                FROM threats
                WHERE timestamp >= ?
                GROUP BY hour, severity
                ORDER BY hour ASC
            ''', (cutoff,))
            
            timeline = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return timeline
        
        except Exception as e:
            self.logger.error(f"Error getting threat timeline: {e}")
            return []
    
    def get_top_attackers(self, limit=10):
        """Get most active attacker IPs"""
        try:
            conn = self.get_connection()
            cursor = conn.execute('''
                SELECT 
                    ip_address,
                    COUNT(*) as attack_count,
                    MAX(severity) as max_severity,
                    MAX(timestamp) as last_seen
                FROM threats
                GROUP BY ip_address
                ORDER BY attack_count DESC
                LIMIT ?
            ''', (limit,))
            
            attackers = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return attackers
        
        except Exception as e:
            self.logger.error(f"Error getting top attackers: {e}")
            return []
    
    # ============= User Authentication Methods =============
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, full_name='', email='', role='user'):
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, full_name, email, role))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            self.logger.info(f"User created: {username} (role: {role})")
            return user_id
        
        except sqlite3.IntegrityError:
            self.logger.error(f"User already exists: {username}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, username, password):
        """Authenticate a user and return user data if successful"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, full_name, email, role, is_active
                FROM users
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user['id'],))
                conn.commit()
                
                conn.close()
                return dict(user)
            
            conn.close()
            return None
        
        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, full_name, email, role, is_active, last_login, created_at
                FROM users
                WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            return dict(user) if user else None
        
        except Exception as e:
            self.logger.error(f"Error getting user: {e}")
            return None
    
    def is_admin(self, user_id):
        """Check if user is an admin"""
        user = self.get_user_by_id(user_id)
        return user and user['role'] == 'admin'
