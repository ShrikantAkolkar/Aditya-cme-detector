import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import logging
from typing import Dict, List, Optional
from datetime import datetime
from src.config import config

logger = logging.getLogger(__name__)

class AlertManager:
    """Manage alerts for CME events"""
    
    def __init__(self):
        self.email_config = {
            'host': config.email_host,
            'port': config.email_port,
            'user': config.email_user,
            'password': config.email_password
        }
        
        # Initialize Twilio client
        self.twilio_client = None
        if config.twilio_account_sid and config.twilio_auth_token:
            self.twilio_client = Client(
                config.twilio_account_sid,
                config.twilio_auth_token
            )
        
        self.alert_recipients = {
            'email': ['scientist@isro.gov.in', 'spaceweather@isro.gov.in'],
            'sms': ['+91XXXXXXXXXX']  # Replace with actual numbers
        }
    
    async def send_cme_alert(self, event: Dict):
        """Send CME alert via multiple channels"""
        logger.info(f"Sending CME alert for event: {event['id']}")
        
        # Determine alert severity
        severity = self._determine_severity(event)
        
        # Create alert message
        message = self._create_alert_message(event, severity)
        
        # Send alerts based on severity
        tasks = []
        
        if severity in ['high', 'critical']:
            # Send email alerts
            tasks.append(self._send_email_alert(event, message, severity))
            
            # Send SMS alerts for critical events
            if severity == 'critical' and self.twilio_client:
                tasks.append(self._send_sms_alert(event, message))
        
        # Send webhook alerts if configured
        webhook_url = config.get('alerts.webhook.url')
        if webhook_url and config.get('alerts.webhook.enabled', False):
            tasks.append(self._send_webhook_alert(event, webhook_url))
        
        # Execute all alert tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"CME alert sent for event: {event['id']}")
    
    def _determine_severity(self, event: Dict) -> str:
        """Determine alert severity based on event characteristics"""
        confidence = event.get('confidence', 0)
        velocity = event.get('velocity', 0)
        event_type = event.get('type', 'non_halo')
        
        if event_type == 'halo' and confidence > 0.9 and velocity > 1000:
            return 'critical'
        elif event_type in ['halo', 'partial_halo'] and confidence > 0.8:
            return 'high'
        elif confidence > 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _create_alert_message(self, event: Dict, severity: str) -> str:
        """Create formatted alert message"""
        timestamp = event['timestamp']
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        message = f"""
🚨 ADITYA-L1 CME ALERT - {severity.upper()} SEVERITY 🚨

Event ID: {event['id']}
Detection Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
Event Type: {event['type'].replace('_', ' ').title()}
Velocity: {event['velocity']:.0f} km/s
Confidence: {event['confidence']:.1%}
Source: {event['source'].upper()}

Event Characteristics:
- Width: {event.get('width', 'N/A')}°
- Acceleration: {event.get('acceleration', 'N/A')} m/s²
- Magnitude: {event.get('magnitude', 'N/A')}

Coordinates:
- Latitude: {event['coordinates']['latitude']:.2f}°
- Longitude: {event['coordinates']['longitude']:.2f}°

This is an automated alert from the Aditya-L1 CME Detection System.
For more information, visit the mission dashboard.

ISRO Space Weather Monitoring Team
        """.strip()
        
        return message
    
    async def _send_email_alert(self, event: Dict, message: str, severity: str):
        """Send email alert"""
        try:
            if not all([self.email_config['host'], self.email_config['user'], self.email_config['password']]):
                logger.warning("Email configuration incomplete, skipping email alert")
                return
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['user']
            msg['To'] = ', '.join(self.alert_recipients['email'])
            msg['Subject'] = f"🚨 Aditya-L1 CME Alert - {severity.upper()} - {event['id']}"
            
            # Add HTML body
            html_message = self._create_html_message(event, message, severity)
            msg.attach(MIMEText(html_message, 'html'))
            
            # Send email
            with smtplib.SMTP(self.email_config['host'], self.email_config['port']) as server:
                server.starttls()
                server.login(self.email_config['user'], self.email_config['password'])
                server.send_message(msg)
            
            logger.info(f"Email alert sent for event: {event['id']}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    async def _send_sms_alert(self, event: Dict, message: str):
        """Send SMS alert via Twilio"""
        try:
            if not self.twilio_client:
                logger.warning("Twilio client not configured, skipping SMS alert")
                return
            
            # Create short SMS message
            sms_message = f"🚨 ADITYA-L1 CME ALERT\n{event['id']}\nType: {event['type']}\nVelocity: {event['velocity']:.0f} km/s\nConfidence: {event['confidence']:.1%}"
            
            # Send SMS to all recipients
            for phone_number in self.alert_recipients['sms']:
                message = self.twilio_client.messages.create(
                    body=sms_message,
                    from_=config.twilio_phone_number,
                    to=phone_number
                )
                logger.info(f"SMS alert sent to {phone_number}: {message.sid}")
                
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
    
    async def _send_webhook_alert(self, event: Dict, webhook_url: str):
        """Send webhook alert"""
        try:
            import aiohttp
            
            payload = {
                'event_type': 'cme_detection',
                'timestamp': datetime.now().isoformat(),
                'event': event,
                'source': 'aditya-cme-detector'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Webhook alert sent for event: {event['id']}")
                    else:
                        logger.warning(f"Webhook alert failed with status: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def _create_html_message(self, event: Dict, message: str, severity: str) -> str:
        """Create HTML formatted email message"""
        severity_colors = {
            'low': '#3B82F6',
            'medium': '#F59E0B',
            'high': '#EF4444',
            'critical': '#DC2626'
        }
        
        color = severity_colors.get(severity, '#6B7280')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .event-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
                .severity-badge {{ display: inline-block; padding: 5px 10px; border-radius: 15px; color: white; background-color: {color}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛰️ Aditya-L1 CME Detection Alert</h1>
                    <span class="severity-badge">{severity.upper()} SEVERITY</span>
                </div>
                <div class="content">
                    <h2>Event Details</h2>
                    <div class="event-details">
                        <p><strong>Event ID:</strong> {event['id']}</p>
                        <p><strong>Detection Time:</strong> {event['timestamp']}</p>
                        <p><strong>Event Type:</strong> {event['type'].replace('_', ' ').title()}</p>
                        <p><strong>Velocity:</strong> {event['velocity']:.0f} km/s</p>
                        <p><strong>Confidence:</strong> {event['confidence']:.1%}</p>
                        <p><strong>Source:</strong> {event['source'].upper()}</p>
                    </div>
                    
                    <h3>Event Characteristics</h3>
                    <ul>
                        <li>Width: {event.get('width', 'N/A')}°</li>
                        <li>Acceleration: {event.get('acceleration', 'N/A')} m/s²</li>
                        <li>Magnitude: {event.get('magnitude', 'N/A')}</li>
                    </ul>
                    
                    <h3>Coordinates</h3>
                    <ul>
                        <li>Latitude: {event['coordinates']['latitude']:.2f}°</li>
                        <li>Longitude: {event['coordinates']['longitude']:.2f}°</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>This is an automated alert from the Aditya-L1 CME Detection System</p>
                    <p>Indian Space Research Organisation (ISRO) - Space Weather Monitoring Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def send_system_alert(self, alert_type: str, message: str, severity: str = 'medium'):
        """Send system-level alerts (maintenance, errors, etc.)"""
        logger.info(f"Sending system alert: {alert_type}")
        
        try:
            if severity in ['high', 'critical']:
                # Send email for system alerts
                msg = MIMEMultipart()
                msg['From'] = self.email_config['user']
                msg['To'] = ', '.join(self.alert_recipients['email'])
                msg['Subject'] = f"🔧 Aditya-L1 System Alert - {alert_type}"
                
                body = f"""
System Alert: {alert_type}
Severity: {severity.upper()}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Message:
{message}

Please check the system dashboard for more details.

Aditya-L1 CME Detection System
                """.strip()
                
                msg.attach(MIMEText(body, 'plain'))
                
                with smtplib.SMTP(self.email_config['host'], self.email_config['port']) as server:
                    server.starttls()
                    server.login(self.email_config['user'], self.email_config['password'])
                    server.send_message(msg)
                
                logger.info(f"System alert sent: {alert_type}")
                
        except Exception as e:
            logger.error(f"Failed to send system alert: {e}")