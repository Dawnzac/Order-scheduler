
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def test_email_sending():
    print("Testing Email Configuration...")
    
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER', 'rykerx066@gmail.com')
    smtp_pass = os.environ.get('SMTP_PASS', '')
    
    recipient = "zacturin@gmail.com"  # Hardcoded for testing or use same as sender
    
    print(f"SMTP Host: {smtp_host}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP User: {smtp_user}")
    print(f"SMTP Pass: {'*' * len(smtp_pass) if smtp_pass else 'None'}")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient
        msg['Subject'] = "Turinix Test Email"
        msg.attach(MIMEText("This is a test email from the Turinix Order Scheduler debug script.", 'plain'))

        print(f"Attempting to connect to {smtp_host}:{smtp_port}...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.set_debuglevel(1) 
        
        print("Starting TLS...")
        server.starttls()
        
        print("Logging in...")
        server.login(smtp_user, smtp_pass)
        
        print(f"Sending email to {recipient}...")
        server.send_message(msg)
        
        print("Quitting...")
        server.quit()
        
        print("\n✅ Email sent successfully!")
        
    except Exception as e:
        print(f"\n❌ Failed to send email: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_sending()
