#!/bin/bash
#
# View Alerts Script
# Displays recent security alerts
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
THREAT_LOG="$PROJECT_DIR/logs/threats.log"

# Default number of entries to show
LINES=${1:-20}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Recent Security Alerts${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f "$THREAT_LOG" ]; then
    echo -e "${RED}✗ Threats log not found: $THREAT_LOG${NC}"
    exit 1
fi

# Check if log is empty
if [ ! -s "$THREAT_LOG" ]; then
    echo -e "${GREEN}✓ No threats detected yet${NC}"
    exit 0
fi

# Display statistics
echo -e "${YELLOW}[Statistics]${NC}"
total_threats=$(wc -l < "$THREAT_LOG")
echo -e "  Total Threats Logged: $total_threats"

today_threats=$(grep "$(date +%Y-%m-%d)" "$THREAT_LOG" | wc -l)
echo -e "  Threats Today: $today_threats"

# Threat type distribution
echo -e "\n${YELLOW}[Threat Type Distribution]${NC}"
awk -F'|' '{print $3}' "$THREAT_LOG" | sort | uniq -c | sort -rn | head -10 | while read count type; do
    type=$(echo "$type" | tr -d ' ')
    echo -e "  $type: $count"
done

# Top attacking IPs
echo -e "\n${YELLOW}[Top 10 Attacking IPs]${NC}"
awk -F'|' '{print $4}' "$THREAT_LOG" | sort | uniq -c | sort -rn | head -10 | while read count ip; do
    ip=$(echo "$ip" | tr -d ' ')
    echo -e "  ${RED}$ip${NC}: $count attempts"
done

# Recent alerts
echo -e "\n${YELLOW}[Last $LINES Alerts]${NC}"
echo ""

tail -"$LINES" "$THREAT_LOG" | while IFS='|' read timestamp severity type ip details; do
    # Trim whitespace
    timestamp=$(echo "$timestamp" | tr -d ' ')
    severity=$(echo "$severity" | tr -d ' ')
    type=$(echo "$type" | tr -d ' ')
    ip=$(echo "$ip" | tr -d ' ')
    details=$(echo "$details" | sed 's/^ *Details: *//')
    
    # Color code by severity
    case "$severity" in
        CRITICAL)
            sev_color=$RED
            sev_icon="⛔"
            ;;
        HIGH)
            sev_color=$MAGENTA
            sev_icon="⚠️"
            ;;
        MEDIUM)
            sev_color=$YELLOW
            sev_icon="⚡"
            ;;
        LOW)
            sev_color=$GREEN
            sev_icon="ℹ️"
            ;;
        *)
            sev_color=$NC
            sev_icon="•"
            ;;
    esac
    
    echo -e "${sev_color}${sev_icon} [$severity] $type${NC}"
    echo -e "   Time: $timestamp"
    echo -e "   IP: ${RED}$ip${NC}"
    echo -e "   Details: $details"
    echo ""
done

# Recent high severity alerts
echo -e "${YELLOW}[Recent Critical/High Severity Alerts]${NC}"
high_sev=$(grep -E "CRITICAL|HIGH" "$THREAT_LOG" | tail -5)

if [ -z "$high_sev" ]; then
    echo -e "${GREEN}✓ No recent high severity alerts${NC}"
else
    echo "$high_sev" | while IFS='|' read timestamp severity type ip details; do
        timestamp=$(echo "$timestamp" | tr -d ' ')
        severity=$(echo "$severity" | tr -d ' ')
        type=$(echo "$type" | tr -d ' ')
        ip=$(echo "$ip" | tr -d ' ')
        details=$(echo "$details" | sed 's/^ *Details: *//')
        
        echo -e "  ${RED}[$severity]${NC} $type from $ip"
        echo -e "    $timestamp - $details"
    done
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo ""
echo "To view more entries, use: $0 <number_of_lines>"
echo "Example: $0 50"
