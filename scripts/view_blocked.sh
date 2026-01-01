#!/bin/bash
#
# View Blocked IPs Script
# Displays all currently blocked IP addresses
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Currently Blocked IP Addresses${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# UFW Blocks
echo -e "${GREEN}[1] UFW Firewall Blocks${NC}"
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        blocked=$(ufw status numbered | grep DENY | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u)
        
        if [ -z "$blocked" ]; then
            echo -e "  ${YELLOW}No IPs currently blocked${NC}"
        else
            count=$(echo "$blocked" | wc -l)
            echo -e "  Total Blocked: $count"
            echo ""
            echo "$blocked" | while read ip; do
                echo -e "  ${RED}✗${NC} $ip"
            done
        fi
    else
        echo -e "  ${YELLOW}UFW is not active${NC}"
    fi
else
    echo -e "  ${RED}UFW not installed${NC}"
fi
echo ""

# iptables Blocks
echo -e "${GREEN}[2] iptables Blocks${NC}"
if command -v iptables &> /dev/null; then
    blocked=$(iptables -L INPUT -n 2>/dev/null | grep DROP | awk '{print $4}' | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u)
    
    if [ -z "$blocked" ]; then
        echo -e "  ${YELLOW}No IPs currently blocked${NC}"
    else
        count=$(echo "$blocked" | wc -l)
        echo -e "  Total Blocked: $count"
        echo ""
        echo "$blocked" | while read ip; do
            echo -e "  ${RED}✗${NC} $ip"
        done
    fi
else
    echo -e "  ${RED}iptables not installed${NC}"
fi
echo ""

# Fail2Ban Bans
echo -e "${GREEN}[3] Fail2Ban Bans${NC}"
if command -v fail2ban-client &> /dev/null; then
    if systemctl is-active --quiet fail2ban; then
        jails=$(fail2ban-client status 2>/dev/null | grep "Jail list" | sed "s/.*://;s/,//g")
        
        if [ -z "$jails" ]; then
            echo -e "  ${YELLOW}No active jails${NC}"
        else
            total_bans=0
            
            for jail in $jails; do
                echo -e "  ${YELLOW}Jail: $jail${NC}"
                
                banned=$(fail2ban-client status "$jail" 2>/dev/null | grep "Banned IP list" | sed "s/.*://")
                currently_banned=$(fail2ban-client status "$jail" 2>/dev/null | grep "Currently banned" | grep -oP '\d+')
                total_banned=$(fail2ban-client status "$jail" 2>/dev/null | grep "Total banned" | grep -oP '\d+')
                
                echo -e "    Currently Banned: ${currently_banned:-0}"
                echo -e "    Total Banned: ${total_banned:-0}"
                
                if [ -n "$banned" ] && [ "$banned" != " " ]; then
                    echo -e "    Banned IPs:"
                    for ip in $banned; do
                        echo -e "      ${RED}✗${NC} $ip"
                        ((total_bans++))
                    done
                fi
                echo ""
            done
            
            echo -e "  ${GREEN}Total Currently Banned: $total_bans${NC}"
        fi
    else
        echo -e "  ${RED}Fail2Ban is not running${NC}"
    fi
else
    echo -e "  ${RED}Fail2Ban not installed${NC}"
fi
echo ""

# Summary from blocks.log
echo -e "${GREEN}[4] Recent Block History${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BLOCK_LOG="$PROJECT_DIR/logs/blocks.log"

if [ -f "$BLOCK_LOG" ]; then
    echo -e "  ${YELLOW}Last 10 Blocked IPs:${NC}"
    tail -10 "$BLOCK_LOG" | while read line; do
        echo -e "    $line"
    done
else
    echo -e "  ${YELLOW}No block history found${NC}"
fi
echo ""

# All Unique Blocked IPs (deduplicated)
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}All Unique Blocked IPs${NC}"
echo -e "${BLUE}========================================${NC}"

all_ips=""

# Collect from UFW
if command -v ufw &> /dev/null; then
    ufw_ips=$(ufw status numbered 2>/dev/null | grep DENY | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u)
    all_ips="$all_ips$ufw_ips"
fi

# Collect from iptables
if command -v iptables &> /dev/null; then
    ipt_ips=$(iptables -L INPUT -n 2>/dev/null | grep DROP | awk '{print $4}' | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u)
    all_ips="$all_ips
$ipt_ips"
fi

# Collect from Fail2Ban
if command -v fail2ban-client &> /dev/null && systemctl is-active --quiet fail2ban; then
    for jail in $(fail2ban-client status 2>/dev/null | grep "Jail list" | sed "s/.*://;s/,//g"); do
        f2b_ips=$(fail2ban-client status "$jail" 2>/dev/null | grep "Banned IP list" | sed "s/.*://")
        all_ips="$all_ips
$f2b_ips"
    done
fi

# Deduplicate and display
unique_ips=$(echo "$all_ips" | tr ' ' '\n' | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u)

if [ -z "$unique_ips" ]; then
    echo -e "${GREEN}No IPs currently blocked - System is clean!${NC}"
else
    count=$(echo "$unique_ips" | wc -l)
    echo -e "${YELLOW}Total Unique Blocked IPs: $count${NC}"
    echo ""
    echo "$unique_ips" | while read ip; do
        echo -e "  ${RED}✗${NC} $ip"
    done
fi

echo ""
echo -e "${BLUE}========================================${NC}"
