#!/bin/bash
#
# IDPS Status Checker Script
# Checks the status of all IDPS components
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IDPS System Status Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Some checks require root privileges${NC}"
    echo ""
fi

# Check IDPS Monitor Service
echo -e "${YELLOW}[1] IDPS Monitor Service${NC}"
if systemctl is-active --quiet idps-monitor 2>/dev/null; then
    echo -e "${GREEN}✓ Status: Running${NC}"
    uptime=$(systemctl show idps-monitor -p ActiveEnterTimestamp | cut -d= -f2)
    echo -e "  Uptime: $uptime"
else
    echo -e "${RED}✗ Status: Not Running${NC}"
fi
echo ""

# Check Fail2Ban
echo -e "${YELLOW}[2] Fail2Ban Service${NC}"
if command -v fail2ban-client &> /dev/null; then
    if systemctl is-active --quiet fail2ban; then
        echo -e "${GREEN}✓ Status: Running${NC}"
        
        # Show active jails
        echo -e "  Active Jails:"
        fail2ban-client status 2>/dev/null | grep "Jail list" | sed "s/.*://;s/,/\n\t/g"
        
        # Show total bans
        total_bans=0
        for jail in $(fail2ban-client status 2>/dev/null | grep "Jail list" | sed "s/.*://;s/,//g"); do
            bans=$(fail2ban-client status "$jail" 2>/dev/null | grep "Currently banned" | grep -oP '\d+')
            total_bans=$((total_bans + bans))
        done
        echo -e "  Total Currently Banned IPs: $total_bans"
    else
        echo -e "${RED}✗ Status: Not Running${NC}"
    fi
else
    echo -e "${RED}✗ Fail2Ban not installed${NC}"
fi
echo ""

# Check UFW Firewall
echo -e "${YELLOW}[3] UFW Firewall${NC}"
if command -v ufw &> /dev/null; then
    status=$(ufw status 2>/dev/null | grep "Status:" | cut -d: -f2 | tr -d ' ')
    if [ "$status" == "active" ]; then
        echo -e "${GREEN}✓ Status: Active${NC}"
        
        # Count deny rules
        deny_rules=$(ufw status numbered 2>/dev/null | grep DENY | wc -l)
        echo -e "  Deny Rules: $deny_rules"
    else
        echo -e "${RED}✗ Status: Inactive${NC}"
    fi
else
    echo -e "${RED}✗ UFW not installed${NC}"
fi
echo ""

# Check iptables
echo -e "${YELLOW}[4] iptables${NC}"
if command -v iptables &> /dev/null; then
    echo -e "${GREEN}✓ iptables installed${NC}"
    
    # Count DROP rules
    drop_rules=$(iptables -L INPUT -n 2>/dev/null | grep DROP | wc -l)
    echo -e "  DROP Rules: $drop_rules"
else
    echo -e "${RED}✗ iptables not installed${NC}"
fi
echo ""

# Check Log Files
echo -e "${YELLOW}[5] Log Files${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

check_log() {
    local log_file=$1
    local log_name=$2
    
    if [ -f "$log_file" ]; then
        size=$(du -h "$log_file" | cut -f1)
        lines=$(wc -l < "$log_file")
        echo -e "${GREEN}✓ $log_name${NC}"
        echo -e "  Size: $size, Lines: $lines"
    else
        echo -e "${RED}✗ $log_name not found${NC}"
    fi
}

check_log "$PROJECT_DIR/logs/idps.log" "IDPS Main Log"
check_log "$PROJECT_DIR/logs/threats.log" "Threats Log"
check_log "$PROJECT_DIR/logs/blocks.log" "Blocks Log"
echo ""

# Check System Logs
echo -e "${YELLOW}[6] System Authentication Logs${NC}"
if [ -f "/var/log/auth.log" ]; then
    echo -e "${GREEN}✓ /var/log/auth.log exists${NC}"
    recent=$(tail -1 /var/log/auth.log 2>/dev/null | awk '{print $1, $2, $3}')
    echo -e "  Last Entry: $recent"
elif [ -f "/var/log/secure" ]; then
    echo -e "${GREEN}✓ /var/log/secure exists${NC}"
    recent=$(tail -1 /var/log/secure 2>/dev/null | awk '{print $1, $2, $3}')
    echo -e "  Last Entry: $recent"
else
    echo -e "${RED}✗ No authentication log found${NC}"
fi
echo ""

# Check Configuration Files
echo -e "${YELLOW}[7] Configuration Files${NC}"
check_config() {
    local config_file=$1
    local config_name=$2
    
    if [ -f "$config_file" ]; then
        echo -e "${GREEN}✓ $config_name${NC}"
    else
        echo -e "${RED}✗ $config_name not found${NC}"
    fi
}

check_config "$PROJECT_DIR/config/idps_config.yaml" "Main Config"
check_config "$PROJECT_DIR/config/alert_config.yaml" "Alert Config"
check_config "$PROJECT_DIR/config/whitelist.txt" "Whitelist"
check_config "$PROJECT_DIR/config/blacklist.txt" "Blacklist"
echo ""

# Recent Threats Summary
echo -e "${YELLOW}[8] Recent Threats (Last 24 hours)${NC}"
if [ -f "$PROJECT_DIR/logs/threats.log" ]; then
    threat_count=$(grep "$(date +%Y-%m-%d)" "$PROJECT_DIR/logs/threats.log" 2>/dev/null | wc -l)
    echo -e "  Threats Detected Today: $threat_count"
    
    if [ $threat_count -gt 0 ]; then
        echo -e "  Recent Threats:"
        grep "$(date +%Y-%m-%d)" "$PROJECT_DIR/logs/threats.log" 2>/dev/null | tail -5 | while read line; do
            echo -e "    - $line"
        done
    fi
else
    echo -e "${RED}✗ Threats log not found${NC}"
fi
echo ""

# System Resources
echo -e "${YELLOW}[9] System Resources${NC}"
if command -v free &> /dev/null; then
    mem_usage=$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2 }')
    echo -e "  Memory Usage: $mem_usage"
fi

if command -v df &> /dev/null; then
    disk_usage=$(df -h / | awk 'NR==2{print $5}')
    echo -e "  Disk Usage: $disk_usage"
fi

if command -v uptime &> /dev/null; then
    load=$(uptime | awk -F'load average:' '{print $2}')
    echo -e "  Load Average:$load"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Status Summary${NC}"
echo -e "${BLUE}========================================${NC}"

services_ok=0
services_total=4

systemctl is-active --quiet idps-monitor 2>/dev/null && ((services_ok++))
systemctl is-active --quiet fail2ban 2>/dev/null && ((services_ok++))
[ "$(ufw status 2>/dev/null | grep "Status:" | cut -d: -f2 | tr -d ' ')" == "active" ] && ((services_ok++))
command -v iptables &> /dev/null && ((services_ok++))

if [ $services_ok -eq $services_total ]; then
    echo -e "${GREEN}✓ All services operational ($services_ok/$services_total)${NC}"
elif [ $services_ok -gt 0 ]; then
    echo -e "${YELLOW}⚠ Some services need attention ($services_ok/$services_total operational)${NC}"
else
    echo -e "${RED}✗ Critical: No services running${NC}"
fi

echo ""
