#!/bin/bash
#
# IP Blocker Utility Script
# Blocks IP addresses using configured methods
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BLOCK_LOG="$PROJECT_DIR/logs/blocks.log"

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Error: This script must be run as root${NC}"
        exit 1
    fi
}

# Function to log block action
log_block() {
    local ip=$1
    local method=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | BLOCKED | $ip | Method: $method" >> "$BLOCK_LOG"
}

# Function to block with UFW
block_with_ufw() {
    local ip=$1
    
    echo -e "${YELLOW}Blocking $ip with UFW...${NC}"
    
    # Check if UFW is installed
    if ! command -v ufw &> /dev/null; then
        echo -e "${RED}UFW is not installed${NC}"
        return 1
    fi
    
    # Check if UFW is active
    if ! ufw status | grep -q "Status: active"; then
        echo -e "${YELLOW}UFW is not active. Enabling...${NC}"
        ufw --force enable
    fi
    
    # Block the IP
    ufw deny from "$ip" to any
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully blocked $ip with UFW${NC}"
        log_block "$ip" "UFW"
        return 0
    else
        echo -e "${RED}Failed to block $ip with UFW${NC}"
        return 1
    fi
}

# Function to block with iptables
block_with_iptables() {
    local ip=$1
    
    echo -e "${YELLOW}Blocking $ip with iptables...${NC}"
    
    # Check if iptables is installed
    if ! command -v iptables &> /dev/null; then
        echo -e "${RED}iptables is not installed${NC}"
        return 1
    fi
    
    # Check if rule already exists
    if iptables -C INPUT -s "$ip" -j DROP 2>/dev/null; then
        echo -e "${YELLOW}$ip is already blocked in iptables${NC}"
        return 0
    fi
    
    # Add DROP rule
    iptables -A INPUT -s "$ip" -j DROP
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully blocked $ip with iptables${NC}"
        log_block "$ip" "iptables"
        
        # Save iptables rules
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null
        fi
        
        return 0
    else
        echo -e "${RED}Failed to block $ip with iptables${NC}"
        return 1
    fi
}

# Function to block with Fail2Ban
block_with_fail2ban() {
    local ip=$1
    local jail=${2:-"idps-ssh"}
    
    echo -e "${YELLOW}Blocking $ip with Fail2Ban (jail: $jail)...${NC}"
    
    # Check if Fail2Ban is installed
    if ! command -v fail2ban-client &> /dev/null; then
        echo -e "${RED}Fail2Ban is not installed${NC}"
        return 1
    fi
    
    # Check if Fail2Ban is running
    if ! systemctl is-active --quiet fail2ban; then
        echo -e "${RED}Fail2Ban is not running${NC}"
        return 1
    fi
    
    # Ban the IP
    fail2ban-client set "$jail" banip "$ip"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully blocked $ip with Fail2Ban${NC}"
        log_block "$ip" "Fail2Ban-$jail"
        return 0
    else
        echo -e "${RED}Failed to block $ip with Fail2Ban${NC}"
        return 1
    fi
}

# Function to block IP with all configured methods
block_ip() {
    local ip=$1
    
    echo -e "${YELLOW}===================================${NC}"
    echo -e "${YELLOW}Blocking IP: $ip${NC}"
    echo -e "${YELLOW}===================================${NC}"
    
    # Validate IP address
    if ! [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo -e "${RED}Error: Invalid IP address format${NC}"
        return 1
    fi
    
    local success=0
    
    # Try UFW
    if block_with_ufw "$ip"; then
        ((success++))
    fi
    
    # Try iptables
    if block_with_iptables "$ip"; then
        ((success++))
    fi
    
    # Try Fail2Ban
    if block_with_fail2ban "$ip"; then
        ((success++))
    fi
    
    if [ $success -gt 0 ]; then
        echo -e "${GREEN}IP $ip blocked successfully with $success method(s)${NC}"
        return 0
    else
        echo -e "${RED}Failed to block IP $ip with any method${NC}"
        return 1
    fi
}

# Function to unblock IP
unblock_ip() {
    local ip=$1
    
    echo -e "${YELLOW}===================================${NC}"
    echo -e "${YELLOW}Unblocking IP: $ip${NC}"
    echo -e "${YELLOW}===================================${NC}"
    
    # UFW
    if command -v ufw &> /dev/null; then
        echo -e "${YELLOW}Removing UFW rule...${NC}"
        ufw delete deny from "$ip" to any 2>/dev/null
    fi
    
    # iptables
    if command -v iptables &> /dev/null; then
        echo -e "${YELLOW}Removing iptables rule...${NC}"
        iptables -D INPUT -s "$ip" -j DROP 2>/dev/null
    fi
    
    # Fail2Ban
    if command -v fail2ban-client &> /dev/null; then
        echo -e "${YELLOW}Unbanning from Fail2Ban...${NC}"
        for jail in $(fail2ban-client status | grep "Jail list" | sed "s/.*://;s/,//g"); do
            fail2ban-client set "$jail" unbanip "$ip" 2>/dev/null
        done
    fi
    
    echo -e "${GREEN}IP $ip unblocked${NC}"
}

# Function to list blocked IPs
list_blocked() {
    echo -e "${YELLOW}===================================${NC}"
    echo -e "${YELLOW}Currently Blocked IPs${NC}"
    echo -e "${YELLOW}===================================${NC}"
    
    # UFW blocks
    echo -e "\n${GREEN}UFW Blocks:${NC}"
    if command -v ufw &> /dev/null; then
        ufw status numbered | grep DENY | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u
    else
        echo "UFW not available"
    fi
    
    # iptables blocks
    echo -e "\n${GREEN}iptables Blocks:${NC}"
    if command -v iptables &> /dev/null; then
        iptables -L INPUT -n | grep DROP | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u
    else
        echo "iptables not available"
    fi
    
    # Fail2Ban bans
    echo -e "\n${GREEN}Fail2Ban Bans:${NC}"
    if command -v fail2ban-client &> /dev/null; then
        for jail in $(fail2ban-client status | grep "Jail list" | sed "s/.*://;s/,//g"); do
            echo -e "\nJail: $jail"
            fail2ban-client status "$jail" | grep "Banned IP list" | sed "s/.*://;s/\s\+/\n/g" | grep -v "^$"
        done
    else
        echo "Fail2Ban not available"
    fi
}

# Main script logic
main() {
    check_root
    
    case "${1:-}" in
        block)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: IP address required${NC}"
                echo "Usage: $0 block <IP_ADDRESS>"
                exit 1
            fi
            block_ip "$2"
            ;;
        unblock)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: IP address required${NC}"
                echo "Usage: $0 unblock <IP_ADDRESS>"
                exit 1
            fi
            unblock_ip "$2"
            ;;
        list)
            list_blocked
            ;;
        *)
            echo "IDPS IP Blocker Utility"
            echo ""
            echo "Usage: $0 {block|unblock|list} [IP_ADDRESS]"
            echo ""
            echo "Commands:"
            echo "  block <IP>    - Block an IP address"
            echo "  unblock <IP>  - Unblock an IP address"
            echo "  list          - List all blocked IPs"
            echo ""
            echo "Examples:"
            echo "  $0 block 192.168.1.100"
            echo "  $0 unblock 192.168.1.100"
            echo "  $0 list"
            exit 1
            ;;
    esac
}

main "$@"
