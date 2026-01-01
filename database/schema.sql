-- IDPS Database Schema
-- SQLite/PostgreSQL compatible

-- Threats table - stores all detected threats
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
);

-- Blocked IPs table - tracks currently blocked IP addresses
CREATE TABLE IF NOT EXISTS blocked_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address VARCHAR(45) UNIQUE NOT NULL,
    reason VARCHAR(100),
    block_method VARCHAR(50),
    blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    unblocked_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);

-- System events table - logs all system activities
CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    ip_address VARCHAR(45),
    username VARCHAR(100),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alert history table - tracks sent alerts
CREATE TABLE IF NOT EXISTS alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    threat_id INTEGER,
    channel VARCHAR(50),
    recipient VARCHAR(255),
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    FOREIGN KEY (threat_id) REFERENCES threats(id)
);

-- System statistics table - stores daily/hourly stats
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    hour INTEGER,
    threats_detected INTEGER DEFAULT 0,
    ips_blocked INTEGER DEFAULT 0,
    events_analyzed INTEGER DEFAULT 0,
    UNIQUE(date, hour)
);

-- Whitelist/Blacklist table
CREATE TABLE IF NOT EXISTS ip_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address VARCHAR(45) NOT NULL,
    list_type VARCHAR(20) NOT NULL, -- 'whitelist' or 'blacklist'
    reason TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip_address, list_type)
);

-- Users table - for authentication and access control
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user', -- 'admin' or 'user'
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp);
CREATE INDEX IF NOT EXISTS idx_threats_ip ON threats(ip_address);
CREATE INDEX IF NOT EXISTS idx_blocked_ips_active ON blocked_ips(is_active);
CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_statistics_date ON statistics(date, hour);
