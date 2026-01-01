// IDPS Dashboard JavaScript

const API_BASE_URL = 'http://localhost:5000/api';
let timelineChart = null;
let severityChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    setupEventListeners();
});

// Check authentication status
async function checkAuthentication() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/check`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = '/login';
            return;
        }
        
        // Set username in header
        if (data.user && data.user.full_name) {
            document.getElementById('username-display').textContent = data.user.full_name;
        }
        
        // Initialize dashboard after authentication is confirmed
        initDashboard();
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    } catch (error) {
        console.error('Authentication check failed:', error);
        window.location.href = '/login';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Logout button
    document.getElementById('logout-button').addEventListener('click', logout);
    
    // Severity filter
    const severityFilter = document.getElementById('severity-filter');
    if (severityFilter) {
        severityFilter.addEventListener('change', () => {
            loadThreats();
        });
    }
}

// Logout function
async function logout() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout failed:', error);
        // Still redirect to login on error
        window.location.href = '/login';
    }
}

// Initialize dashboard with all data
async function initDashboard() {
    await Promise.all([
        loadDashboardStats(),
        loadThreats(),
        loadTopAttackers(),
        loadBlockedIPs(),
        loadTimelineChart(),
        loadSeverityChart()
    ]);
}

// Refresh all data
async function refreshData() {
    console.log('Refreshing dashboard data...');
    await initDashboard();
}

// ==================== API CALLS ====================

async function apiCall(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            credentials: 'include'
        });
        
        // Check if unauthorized
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'API call failed');
        }
        
        return data.data;
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        return null;
    }
}

// ==================== DASHBOARD STATS ====================

async function loadDashboardStats() {
    const stats = await apiCall('/dashboard/stats');
    
    if (stats) {
        document.getElementById('threats-today').textContent = stats.threats_today || 0;
        document.getElementById('blocked-ips').textContent = stats.blocked_ips || 0;
        document.getElementById('critical-threats').textContent = stats.critical_threats || 0;
        document.getElementById('total-threats').textContent = stats.total_threats || 0;
    }
}

// ==================== THREATS TABLE ====================

async function loadThreats() {
    const severityFilter = document.getElementById('severity-filter').value;
    const endpoint = severityFilter ? `/threats?severity=${severityFilter}` : '/threats?limit=50';
    
    const threats = await apiCall(endpoint);
    const tbody = document.getElementById('threats-tbody');
    
    if (!threats || threats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No threats detected</td></tr>';
        return;
    }
    
    tbody.innerHTML = threats.map(threat => `
        <tr>
            <td>${formatDateTime(threat.timestamp)}</td>
            <td>${threat.threat_type}</td>
            <td><strong>${threat.ip_address}</strong></td>
            <td><span class="severity-badge severity-${threat.severity}">${threat.severity}</span></td>
            <td>${threat.details}</td>
            <td>${threat.blocked ? '<span class="status-blocked">🚫 BLOCKED</span>' : '<span class="status-detected">⚠️ Detected</span>'}</td>
        </tr>
    `).join('');
}

// ==================== TOP ATTACKERS ====================

async function loadTopAttackers() {
    const attackers = await apiCall('/threats/top-attackers?limit=10');
    const tbody = document.getElementById('attackers-tbody');
    
    if (!attackers || attackers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="loading">No attackers found</td></tr>';
        return;
    }
    
    tbody.innerHTML = attackers.map(attacker => `
        <tr>
            <td><strong>${attacker.ip_address}</strong></td>
            <td>${attacker.attack_count}</td>
            <td><span class="severity-badge severity-${attacker.max_severity}">${attacker.max_severity}</span></td>
            <td>${formatDateTime(attacker.last_seen)}</td>
        </tr>
    `).join('');
}

// ==================== BLOCKED IPS ====================

async function loadBlockedIPs() {
    const blockedIPs = await apiCall('/blocked-ips');
    const tbody = document.getElementById('blocked-tbody');
    
    if (!blockedIPs || blockedIPs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="loading">No blocked IPs</td></tr>';
        return;
    }
    
    tbody.innerHTML = blockedIPs.map(ip => `
        <tr>
            <td><strong>${ip.ip_address}</strong></td>
            <td>${ip.reason || 'Security threat'}</td>
            <td>${formatDateTime(ip.blocked_at)}</td>
            <td><button class="btn-action" onclick="unblockIP('${ip.ip_address}')">Unblock</button></td>
        </tr>
    `).join('');
}

async function unblockIP(ipAddress) {
    if (!confirm(`Are you sure you want to unblock ${ipAddress}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/blocked-ips/${ipAddress}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`IP ${ipAddress} unblocked successfully`);
            await loadBlockedIPs();
            await loadDashboardStats();
        } else {
            alert('Failed to unblock IP: ' + data.error);
        }
    } catch (error) {
        console.error('Error unblocking IP:', error);
        alert('Error unblocking IP');
    }
}

// ==================== CHARTS ====================

async function loadTimelineChart() {
    const timeline = await apiCall('/threats/timeline?hours=24');
    
    if (!timeline) return;
    
    // Process data for chart
    const hours = [...new Set(timeline.map(t => t.hour))];
    const severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
    
    const datasets = severities.map(severity => {
        const data = hours.map(hour => {
            const entry = timeline.find(t => t.hour === hour && t.severity === severity);
            return entry ? entry.count : 0;
        });
        
        return {
            label: severity,
            data: data,
            borderColor: getSeverityColor(severity),
            backgroundColor: getSeverityColor(severity, 0.2),
            tension: 0.4,
            fill: true
        };
    });
    
    const ctx = document.getElementById('timelineChart').getContext('2d');
    
    if (timelineChart) {
        timelineChart.destroy();
    }
    
    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours.map(h => h.split(' ')[1]),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#94a3b8' },
                    grid: { color: '#334155' }
                },
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: '#334155' }
                }
            }
        }
    });
}

async function loadSeverityChart() {
    const stats = await apiCall('/threats/statistics?days=1');
    
    if (!stats) return;
    
    // Aggregate by severity
    const severityCounts = {
        'LOW': 0,
        'MEDIUM': 0,
        'HIGH': 0,
        'CRITICAL': 0
    };
    
    stats.forEach(stat => {
        severityCounts[stat.severity] += stat.count;
    });
    
    const ctx = document.getElementById('severityChart').getContext('2d');
    
    if (severityChart) {
        severityChart.destroy();
    }
    
    severityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low', 'Medium', 'High', 'Critical'],
            datasets: [{
                data: [
                    severityCounts.LOW,
                    severityCounts.MEDIUM,
                    severityCounts.HIGH,
                    severityCounts.CRITICAL
                ],
                backgroundColor: [
                    getSeverityColor('LOW'),
                    getSeverityColor('MEDIUM'),
                    getSeverityColor('HIGH'),
                    getSeverityColor('CRITICAL')
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9' }
                }
            }
        }
    });
}

// ==================== HELPER FUNCTIONS ====================

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getSeverityColor(severity, alpha = 1) {
    const colors = {
        'LOW': `rgba(16, 185, 129, ${alpha})`,
        'MEDIUM': `rgba(245, 158, 11, ${alpha})`,
        'HIGH': `rgba(239, 68, 68, ${alpha})`,
        'CRITICAL': `rgba(220, 38, 38, ${alpha})`
    };
    
    return colors[severity] || `rgba(148, 163, 184, ${alpha})`;
}
