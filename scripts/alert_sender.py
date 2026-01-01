#!/usr/bin/env python3
"""
Alert Sender Module
Sends security alerts via various channels
"""

import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import yaml

class AlertSender:
    def __init__(self, config):
        """Initialize Alert Sender"""
        self.config = config
        self.logger = logging.getLogger('AlertSender')
        
        # Load alert configuration
        self.alert_config = self.load_alert_config()
        
        # Alert cooldown tracking
        self.last_alert_time = {}
        
        self.logger.info("Alert Sender initialized")
    
    def load_alert_config(self):
        """Load alert configuration"""
        alert_config_file = self.config.get('alerts', {}).get(
            'email_config', 'config/alert_config.yaml'
        )
        
        try:
            with open(alert_config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading alert config: {e}")
            return {}
    
    def send_alert(self, threat):
        """Send alert for detected threat"""
        # Check cooldown
        if not self.check_cooldown(threat):
            self.logger.debug(f"Alert cooldown active for {threat.get('type')}")
            return
        
        # Send via configured channels
        if self.alert_config.get('email', {}).get('enabled', False):
            self.send_email_alert(threat)
        
        if self.alert_config.get('slack', {}).get('enabled', False):
            self.send_slack_alert(threat)
        
        if self.alert_config.get('telegram', {}).get('enabled', False):
            self.send_telegram_alert(threat)
        
        if self.alert_config.get('webhook', {}).get('enabled', False):
            self.send_webhook_alert(threat)
        
        # Update last alert time
        self.last_alert_time[threat.get('type')] = datetime.now()
    
    def check_cooldown(self, threat):
        """Check if alert cooldown has expired"""
        cooldown = self.config.get('alerts', {}).get('cooldown', 300)
        threat_type = threat.get('type')
        
        if threat_type not in self.last_alert_time:
            return True
        
        last_alert = self.last_alert_time[threat_type]
        elapsed = (datetime.now() - last_alert).total_seconds()
        
        return elapsed >= cooldown
    
    def send_email_alert(self, threat):
        """Send email alert"""
        email_config = self.alert_config.get('email', {})
        
        try:
            # Get template
            template = self.get_email_template(threat)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = email_config.get('sender')
            msg['Subject'] = f"{email_config.get('subject_prefix', '[IDPS]')} {template['subject']}"
            
            # Format message with threat details
            body = template['message'].format(**threat)
            
            # Add body
            if email_config.get('format', 'html') == 'html':
                html_body = self.format_html_email(template['subject'], body, threat)
                msg.attach(MIMEText(html_body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send to all recipients
            recipients = email_config.get('recipients', [])
            for recipient in recipients:
                msg['To'] = recipient
                
                # Connect and send
                server = smtplib.SMTP(
                    email_config.get('smtp_server'),
                    email_config.get('smtp_port', 587)
                )
                
                if email_config.get('use_tls', True):
                    server.starttls()
                
                server.login(
                    email_config.get('sender'),
                    email_config.get('password')
                )
                
                server.send_message(msg)
                server.quit()
                
                self.logger.info(f"Email alert sent to {recipient}")
        
        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
    
    def get_email_template(self, threat):
        """Get email template for threat type"""
        templates = self.alert_config.get('templates', {})
        threat_type = threat.get('type')
        
        # Get specific template or use default
        template = templates.get(threat_type, {
            'subject': f"Security Alert: {threat_type}",
            'message': "A security threat has been detected.\n\nDetails: {details}\nIP: {ip}\nSeverity: {severity}\nTime: {timestamp}"
        })
        
        return template
    
    def format_html_email(self, subject, body, threat):
        """Format HTML email"""
        severity = threat.get('severity', 'MEDIUM')
        severity_colors = {
            'LOW': '#36a64f',
            'MEDIUM': '#ff9900',
            'HIGH': '#ff0000',
            'CRITICAL': '#990000'
        }
        
        color = severity_colors.get(severity, '#cccccc')
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: {color}; color: white; padding: 20px; }}
                    .content {{ padding: 20px; }}
                    .details {{ background-color: #f5f5f5; padding: 15px; border-left: 4px solid {color}; }}
                    .footer {{ padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🚨 {subject}</h2>
                </div>
                <div class="content">
                    <p><strong>Severity:</strong> <span style="color: {color};">{severity}</span></p>
                    <div class="details">
                        <pre>{body}</pre>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated alert from your IDPS system.</p>
                    <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </body>
        </html>
        """
        
        return html
    
    def send_slack_alert(self, threat):
        """Send Slack alert"""
        slack_config = self.alert_config.get('slack', {})
        
        try:
            webhook_url = slack_config.get('webhook_url')
            
            severity_colors = {
                'LOW': 'good',
                'MEDIUM': 'warning',
                'HIGH': 'danger',
                'CRITICAL': 'danger'
            }
            
            color = severity_colors.get(threat.get('severity'), 'warning')
            
            payload = {
                'channel': slack_config.get('channel', '#security'),
                'username': slack_config.get('username', 'IDPS Bot'),
                'icon_emoji': ':shield:',
                'attachments': [{
                    'color': color,
                    'title': f"Security Alert: {threat.get('type')}",
                    'text': threat.get('details'),
                    'fields': [
                        {'title': 'IP Address', 'value': threat.get('ip'), 'short': True},
                        {'title': 'Severity', 'value': threat.get('severity'), 'short': True},
                        {'title': 'Timestamp', 'value': str(threat.get('timestamp')), 'short': False}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            self.logger.info("Slack alert sent")
        
        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {e}")
    
    def send_telegram_alert(self, threat):
        """Send Telegram alert"""
        telegram_config = self.alert_config.get('telegram', {})
        
        try:
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            message = f"""
🚨 *IDPS Security Alert*

*Type:* {threat.get('type')}
*Severity:* {threat.get('severity')}
*IP:* {threat.get('ip')}
*Details:* {threat.get('details')}
*Time:* {threat.get('timestamp')}
            """
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            self.logger.info("Telegram alert sent")
        
        except Exception as e:
            self.logger.error(f"Error sending Telegram alert: {e}")
    
    def send_webhook_alert(self, threat):
        """Send generic webhook alert"""
        webhook_config = self.alert_config.get('webhook', {})
        
        try:
            url = webhook_config.get('url')
            method = webhook_config.get('method', 'POST').upper()
            headers = webhook_config.get('headers', {})
            
            payload = {
                'type': threat.get('type'),
                'ip': threat.get('ip'),
                'severity': threat.get('severity'),
                'details': threat.get('details'),
                'timestamp': str(threat.get('timestamp')),
                'offense_count': threat.get('offense_count', 0)
            }
            
            if method == 'POST':
                response = requests.post(url, json=payload, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=payload, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            self.logger.info("Webhook alert sent")
        
        except Exception as e:
            self.logger.error(f"Error sending webhook alert: {e}")
