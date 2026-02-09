from utils.logger import log_info, log_error
import os


class NotificationService:
    """Service for sending notifications"""
    
    NOTIFICATION_TYPE = os.getenv('NOTIFICATION_TYPE', 'console')
    
    @staticmethod
    def send_notification(email, subject, message):
        """Send notification to user"""
        try:
            from flask import current_app
            notification_type = current_app.config.get('NOTIFICATION_TYPE', 'console')
            
            if notification_type == 'email':
                NotificationService._send_email(email, subject, message)
            else:
                NotificationService._send_console(email, subject, message)
            
            log_info(f"Notification sent to {email}: {subject}")
            return True
        
        except Exception as e:
            log_error(f"Error sending notification: {str(e)}")
            return False
    
    @staticmethod
    def _send_console(email, subject, message):
        """Send notification to console"""
        print(f"\n{'='*60}")
        print(f"NOTIFICATION TO: {email}")
        print(f"SUBJECT: {subject}")
        print(f"MESSAGE:\n{message}")
        print(f"{'='*60}\n")
    
    @staticmethod
    def _send_email(email, subject, message):
        """Send notification via email using SMTP"""
        try:
            from flask import current_app
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_host = current_app.config['SMTP_HOST']
            smtp_port = current_app.config['SMTP_PORT']
            smtp_user = current_app.config['SMTP_USER']
            smtp_pass = current_app.config['SMTP_PASS']

            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            
            log_info(f"Email sent successfully to {email}")
        except Exception as e:
            log_error(f"Failed to send email to {email}: {str(e)}")
            # Fallback to console for debugging
            NotificationService._send_console(email, subject, f"{message}\n\n[FALLBACK: Email failed]")
