#!/bin/bash
#
# Unban IP Script
# Removes an IP address from all blocking mechanisms
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

# Check if IP provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No IP address provided${NC}"
    echo "Usage: $0 <IP_ADDRESS>"
    exit 1
fi

IP=$1

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Unbanning IP: $IP${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Validate IP address
if ! [[ $IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo -e "${RED}Error: Invalid IP address format${NC}"
    exit 1
fi

# Unban from UFW
echo -e "${YELLOW}[1] Removing from UFW...${NC}"
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "$IP"; then
        ufw delete deny from "$IP" to any 2>/dev/null
        echo -e "${GREEN}✓ Removed from UFW${NC}"
    else
        echo -e "  IP not found in UFW rules"
    fi
else
    echo -e "  UFW not available"
fi
echo ""

# Unban from iptables
echo -e "${YELLOW}[2] Removing from iptables...${NC}"
if command -v iptables &> /dev/null; then
    if iptables -L INPUT -n | grep -q "$IP"; then
        iptables -D INPUT -s "$IP" -j DROP 2>/dev/null
        
        # Save iptables rules
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null
        fi
        
        echo -e "${GREEN}✓ Removed from iptables${NC}"
    else
        echo -e "  IP not found in iptables rules"
    fi
else
    echo -e "  iptables not available"
fi
echo ""

# Unban from Fail2Ban
echo -e "${YELLOW}[3] Removing from Fail2Ban...${NC}"
if command -v fail2ban-client &> /dev/null; then
    if systemctl is-active --quiet fail2ban; then
        unbanned=0
        
        for jail in $(fail2ban-client status 2>/dev/null | grep "Jail list" | sed "s/.*://;s/,//g"); do
            if fail2ban-client status "$jail" 2>/dev/null | grep -q "$IP"; then
                fail2ban-client set "$jail" unbanip "$IP" 2>/dev/null
                echo -e "${GREEN}✓ Unbanned from jail: $jail${NC}"
                ((unbanned++))
            fi
        done
        
        if [ $unbanned -eq 0 ]; then
            echo -e "  IP not found in any Fail2Ban jail"
        fi
    else
        echo -e "  Fail2Ban is not running"
    fi
else
    echo -e "  Fail2Ban not available"
fi
echo ""

# Log the unban action
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BLOCK_LOG="$PROJECT_DIR/logs/blocks.log"

if [ -f "$BLOCK_LOG" ]; then
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | UNBANNED | $IP | Manual unban" >> "$BLOCK_LOG"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IP $IP has been unbanned${NC}"
echo -e "${GREEN}========================================${NC}"
