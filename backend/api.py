#!/usr/bin/env python3
"""
IDPS Backend API
Flask REST API for IDPS Dashboard
"""

from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import logging
import sys
import os
from pathlib import Path
import secrets

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import IDPSDatabase

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Use environment variable for production or generate for development
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# CORS configuration
CORS(app, supports_credentials=True)  # Enable CORS with credentials

# Initialize database
db = IDPSDatabase()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('IDPS-API')

# ==================== AUTHENTICATION DECORATOR ====================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not db.is_admin(session['user_id']):
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Serve the landing page"""
    return send_from_directory(app.static_folder, 'home.html')

@app.route('/login')
def login_page():
    """Serve the login page"""
    if 'user_id' in session:
        return redirect('/dashboard')
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/dashboard')
def dashboard_page():
    """Serve the dashboard (requires admin)"""
    if 'user_id' not in session:
        return redirect('/login')
    
    if not db.is_admin(session['user_id']):
        return jsonify({'error': 'Admin access required'}), 403
    
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Username and password required'
        }), 400
    
    username = data['username']
    password = data['password']
    
    # Authenticate user
    user = db.authenticate_user(username, password)
    
    if user:
        # Check if user is admin
        if user['role'] != 'admin':
            logger.warning(f"Non-admin user attempted access: {username}")
            return jsonify({
                'success': False,
                'message': 'Admin access required. Only administrators can access the security dashboard.'
            }), 403
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        logger.info(f"Admin logged in: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role']
            }
        })
    else:
        logger.warning(f"Failed login attempt: {username}")
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout endpoint"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"User logged out: {username}")
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check authentication status"""
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
            })
    
    return jsonify({'authenticated': False})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'IDPS API',
        'version': '1.0.0'
    })

@app.route('/api/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_dashboard_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== THREAT ROUTES ====================

@app.route('/api/threats', methods=['GET'])
@admin_required
def get_threats():
    """Get recent threats"""
    try:
        limit = request.args.get('limit', 50, type=int)
        severity = request.args.get('severity', None)
        
        if severity:
            threats = db.get_threats_by_severity(severity)
        else:
            threats = db.get_recent_threats(limit)
        
        return jsonify({
            'success': True,
            'count': len(threats),
            'data': threats
        })
    except Exception as e:
        logger.error(f"Error getting threats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/threats/timeline', methods=['GET'])
@admin_required
def get_threat_timeline():
    """Get threat timeline for charts"""
    try:
        hours = request.args.get('hours', 24, type=int)
        timeline = db.get_threat_timeline(hours)
        
        return jsonify({
            'success': True,
            'data': timeline
        })
    except Exception as e:
        logger.error(f"Error getting threat timeline: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/threats/statistics', methods=['GET'])
@admin_required
def get_threat_statistics():
    """Get threat statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        stats = db.get_threat_statistics(days)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error getting threat statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/threats/top-attackers', methods=['GET'])
@admin_required
def get_top_attackers():
    """Get top attacker IPs"""
    try:
        limit = request.args.get('limit', 10, type=int)
        attackers = db.get_top_attackers(limit)
        
        return jsonify({
            'success': True,
            'data': attackers
        })
    except Exception as e:
        logger.error(f"Error getting top attackers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== BLOCKED IP ROUTES ====================

@app.route('/api/blocked-ips', methods=['GET'])
@admin_required
def get_blocked_ips():
    """Get all blocked IPs"""
    try:
        blocked_ips = db.get_blocked_ips()
        
        return jsonify({
            'success': True,
            'count': len(blocked_ips),
            'data': blocked_ips
        })
    except Exception as e:
        logger.error(f"Error getting blocked IPs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blocked-ips/<ip_address>', methods=['DELETE'])
@admin_required
def unblock_ip(ip_address):
    """Unblock an IP address"""
    try:
        success = db.unblock_ip(ip_address)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'IP {ip_address} unblocked successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to unblock IP'
            }), 500
    except Exception as e:
        logger.error(f"Error unblocking IP: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== SYSTEM EVENTS ROUTES ====================

@app.route('/api/events', methods=['GET'])
@admin_required
def get_events():
    """Get recent system events"""
    try:
        limit = request.args.get('limit', 100, type=int)
        events = db.get_recent_events(limit)
        
        return jsonify({
            'success': True,
            'count': len(events),
            'data': events
        })
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== SEARCH & FILTER ROUTES ====================

@app.route('/api/search', methods=['GET'])
@admin_required
def search():
    """Search threats by IP or keywords"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        conn = db.get_connection()
        cursor = conn.execute('''
            SELECT * FROM threats
            WHERE ip_address LIKE ? OR details LIKE ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (f'%{query}%', f'%{query}%'))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    logger.info("Starting IDPS API Server...")
    
    # Get port from environment variable or use 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    
    # Determine if running in production
    is_production = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    
    if not is_production:
        logger.info("Dashboard will be available at: http://localhost:5000")
    
    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=not is_production
    )
