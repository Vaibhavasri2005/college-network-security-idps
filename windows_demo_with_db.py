#!/usr/bin/env python3
"""
IDPS Windows Demo with Database
Simulates IDPS functionality and populates database with sample data
"""

import sys
import time
import random
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.models import IDPSDatabase

class IDPSDemoWithDB:
    def __init__(self):
        """Initialize demo"""
        self.database = IDPSDatabase('database/idps.db')
        self.recent_events = deque(maxlen=100)
        self.blocked_ips = set()
        
        # Demo configurations
        self.attack_types = ['brute_force', 'port_scan', 'invalid_user', 'root_login', 'connection_flood']
        self.severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        print("=" * 60)
        print("🛡️  IDPS Windows Demo with Database".center(60))
        print("=" * 60)
        print()
    
    def generate_sample_data(self, days=7, threats_per_day=20):
        """Generate sample historical data"""
        print(f"📊 Generating {threats_per_day} threats per day for {days} days...")
        
        demo_ips = [
            '192.168.1.100', '203.0.113.45', '198.51.100.78',
            '10.0.0.50', '172.16.0.25', '192.168.100.200',
            '8.8.8.8', '1.2.3.4', '5.6.7.8', '9.10.11.12'
        ]
        
        total_threats = 0
        
        for day in range(days):
            date = datetime.now() - timedelta(days=days-day)
            
            for _ in range(threats_per_day):
                # Generate random threat
                threat_type = random.choice(self.attack_types)
                ip = random.choice(demo_ips)
                
                # Assign severity based on threat type
                if threat_type == 'root_login':
                    severity = random.choice(['HIGH', 'CRITICAL'])
                elif threat_type == 'brute_force':
                    severity = random.choice(['MEDIUM', 'HIGH'])
                elif threat_type == 'port_scan':
                    severity = random.choice(['LOW', 'MEDIUM'])
                else:
                    severity = random.choice(self.severities)
                
                # Create threat details
                details = self.generate_threat_details(threat_type, ip)
                offense_count = random.randint(1, 10)
                blocked = severity in ['HIGH', 'CRITICAL'] or offense_count >= 5
                
                # Add timestamp variation within the day
                hours = random.randint(0, 23)
                minutes = random.randint(0, 59)
                threat_time = date.replace(hour=hours, minute=minutes)
                
                # Insert into database with specific timestamp
                # (We'd need to modify the add_threat method to accept custom timestamps,
                # but for demo purposes, we'll add with current time and note this limitation)
                threat_id = self.database.add_threat(
                    threat_type=threat_type,
                    ip_address=ip,
                    severity=severity,
                    details=details,
                    offense_count=offense_count,
                    blocked=blocked
                )
                
                # Add blocked IP if blocked
                if blocked and ip not in self.blocked_ips:
                    self.database.add_blocked_ip(ip, f"{threat_type} - {details}")
                    self.blocked_ips.add(ip)
                
                total_threats += 1
            
            print(f"  ✓ Day {day+1}/{days} complete ({threats_per_day} threats)")
        
        print(f"\n✅ Generated {total_threats} total threats in database!")
        print(f"✅ Blocked {len(self.blocked_ips)} unique IPs")
        print()
    
    def generate_threat_details(self, threat_type, ip):
        """Generate realistic threat details"""
        if threat_type == 'brute_force':
            attempts = random.randint(5, 20)
            return f"{attempts} failed login attempts from {ip}"
        
        elif threat_type == 'port_scan':
            ports = random.randint(10, 50)
            return f"Scanned {ports} ports from {ip}"
        
        elif threat_type == 'invalid_user':
            users = ['admin', 'test', 'guest', 'user123', 'root']
            user = random.choice(users)
            return f"Attempted login with invalid user '{user}' from {ip}"
        
        elif threat_type == 'root_login':
            return f"Direct root login attempt from {ip}"
        
        elif threat_type == 'connection_flood':
            connections = random.randint(50, 200)
            return f"{connections} rapid connections from {ip}"
        
        return f"Security event from {ip}"
    
    def simulate_realtime_attack(self):
        """Simulate a real-time attack scenario"""
        print("🔴 Simulating REAL-TIME ATTACK SCENARIO...")
        print("-" * 60)
        
        attacker_ip = "192.168.1.100"
        
        # Stage 1: Port Scan
        print(f"\n[Stage 1] Port scan detected from {attacker_ip}")
        self.database.add_threat(
            threat_type='port_scan',
            ip_address=attacker_ip,
            severity='MEDIUM',
            details='Scanned 25 ports',
            offense_count=1,
            blocked=False
        )
        print("  ⚠️  Severity: MEDIUM - Monitoring...")
        time.sleep(2)
        
        # Stage 2: Invalid User Attempts
        print(f"\n[Stage 2] Invalid user attempts from {attacker_ip}")
        self.database.add_threat(
            threat_type='invalid_user',
            ip_address=attacker_ip,
            severity='MEDIUM',
            details='Tried users: admin, test, guest',
            offense_count=3,
            blocked=False
        )
        print("  ⚠️  Severity: MEDIUM - Threat escalating...")
        time.sleep(2)
        
        # Stage 3: Brute Force Attack
        print(f"\n[Stage 3] Brute force attack from {attacker_ip}")
        threat_id = self.database.add_threat(
            threat_type='brute_force',
            ip_address=attacker_ip,
            severity='HIGH',
            details='15 failed login attempts in 2 minutes',
            offense_count=5,
            blocked=True
        )
        print("  🚨 Severity: HIGH")
        print(f"  🚫 ACTION TAKEN: IP {attacker_ip} BLOCKED!")
        self.database.add_blocked_ip(attacker_ip, 'Brute force attack')
        self.database.add_system_event(
            event_type='ip_blocked',
            description=f'Blocked {attacker_ip} due to brute force',
            ip_address=attacker_ip
        )
        time.sleep(2)
        
        print("\n✅ Attack blocked successfully!")
        print("-" * 60)
    
    def show_statistics(self):
        """Display current statistics"""
        print("\n" + "=" * 60)
        print("📊 CURRENT IDPS STATISTICS".center(60))
        print("=" * 60)
        
        stats = self.database.get_dashboard_stats()
        
        print(f"\n  🚨 Threats Today:      {stats.get('threats_today', 0)}")
        print(f"  🚫 Blocked IPs:        {stats.get('blocked_ips', 0)}")
        print(f"  ⚠️  Critical Threats:   {stats.get('critical_threats', 0)}")
        print(f"  📈 Total Threats:      {stats.get('total_threats', 0)}")
        
        print("\n" + "=" * 60)
    
    def show_recent_threats(self, limit=5):
        """Show recent threats"""
        print(f"\n🔍 RECENT THREATS (Last {limit}):")
        print("-" * 60)
        
        threats = self.database.get_recent_threats(limit)
        
        if not threats:
            print("  No threats detected yet.")
        else:
            for threat in threats:
                timestamp = threat['timestamp']
                print(f"\n  [{timestamp}]")
                print(f"  Type: {threat['threat_type']}")
                print(f"  IP: {threat['ip_address']}")
                print(f"  Severity: {threat['severity']}")
                print(f"  Details: {threat['details']}")
                print(f"  Status: {'🚫 BLOCKED' if threat['blocked'] else '⚠️  Detected'}")
        
        print("-" * 60)
    
    def show_top_attackers(self, limit=5):
        """Show top attackers"""
        print(f"\n👥 TOP {limit} ATTACKERS:")
        print("-" * 60)
        
        attackers = self.database.get_top_attackers(limit)
        
        if not attackers:
            print("  No attackers recorded yet.")
        else:
            for i, attacker in enumerate(attackers, 1):
                print(f"\n  #{i}. {attacker['ip_address']}")
                print(f"      Attacks: {attacker['attack_count']}")
                print(f"      Max Severity: {attacker['max_severity']}")
                print(f"      Last Seen: {attacker['last_seen']}")
        
        print("-" * 60)
    
    def run_interactive_menu(self):
        """Interactive menu"""
        while True:
            print("\n" + "=" * 60)
            print("🛡️  IDPS DEMO MENU".center(60))
            print("=" * 60)
            print("\n1. Generate Sample Historical Data")
            print("2. Simulate Real-Time Attack")
            print("3. View Current Statistics")
            print("4. View Recent Threats")
            print("5. View Top Attackers")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                days = input("Enter number of days (default 7): ").strip() or "7"
                threats = input("Enter threats per day (default 20): ").strip() or "20"
                self.generate_sample_data(int(days), int(threats))
            
            elif choice == '2':
                self.simulate_realtime_attack()
            
            elif choice == '3':
                self.show_statistics()
            
            elif choice == '4':
                self.show_recent_threats(10)
            
            elif choice == '5':
                self.show_top_attackers(10)
            
            elif choice == '6':
                print("\n👋 Exiting demo. Database saved!")
                break
            
            else:
                print("\n❌ Invalid option. Please try again.")
    
    def run_automated_demo(self):
        """Run automated demonstration"""
        print("🎬 Running Automated Demo...\n")
        
        # Generate historical data
        self.generate_sample_data(days=3, threats_per_day=15)
        
        # Simulate real-time attack
        self.simulate_realtime_attack()
        
        # Show statistics
        self.show_statistics()
        
        # Show recent threats
        self.show_recent_threats(5)
        
        # Show top attackers
        self.show_top_attackers(5)
        
        print("\n✅ Automated demo complete!")
        print(f"\n📊 Dashboard: http://localhost:5000")
        print("   To start the API: cd backend && python api.py")

if __name__ == '__main__':
    demo = IDPSDemoWithDB()
    
    # Check if user wants interactive or automated mode
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        demo.run_interactive_menu()
    else:
        demo.run_automated_demo()
        print("\n💡 Tip: Run with --interactive flag for menu mode")
