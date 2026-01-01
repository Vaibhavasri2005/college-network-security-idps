#!/bin/bash
#
# IDPS Complete Installation Script
# Installs and configures all components of the IDPS system
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR="/opt/idps"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IDPS Installation Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}Error: Cannot detect operating system${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS $VER${NC}"
echo ""

# Check if Ubuntu/Debian
if [[ "$OS" != "ubuntu" ]] && [[ "$OS" != "debian" ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Ubuntu/Debian${NC}"
    echo -e "It may work on other Debian-based systems, but it's not tested."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${YELLOW}[1/10] Updating system packages...${NC}"
apt-get update -qq
echo -e "${GREEN}✓ System packages updated${NC}"
echo ""

echo -e "${YELLOW}[2/10] Installing required packages...${NC}"
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-yaml \
    fail2ban \
    ufw \
    iptables \
    iptables-persistent \
    rsyslog \
    curl \
    wget \
    git \
    > /dev/null 2>&1

echo -e "${GREEN}✓ Required packages installed${NC}"
echo ""

echo -e "${YELLOW}[3/10] Installing Python dependencies...${NC}"
pip3 install -q pyyaml requests
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

echo -e "${YELLOW}[4/10] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/fail2ban/filters"
mkdir -p "$INSTALL_DIR/fail2ban/jails"
echo -e "${GREEN}✓ Installation directory created${NC}"
echo ""

echo -e "${YELLOW}[5/10] Copying IDPS files...${NC}"
# Copy configuration files
cp "$PROJECT_DIR/config/"*.yaml "$INSTALL_DIR/config/" 2>/dev/null || true
cp "$PROJECT_DIR/config/"*.txt "$INSTALL_DIR/config/" 2>/dev/null || true

# Copy scripts
cp "$PROJECT_DIR/scripts/"*.py "$INSTALL_DIR/scripts/" 2>/dev/null || true
cp "$PROJECT_DIR/scripts/"*.sh "$INSTALL_DIR/scripts/" 2>/dev/null || true

# Copy Fail2Ban configurations
cp "$PROJECT_DIR/fail2ban/filters/"*.conf "$INSTALL_DIR/fail2ban/filters/" 2>/dev/null || true
cp "$PROJECT_DIR/fail2ban/jails/"*.local "$INSTALL_DIR/fail2ban/jails/" 2>/dev/null || true

# Make scripts executable
chmod +x "$INSTALL_DIR/scripts/"*.sh
chmod +x "$INSTALL_DIR/scripts/"*.py

echo -e "${GREEN}✓ IDPS files copied${NC}"
echo ""

echo -e "${YELLOW}[6/10] Configuring Fail2Ban...${NC}"
# Install custom filters
cp "$INSTALL_DIR/fail2ban/filters/"*.conf /etc/fail2ban/filter.d/

# Install custom jails
cp "$INSTALL_DIR/fail2ban/jails/"*.local /etc/fail2ban/jail.d/

# Restart Fail2Ban
systemctl enable fail2ban
systemctl restart fail2ban

echo -e "${GREEN}✓ Fail2Ban configured and started${NC}"
echo ""

echo -e "${YELLOW}[7/10] Configuring UFW firewall...${NC}"
# Enable UFW
ufw --force enable

# Allow SSH (important!)
ufw allow 22/tcp

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Reload UFW
ufw reload

echo -e "${GREEN}✓ UFW firewall configured${NC}"
echo ""

echo -e "${YELLOW}[8/10] Creating systemd service...${NC}"
cat > /etc/systemd/system/idps-monitor.service << 'EOF'
[Unit]
Description=IDPS Intrusion Detection and Prevention System
After=network.target fail2ban.service
Wants=fail2ban.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/idps
ExecStart=/usr/bin/python3 /opt/idps/scripts/monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload
systemctl enable idps-monitor

echo -e "${GREEN}✓ Systemd service created${NC}"
echo ""

echo -e "${YELLOW}[9/10] Configuring log rotation...${NC}"
cat > /etc/logrotate.d/idps << 'EOF'
/opt/idps/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload idps-monitor > /dev/null 2>&1 || true
    endscript
}
EOF

echo -e "${GREEN}✓ Log rotation configured${NC}"
echo ""

echo -e "${YELLOW}[10/10] Setting up initial whitelist...${NC}"
# Add localhost to whitelist if not already there
if ! grep -q "127.0.0.1" "$INSTALL_DIR/config/whitelist.txt"; then
    echo "127.0.0.1" >> "$INSTALL_DIR/config/whitelist.txt"
fi
if ! grep -q "::1" "$INSTALL_DIR/config/whitelist.txt"; then
    echo "::1" >> "$INSTALL_DIR/config/whitelist.txt"
fi

# Get current SSH IP and add to whitelist
if [ -n "$SSH_CLIENT" ]; then
    CURRENT_IP=$(echo $SSH_CLIENT | awk '{print $1}')
    echo -e "${YELLOW}Your current IP: $CURRENT_IP${NC}"
    read -p "Add your current IP to whitelist? (recommended) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! grep -q "$CURRENT_IP" "$INSTALL_DIR/config/whitelist.txt"; then
            echo "$CURRENT_IP" >> "$INSTALL_DIR/config/whitelist.txt"
            echo -e "${GREEN}✓ Your IP added to whitelist${NC}"
        fi
    fi
fi

echo -e "${GREEN}✓ Whitelist configured${NC}"
echo ""

# Create convenience symlinks
echo -e "${YELLOW}Creating command shortcuts...${NC}"
ln -sf "$INSTALL_DIR/scripts/status.sh" /usr/local/bin/idps-status
ln -sf "$INSTALL_DIR/scripts/view_blocked.sh" /usr/local/bin/idps-blocked
ln -sf "$INSTALL_DIR/scripts/view_alerts.sh" /usr/local/bin/idps-alerts
ln -sf "$INSTALL_DIR/scripts/unban_ip.sh" /usr/local/bin/idps-unban
ln -sf "$INSTALL_DIR/scripts/ip_blocker.sh" /usr/local/bin/idps-block
echo -e "${GREEN}✓ Command shortcuts created${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${BLUE}Available Commands:${NC}"
echo -e "  ${YELLOW}idps-status${NC}      - Check IDPS system status"
echo -e "  ${YELLOW}idps-blocked${NC}     - View blocked IPs"
echo -e "  ${YELLOW}idps-alerts${NC}      - View recent security alerts"
echo -e "  ${YELLOW}idps-unban <IP>${NC}  - Unban an IP address"
echo -e "  ${YELLOW}idps-block <IP>${NC}  - Manually block an IP"
echo ""

echo -e "${BLUE}Service Management:${NC}"
echo -e "  ${YELLOW}systemctl start idps-monitor${NC}    - Start IDPS"
echo -e "  ${YELLOW}systemctl stop idps-monitor${NC}     - Stop IDPS"
echo -e "  ${YELLOW}systemctl status idps-monitor${NC}   - Check status"
echo -e "  ${YELLOW}systemctl restart idps-monitor${NC}  - Restart IDPS"
echo ""

echo -e "${BLUE}Configuration:${NC}"
echo -e "  Main config: ${YELLOW}$INSTALL_DIR/config/idps_config.yaml${NC}"
echo -e "  Alert config: ${YELLOW}$INSTALL_DIR/config/alert_config.yaml${NC}"
echo -e "  Whitelist: ${YELLOW}$INSTALL_DIR/config/whitelist.txt${NC}"
echo -e "  Blacklist: ${YELLOW}$INSTALL_DIR/config/blacklist.txt${NC}"
echo ""

echo -e "${BLUE}Log Files:${NC}"
echo -e "  Main log: ${YELLOW}$INSTALL_DIR/logs/idps.log${NC}"
echo -e "  Threats: ${YELLOW}$INSTALL_DIR/logs/threats.log${NC}"
echo -e "  Blocks: ${YELLOW}$INSTALL_DIR/logs/blocks.log${NC}"
echo ""

# Ask if user wants to start the service now
read -p "Start IDPS monitor service now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start idps-monitor
    sleep 2
    
    if systemctl is-active --quiet idps-monitor; then
        echo -e "${GREEN}✓ IDPS monitor service started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start IDPS monitor service${NC}"
        echo -e "Check logs: journalctl -u idps-monitor -n 50"
    fi
else
    echo -e "${YELLOW}You can start the service later with:${NC}"
    echo -e "  ${YELLOW}sudo systemctl start idps-monitor${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Thank you for using IDPS!${NC}"
echo -e "${GREEN}========================================${NC}"
