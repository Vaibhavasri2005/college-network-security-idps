#!/usr/bin/env python3
"""
IDPS Windows Demo - Simulation Version
Demonstrates IDPS functionality on Windows without requiring Linux tools
"""

import time
import random
from datetime import datetime
from collections import defaultdict
import os

class IDPSDemo:
    def __init__(self):
        self.detected_threats = []
        self.blocked_ips = set()
        self.ip_events = defaultdict(list)
        
        # Simulated attack IPs
        self.attack_ips = [
            "203.0.113.100", "198.51.100.50", "192.0.2.25",
            "203.0.113.200", "198.51.100.75"
        ]
        
        # Legitimate IPs
        self.legit_ips = ["192.168.1.100", "10.0.0.50"]
        
        print("=" * 70)
        print("IDPS WINDOWS DEMO - Intrusion Detection Simulation")
        print("=" * 70)
        print()
        print("This demo simulates the IDPS system detecting and blocking attacks.")
        print("In a real Linux deployment, this would actively protect your server.")
        print()
    
    def generate_log_entry(self, attack_type="random"):
        """Generate simulated log entries"""
        if attack_type == "random":
            attack_type = random.choice([
                "failed_login", "invalid_user", "port_scan", 
                "brute_force", "normal"
            ])
        
        if attack_type == "normal":
            ip = random.choice(self.legit_ips)
            log = f"{datetime.now().strftime('%b %d %H:%M:%S')} Accepted password for user from {ip} port 22"
        elif attack_type == "failed_login":
            ip = random.choice(self.attack_ips)
            log = f"{datetime.now().strftime('%b %d %H:%M:%S')} Failed password for admin from {ip} port 22"
        elif attack_type == "invalid_user":
            ip = random.choice(self.attack_ips)
            user = random.choice(["hacker", "admin", "test", "root"])
            log = f"{datetime.now().strftime('%b %d %H:%M:%S')} Invalid user {user} from {ip} port 22"
        elif attack_type == "port_scan":
            ip = random.choice(self.attack_ips)
            log = f"{datetime.now().strftime('%b %d %H:%M:%S')} Did not receive identification string from {ip}"
        elif attack_type == "brute_force":
            ip = random.choice(self.attack_ips)
            log = f"{datetime.now().strftime('%b %d %H:%M:%S')} authentication failure from {ip}"
        
        return log, ip if attack_type != "normal" else None, attack_type
    
    def analyze_log(self, log, ip, event_type):
        """Analyze log entry for threats"""
        if event_type == "normal":
            return None
        
        # Track events per IP
        self.ip_events[ip].append({
            'type': event_type,
            'timestamp': datetime.now(),
            'log': log
        })
        
        # Detect threats based on event count
        event_count = len(self.ip_events[ip])
        
        if event_count >= 3:
            threat = {
                'ip': ip,
                'type': event_type,
                'severity': 'HIGH' if event_count >= 5 else 'MEDIUM',
                'attempts': event_count,
                'timestamp': datetime.now()
            }
            return threat
        
        return None
    
    def block_ip(self, ip):
        """Simulate blocking an IP"""
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            print(f"\n{'=' * 70}")
            print(f"🛡️  BLOCKING IP: {ip}")
            print(f"{'=' * 70}")
            print(f"✓ Added to firewall deny list")
            print(f"✓ Banned by Fail2Ban")
            print(f"✓ All connections from {ip} will be dropped")
            print()
    
    def display_threat(self, threat):
        """Display detected threat"""
        severity_icon = "⛔" if threat['severity'] == "HIGH" else "⚠️"
        print(f"\n{severity_icon} THREAT DETECTED!")
        print(f"  Type: {threat['type']}")
        print(f"  IP: {threat['ip']}")
        print(f"  Severity: {threat['severity']}")
        print(f"  Attempts: {threat['attempts']}")
        print(f"  Time: {threat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def show_status(self):
        """Show current system status"""
        print("\n" + "=" * 70)
        print("📊 IDPS SYSTEM STATUS")
        print("=" * 70)
        print(f"✓ Monitor Status: Running")
        print(f"✓ Threats Detected: {len(self.detected_threats)}")
        print(f"✓ IPs Blocked: {len(self.blocked_ips)}")
        print(f"✓ Events Analyzed: {sum(len(events) for events in self.ip_events.values())}")
        
        if self.blocked_ips:
            print(f"\n🚫 Currently Blocked IPs:")
            for ip in self.blocked_ips:
                print(f"  ✗ {ip}")
        print()
    
    def simulate_attack_scenario(self):
        """Simulate a realistic attack scenario"""
        print("🔍 Starting continuous monitoring...\n")
        time.sleep(1)
        
        scenarios = [
            ("normal", "Normal user login activity..."),
            ("failed_login", "Detecting failed login attempt..."),
            ("failed_login", "Another failed login from same IP..."),
            ("invalid_user", "Invalid username detected..."),
            ("failed_login", "Repeated authentication failure..."),
            ("brute_force", "BRUTE FORCE pattern detected!"),
            ("port_scan", "Port scanning activity detected!"),
        ]
        
        for i, (attack_type, description) in enumerate(scenarios, 1):
            print(f"[{i}/{len(scenarios)}] {description}")
            
            # Generate and analyze log
            log, ip, event_type = self.generate_log_entry(attack_type)
            print(f"  Log: {log[:80]}...")
            
            if ip:
                threat = self.analyze_log(log, ip, event_type)
                
                if threat:
                    self.detected_threats.append(threat)
                    self.display_threat(threat)
                    
                    # Block if threshold reached
                    if threat['attempts'] >= 3:
                        self.block_ip(threat['ip'])
            
            time.sleep(1.5)
        
        # Show final status
        time.sleep(1)
        self.show_status()
    
    def interactive_menu(self):
        """Interactive demo menu"""
        while True:
            print("\n" + "=" * 70)
            print("IDPS DEMO MENU")
            print("=" * 70)
            print("1. Run Attack Simulation")
            print("2. View System Status")
            print("3. View Detected Threats")
            print("4. View Blocked IPs")
            print("5. Generate Random Attack")
            print("6. Reset Demo")
            print("7. Exit")
            print()
            
            choice = input("Select option (1-7): ").strip()
            
            if choice == "1":
                self.simulate_attack_scenario()
            elif choice == "2":
                self.show_status()
            elif choice == "3":
                self.show_threats()
            elif choice == "4":
                self.show_blocked()
            elif choice == "5":
                self.generate_random_attack()
            elif choice == "6":
                self.reset()
            elif choice == "7":
                print("\n👋 Thank you for using IDPS Demo!")
                print("Deploy the real version on Ubuntu for actual protection.")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def show_threats(self):
        """Display all detected threats"""
        print("\n" + "=" * 70)
        print("🚨 DETECTED THREATS")
        print("=" * 70)
        if not self.detected_threats:
            print("No threats detected yet.")
        else:
            for i, threat in enumerate(self.detected_threats, 1):
                print(f"\n[{i}] {threat['type'].upper()}")
                print(f"    IP: {threat['ip']}")
                print(f"    Severity: {threat['severity']}")
                print(f"    Attempts: {threat['attempts']}")
                print(f"    Time: {threat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def show_blocked(self):
        """Display blocked IPs"""
        print("\n" + "=" * 70)
        print("🚫 BLOCKED IP ADDRESSES")
        print("=" * 70)
        if not self.blocked_ips:
            print("No IPs blocked yet.")
        else:
            for ip in self.blocked_ips:
                event_count = len(self.ip_events.get(ip, []))
                print(f"  ✗ {ip} (Total violations: {event_count})")
    
    def generate_random_attack(self):
        """Generate a random attack event"""
        attack_type = random.choice(["failed_login", "invalid_user", "port_scan", "brute_force"])
        log, ip, event_type = self.generate_log_entry(attack_type)
        
        print(f"\n🎲 Generating random {attack_type} event...")
        print(f"Log: {log}")
        
        threat = self.analyze_log(log, ip, event_type)
        if threat:
            self.detected_threats.append(threat)
            self.display_threat(threat)
            if threat['attempts'] >= 3:
                self.block_ip(threat['ip'])
        else:
            print("Event logged, threshold not reached yet.")
    
    def reset(self):
        """Reset demo state"""
        self.detected_threats = []
        self.blocked_ips = set()
        self.ip_events = defaultdict(list)
        print("\n✓ Demo reset. All data cleared.")

def main():
    demo = IDPSDemo()
    
    print("Choose demo mode:")
    print("1. Automatic Attack Simulation")
    print("2. Interactive Menu")
    print()
    
    choice = input("Select mode (1 or 2): ").strip()
    
    if choice == "1":
        demo.simulate_attack_scenario()
        print("\n" + "=" * 70)
        print("Demo complete! Deploy on Ubuntu for real protection.")
        print("=" * 70)
    else:
        demo.interactive_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
