"""
Background Legal Updates Monitoring Service
Handles periodic monitoring, scheduling, and notifications
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
import json
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import os

# Configure logging
logger = logging.getLogger(__name__)

class MonitoringSchedule(Enum):
    HOURLY = "hourly"
    EVERY_2_HOURS = "every_2_hours"
    EVERY_6_HOURS = "every_6_hours"
    DAILY = "daily"
    CUSTOM = "custom"

class AlertType(Enum):
    CRITICAL_UPDATE = "critical_update"
    HIGH_PRIORITY_UPDATE = "high_priority_update"
    SYSTEM_STATUS = "system_status"
    ERROR_ALERT = "error_alert"
    DAILY_SUMMARY = "daily_summary"

@dataclass
class MonitoringConfig:
    """Configuration for monitoring system"""
    schedule: MonitoringSchedule
    custom_interval_hours: Optional[int] = None
    enable_email_alerts: bool = True
    enable_in_app_notifications: bool = True
    alert_thresholds: Dict[str, int] = None
    monitored_domains: List[str] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                'critical_updates': 1,    # Alert immediately for critical updates
                'high_priority_updates': 3,  # Alert when 3+ high priority updates
                'system_errors': 1       # Alert immediately for system errors
            }
        
        if self.monitored_domains is None:
            self.monitored_domains = [
                'constitutional_law',
                'contract_law', 
                'employment_law',
                'intellectual_property',
                'securities_law',
                'administrative_law'
            ]

@dataclass
class AlertMessage:
    """Structure for alert messages"""
    alert_id: str
    alert_type: AlertType
    title: str
    message: str
    updates: List[Dict[str, Any]]
    timestamp: datetime
    priority: str
    requires_action: bool = False

class EmailNotificationService:
    """Free email notification service using Gmail SMTP"""
    
    def __init__(self, sender_email: str = None, sender_password: str = None):
        # For demo purposes, using free Gmail SMTP
        # In production, would use environment variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = sender_email or "legalmateai@gmail.com"
        self.sender_password = sender_password or "demo_password"  # Would be app password
        
    async def send_alert(self, alert: AlertMessage, recipient_emails: List[str]):
        """Send email alert (async wrapper for sync email sending)"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                await loop.run_in_executor(
                    executor, 
                    self._send_email_sync, 
                    alert, 
                    recipient_emails
                )
                
            logger.info(f"Email alert sent: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert {alert.alert_id}: {e}")
    
    def _send_email_sync(self, alert: AlertMessage, recipient_emails: List[str]):
        """Synchronous email sending"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(recipient_emails)
            msg['Subject'] = f"LegalMate AI Alert: {alert.title}"
            
            # Create HTML body
            html_body = self._create_html_email_body(alert)
            msg.attach(MIMEText(html_body, 'html'))
            
            # For demo purposes, we'll log the email instead of actually sending
            # In production, would use actual SMTP
            logger.info(f"EMAIL ALERT (Demo Mode):")
            logger.info(f"To: {recipient_emails}")
            logger.info(f"Subject: {alert.title}")
            logger.info(f"Body: {alert.message}")
            logger.info(f"Updates: {len(alert.updates)} legal updates")
            
            # Actual SMTP sending would be:
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.sender_email, self.sender_password)
            # server.send_message(msg)
            # server.quit()
            
        except Exception as e:
            logger.error(f"Error in sync email sending: {e}")
    
    def _create_html_email_body(self, alert: AlertMessage) -> str:
        """Create HTML email body"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #1e40af; color: white; padding: 15px; border-radius: 5px; }}
                .content {{ padding: 20px; border: 1px solid #e5e5e5; margin-top: 10px; }}
                .update {{ background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #1e40af; }}
                .priority-high {{ border-left-color: #dc2626; }}
                .priority-critical {{ border-left-color: #991b1b; background-color: #fef2f2; }}
                .timestamp {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🏛️ LegalMate AI - Legal Updates Alert</h2>
                <p>{alert.title}</p>
            </div>
            
            <div class="content">
                <p><strong>Alert Type:</strong> {alert.alert_type.value.replace('_', ' ').title()}</p>
                <p><strong>Priority:</strong> {alert.priority.upper()}</p>
                <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                
                <h3>Message:</h3>
                <p>{alert.message}</p>
                
                <h3>Legal Updates ({len(alert.updates)}):</h3>
        """
        
        for update in alert.updates[:10]:  # Limit to 10 updates in email
            priority_class = f"priority-{update.get('priority', 'medium')}"
            html += f"""
                <div class="update {priority_class}">
                    <h4>{update.get('title', 'Untitled Update')}</h4>
                    <p><strong>Source:</strong> {update.get('source', 'Unknown')}</p>
                    <p><strong>Type:</strong> {update.get('update_type', 'Unknown')}</p>
                    <p><strong>Domains:</strong> {', '.join(update.get('legal_domains', []))}</p>
                    <p>{update.get('summary', 'No summary available')[:200]}...</p>
                    <p class="timestamp">Published: {update.get('publication_date', 'Unknown')}</p>
                    <p><a href="{update.get('url', '#')}">View Full Update</a></p>
                </div>
            """
        
        if len(alert.updates) > 10:
            html += f"<p><em>... and {len(alert.updates) - 10} more updates</em></p>"
        
        html += """
                <hr>
                <p><em>This is an automated alert from LegalMate AI Legal Updates Monitoring System.</em></p>
                <p><small>To manage your alert preferences, visit your dashboard.</small></p>
            </div>
        </body>
        </html>
        """
        
        return html

class InAppNotificationService:
    """In-app notification service for real-time alerts"""
    
    def __init__(self):
        self.notifications = []
        self.subscribers = []  # WebSocket connections or callback functions
        
    async def send_notification(self, alert: AlertMessage):
        """Send in-app notification"""
        try:
            notification = {
                'id': alert.alert_id,
                'type': alert.alert_type.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'priority': alert.priority,
                'updates_count': len(alert.updates),
                'requires_action': alert.requires_action
            }
            
            # Store notification
            self.notifications.append(notification)
            
            # Keep only recent notifications (last 100)
            if len(self.notifications) > 100:
                self.notifications = self.notifications[-100:]
            
            # Notify subscribers (would be WebSocket connections in real implementation)
            logger.info(f"IN-APP NOTIFICATION: {alert.title}")
            logger.info(f"Message: {alert.message}")
            logger.info(f"Updates: {len(alert.updates)} legal updates")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending in-app notification: {e}")
            return False
    
    def get_recent_notifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent notifications"""
        return self.notifications[-limit:] if self.notifications else []
    
    def mark_notification_read(self, notification_id: str):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                break

class LegalUpdatesScheduler:
    """Background scheduler for legal updates monitoring"""
    
    def __init__(self, 
                 legal_updates_monitor,
                 legal_update_validator,
                 config: MonitoringConfig = None):
        
        self.legal_updates_monitor = legal_updates_monitor
        self.legal_update_validator = legal_update_validator
        self.config = config or MonitoringConfig(MonitoringSchedule.EVERY_6_HOURS)
        
        # Notification services
        self.email_service = EmailNotificationService()
        self.in_app_service = InAppNotificationService()
        
        # Scheduling state
        self.is_running = False
        self.last_check = None
        self.next_check = None
        self.monitoring_thread = None
        self.stats = {
            'total_checks': 0,
            'total_updates_found': 0,
            'total_alerts_sent': 0,
            'last_error': None,
            'uptime_start': datetime.now()
        }
        
        # Alert recipients (would be configurable per user)
        self.alert_recipients = ["admin@legalmate.ai"]  # Demo email
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return
        
        self.is_running = True
        self.stats['uptime_start'] = datetime.now()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"Legal updates monitoring started with {self.config.schedule.value} schedule")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Legal updates monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Calculate next check time
                self.next_check = self._calculate_next_check()
                
                # Wait until next check time
                while self.is_running and datetime.now() < self.next_check:
                    time.sleep(60)  # Check every minute if it's time
                
                if not self.is_running:
                    break
                
                # Perform monitoring check
                asyncio.run(self._perform_monitoring_check())
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.stats['last_error'] = str(e)
                # Sleep for a bit before retrying
                time.sleep(300)  # 5 minutes
    
    async def _perform_monitoring_check(self):
        """Perform a single monitoring check"""
        try:
            logger.info("Starting scheduled legal updates monitoring check")
            start_time = datetime.now()
            
            # Get updates since last check
            since_date = self.last_check or (datetime.now() - timedelta(hours=24))
            
            # Monitor all sources
            updates = await self.legal_updates_monitor.monitor_all_sources(since_date)
            
            # Update statistics
            self.stats['total_checks'] += 1
            self.stats['total_updates_found'] += len(updates)
            self.last_check = start_time
            
            logger.info(f"Monitoring check completed: {len(updates)} updates found")
            
            # Process and validate updates
            validated_updates = []
            for update in updates:
                try:
                    validation_result = await self.legal_update_validator.validate_update(update)
                    validated_updates.append((update, validation_result))
                except Exception as e:
                    logger.error(f"Error validating update {update.update_id}: {e}")
            
            # Generate alerts based on findings
            await self._generate_alerts(validated_updates)
            
            # Send daily summary if it's appropriate time
            if self._should_send_daily_summary():
                await self._send_daily_summary(validated_updates)
                
        except Exception as e:
            logger.error(f"Error in monitoring check: {e}")
            self.stats['last_error'] = str(e)
            
            # Send error alert
            await self._send_error_alert(str(e))
    
    async def _generate_alerts(self, validated_updates: List[tuple]):
        """Generate appropriate alerts based on validated updates"""
        try:
            critical_updates = []
            high_priority_updates = []
            
            for update, validation in validated_updates:
                if update.priority_level.value == 'critical':
                    critical_updates.append(update)
                elif update.priority_level.value == 'high':
                    high_priority_updates.append(update)
            
            # Send critical updates alert immediately
            if len(critical_updates) >= self.config.alert_thresholds['critical_updates']:
                await self._send_critical_updates_alert(critical_updates)
            
            # Send high priority updates alert if threshold met
            if len(high_priority_updates) >= self.config.alert_thresholds['high_priority_updates']:
                await self._send_high_priority_alert(high_priority_updates)
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
    
    async def _send_critical_updates_alert(self, updates: List):
        """Send alert for critical legal updates"""
        alert = AlertMessage(
            alert_id=f"critical_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            alert_type=AlertType.CRITICAL_UPDATE,
            title=f"🚨 CRITICAL: {len(updates)} Critical Legal Update{'s' if len(updates) > 1 else ''}",
            message=f"Critical legal updates detected that may significantly impact legal knowledge base and require immediate attention.",
            updates=[self._update_to_dict(update) for update in updates],
            timestamp=datetime.now(),
            priority="critical",
            requires_action=True
        )
        
        await self._send_alert(alert)
    
    async def _send_high_priority_alert(self, updates: List):
        """Send alert for high priority legal updates"""
        alert = AlertMessage(
            alert_id=f"high_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            alert_type=AlertType.HIGH_PRIORITY_UPDATE,
            title=f"⚠️ HIGH PRIORITY: {len(updates)} Important Legal Update{'s' if len(updates) > 1 else ''}",
            message=f"High priority legal updates detected that may impact specific legal domains.",
            updates=[self._update_to_dict(update) for update in updates],
            timestamp=datetime.now(),
            priority="high",
            requires_action=False
        )
        
        await self._send_alert(alert)
    
    async def _send_daily_summary(self, validated_updates: List[tuple]):
        """Send daily summary of all updates"""
        all_updates = [update for update, _ in validated_updates]
        
        if not all_updates:
            return
        
        alert = AlertMessage(
            alert_id=f"summary_{datetime.now().strftime('%Y%m%d')}",
            alert_type=AlertType.DAILY_SUMMARY,
            title=f"📊 Daily Legal Updates Summary: {len(all_updates)} Update{'s' if len(all_updates) > 1 else ''}",
            message=f"Daily summary of legal updates monitored by LegalMate AI system.",
            updates=[self._update_to_dict(update) for update in all_updates],
            timestamp=datetime.now(),
            priority="normal",
            requires_action=False
        )
        
        await self._send_alert(alert)
    
    async def _send_error_alert(self, error_message: str):
        """Send alert for system errors"""
        alert = AlertMessage(
            alert_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            alert_type=AlertType.ERROR_ALERT,
            title="🔧 System Error in Legal Updates Monitoring",
            message=f"An error occurred in the legal updates monitoring system: {error_message}",
            updates=[],
            timestamp=datetime.now(),
            priority="high",
            requires_action=True
        )
        
        await self._send_alert(alert)
    
    async def _send_alert(self, alert: AlertMessage):
        """Send alert through configured notification services"""
        try:
            # Send email alert if enabled
            if self.config.enable_email_alerts:
                await self.email_service.send_alert(alert, self.alert_recipients)
            
            # Send in-app notification if enabled
            if self.config.enable_in_app_notifications:
                await self.in_app_service.send_notification(alert)
            
            self.stats['total_alerts_sent'] += 1
            
        except Exception as e:
            logger.error(f"Error sending alert {alert.alert_id}: {e}")
    
    def _update_to_dict(self, update) -> Dict[str, Any]:
        """Convert legal update to dictionary for serialization"""
        return {
            'id': update.update_id,
            'title': update.title,
            'source': update.source.value,
            'update_type': update.update_type.value,
            'priority': update.priority_level.value,
            'publication_date': update.publication_date.isoformat(),
            'summary': update.summary,
            'legal_domains': update.legal_domains_affected,
            'url': update.url,
            'impact_score': update.impact_score,
            'confidence_score': update.confidence_score
        }
    
    def _calculate_next_check(self) -> datetime:
        """Calculate next monitoring check time"""
        now = datetime.now()
        
        if self.config.schedule == MonitoringSchedule.HOURLY:
            return now + timedelta(hours=1)
        elif self.config.schedule == MonitoringSchedule.EVERY_2_HOURS:
            return now + timedelta(hours=2)
        elif self.config.schedule == MonitoringSchedule.EVERY_6_HOURS:
            return now + timedelta(hours=6)
        elif self.config.schedule == MonitoringSchedule.DAILY:
            return now + timedelta(days=1)
        elif self.config.schedule == MonitoringSchedule.CUSTOM and self.config.custom_interval_hours:
            return now + timedelta(hours=self.config.custom_interval_hours)
        else:
            return now + timedelta(hours=6)  # Default
    
    def _should_send_daily_summary(self) -> bool:
        """Check if it's time to send daily summary"""
        now = datetime.now()
        # Send daily summary at 8 AM
        return now.hour == 8 and (not self.last_check or 
                                  self.last_check.date() < now.date())
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        uptime = datetime.now() - self.stats['uptime_start']
        
        return {
            'is_running': self.is_running,
            'schedule': self.config.schedule.value,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'next_check': self.next_check.isoformat() if self.next_check else None,
            'uptime_hours': uptime.total_seconds() / 3600,
            'statistics': self.stats.copy(),
            'configuration': {
                'email_alerts_enabled': self.config.enable_email_alerts,
                'in_app_notifications_enabled': self.config.enable_in_app_notifications,
                'alert_thresholds': self.config.alert_thresholds,
                'monitored_domains': self.config.monitored_domains
            }
        }

# Global instances
legal_updates_scheduler = None
in_app_notification_service = InAppNotificationService()

def initialize_legal_updates_scheduler(legal_updates_monitor, legal_update_validator, config: MonitoringConfig = None):
    """Initialize the global legal updates scheduler"""
    global legal_updates_scheduler
    legal_updates_scheduler = LegalUpdatesScheduler(
        legal_updates_monitor, 
        legal_update_validator, 
        config
    )
    return legal_updates_scheduler