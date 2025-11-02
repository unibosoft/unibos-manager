#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
import sys

# Test different configurations
configs = [
    {"host": "mail.recaria.org", "port": 587, "use_tls": True, "use_ssl": False, "name": "587/TLS"},
    {"host": "mail.recaria.org", "port": 465, "use_tls": False, "use_ssl": True, "name": "465/SSL"},
    {"host": "mail.recaria.org", "port": 25, "use_tls": False, "use_ssl": False, "name": "25/Plain"},
    {"host": "mail.recaria.org", "port": 25, "use_tls": True, "use_ssl": False, "name": "25/TLS"},
]

email_user = "berk@recaria.org"
email_pass = "Recaria2025Mail!"
test_recipient = "bhatirli@gmail.com"

print("Testing SMTP configurations for recaria.org mail server")
print("=" * 60)

for config in configs:
    print(f"\n[{config['name']}] Testing port {config['port']}...")
    
    try:
        # Connect to server
        if config["use_ssl"]:
            server = smtplib.SMTP_SSL(config["host"], config["port"], timeout=10)
            print(f"  Connected via SSL on port {config['port']}")
        else:
            server = smtplib.SMTP(config["host"], config["port"], timeout=10)
            print(f"  Connected on port {config['port']}")
            server.ehlo()
            
            if config["use_tls"]:
                server.starttls()
                server.ehlo()
                print(f"  STARTTLS enabled")
        
        # Try authentication
        server.login(email_user, email_pass)
        print(f"  ✅ Authentication successful!")
        
        # Try sending test email
        msg = MIMEText("Test email from UNIBOS v524\n\nThis is a test message to verify email configuration.")
        msg["Subject"] = "UNIBOS Email Test"
        msg["From"] = email_user
        msg["To"] = test_recipient
        
        server.send_message(msg)
        print(f"  ✅ Test email sent to {test_recipient}")
        
        server.quit()
        print(f"\n✅ SUCCESS: Use port {config['port']} with", end=" ")
        if config["use_ssl"]:
            print("SSL=True, TLS=False")
        elif config["use_tls"]:
            print("SSL=False, TLS=True")
        else:
            print("SSL=False, TLS=False")
        break
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"  ❌ Authentication failed: {e}")
    except smtplib.SMTPException as e:
        print(f"  ❌ SMTP error: {e}")
    except Exception as e:
        print(f"  ❌ Connection error: {e}")

print("\n" + "=" * 60)