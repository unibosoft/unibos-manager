"""
Management command to test and configure email settings
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import smtplib
from email.mime.text import MIMEText


class Command(BaseCommand):
    help = 'Test email configuration and send test emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            default='bhatirli@gmail.com',
            help='Email address to send test email to'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='New password to test'
        )
        parser.add_argument(
            '--port',
            type=int,
            help='SMTP port to test'
        )

    def handle(self, *args, **options):
        self.stdout.write("testing email configuration...")
        
        # Test configurations
        configs = [
            {"host": "mail.recaria.org", "port": 587, "use_tls": True, "use_ssl": False, "name": "587/TLS"},
            {"host": "mail.recaria.org", "port": 465, "use_tls": False, "use_ssl": True, "name": "465/SSL"},
            {"host": "mail.recaria.org", "port": 25, "use_tls": True, "use_ssl": False, "name": "25/TLS"},
        ]
        
        # Override with command line options
        if options.get('port'):
            port = options['port']
            if port == 465:
                configs = [{"host": "mail.recaria.org", "port": 465, "use_tls": False, "use_ssl": True, "name": "465/SSL"}]
            elif port == 587:
                configs = [{"host": "mail.recaria.org", "port": 587, "use_tls": True, "use_ssl": False, "name": "587/TLS"}]
            else:
                configs = [{"host": "mail.recaria.org", "port": port, "use_tls": True, "use_ssl": False, "name": f"{port}/TLS"}]
        
        email_user = "berk@recaria.org"
        email_pass = options.get('password', 'Recaria2025Mail!')
        test_recipient = options['to']
        
        self.stdout.write(f"testing with user: {email_user}")
        self.stdout.write(f"testing password: {'*' * len(email_pass)}")
        
        for config in configs:
            self.stdout.write(f"\n[{config['name']}] testing port {config['port']}...")
            
            try:
                # Direct SMTP test
                if config["use_ssl"]:
                    server = smtplib.SMTP_SSL(config["host"], config["port"], timeout=10)
                    self.stdout.write(f"  connected via SSL on port {config['port']}")
                else:
                    server = smtplib.SMTP(config["host"], config["port"], timeout=10)
                    self.stdout.write(f"  connected on port {config['port']}")
                    server.ehlo()
                    
                    if config["use_tls"]:
                        server.starttls()
                        server.ehlo()
                        self.stdout.write("  STARTTLS enabled")
                
                # Try authentication
                server.login(email_user, email_pass)
                self.stdout.write(self.style.SUCCESS("  ✓ authentication successful!"))
                
                # Try sending test email
                msg = MIMEText("test email from UNIBOS v524\n\nthis is a test message to verify email configuration.")
                msg["Subject"] = "UNIBOS email test"
                msg["From"] = email_user
                msg["To"] = test_recipient
                
                server.send_message(msg)
                self.stdout.write(self.style.SUCCESS(f"  ✓ test email sent to {test_recipient}"))
                
                server.quit()
                self.stdout.write(self.style.SUCCESS(f"\n✓ SUCCESS: use port {config['port']} with SSL={config['use_ssl']}, TLS={config['use_tls']}"))
                
                # Update Django settings
                self.stdout.write("\nupdating django settings...")
                self.stdout.write(f"EMAIL_HOST = 'mail.recaria.org'")
                self.stdout.write(f"EMAIL_PORT = {config['port']}")
                self.stdout.write(f"EMAIL_USE_TLS = {config['use_tls']}")
                self.stdout.write(f"EMAIL_USE_SSL = {config['use_ssl']}")
                self.stdout.write(f"EMAIL_HOST_USER = '{email_user}'")
                self.stdout.write(f"EMAIL_HOST_PASSWORD = '{email_pass}'")
                
                break
                
            except smtplib.SMTPAuthenticationError as e:
                self.stdout.write(self.style.ERROR(f"  ✗ authentication failed: {e}"))
            except smtplib.SMTPException as e:
                self.stdout.write(self.style.ERROR(f"  ✗ SMTP error: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ connection error: {e}"))