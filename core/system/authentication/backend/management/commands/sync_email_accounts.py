"""
Sync Django users with email server accounts
Creates email accounts for all active users at username@recaria.org
"""

import subprocess
import hashlib
import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync Django users with email server accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Sync only specific user',
        )
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='Reset email password for user',
        )

    def handle(self, *args, **options):
        """Sync Django users with mail server"""
        
        # Check if we're on the server
        try:
            import socket
            hostname = socket.gethostname()
            if 'rocksteady' not in hostname and 'ubuntu' not in hostname:
                self.stdout.write(self.style.WARNING(
                    'This command should be run on the server (rocksteady)'
                ))
                return
        except:
            pass
        
        specific_user = options.get('user')
        reset_password = options.get('reset_password')
        
        # Get users to sync
        if specific_user:
            users = User.objects.filter(username=specific_user, is_active=True)
            if not users.exists():
                self.stdout.write(self.style.ERROR(
                    f'User {specific_user} not found or not active'
                ))
                return
        else:
            users = User.objects.filter(is_active=True)
        
        # Paths
        vmailbox_path = '/etc/postfix/vmailbox'
        dovecot_users_path = '/etc/dovecot/users'
        
        # Sync each user
        synced = 0
        for user in users:
            email = f"{user.username}@recaria.org"
            
            # Generate password (or use existing)
            if reset_password or not hasattr(user, 'email_password'):
                # Generate secure password
                password = secrets.token_urlsafe(16)
                
                # Save to user profile (you might want to encrypt this)
                # For now, we'll just print it
                self.stdout.write(f"Generated password for {email}: {password}")
            else:
                password = getattr(user, 'email_password', secrets.token_urlsafe(16))
            
            # Create password hash for Dovecot (SHA512-CRYPT)
            # In production, use doveadm pw -s SHA512-CRYPT
            try:
                result = subprocess.run(
                    ['doveadm', 'pw', '-s', 'SHA512-CRYPT', '-p', password],
                    capture_output=True,
                    text=True
                )
                password_hash = result.stdout.strip()
            except:
                # Fallback to Python implementation
                import crypt
                salt = crypt.mksalt(crypt.METHOD_SHA512)
                password_hash = crypt.crypt(password, salt)
            
            # Add to vmailbox
            vmailbox_line = f"{email} recaria.org/{user.username}/\n"
            
            try:
                # Read existing vmailbox
                try:
                    with open(vmailbox_path, 'r') as f:
                        vmailbox_content = f.read()
                except FileNotFoundError:
                    vmailbox_content = ""
                
                # Add if not exists
                if email not in vmailbox_content:
                    with open(vmailbox_path, 'a') as f:
                        f.write(vmailbox_line)
                    self.stdout.write(f"Added {email} to vmailbox")
                
                # Add to dovecot users
                dovecot_line = f"{email}:{password_hash}\n"
                
                try:
                    with open(dovecot_users_path, 'r') as f:
                        dovecot_content = f.read()
                except FileNotFoundError:
                    dovecot_content = ""
                
                # Update or add user
                if email in dovecot_content:
                    # Update existing
                    lines = dovecot_content.split('\n')
                    new_lines = []
                    for line in lines:
                        if line.startswith(f"{email}:"):
                            new_lines.append(dovecot_line.strip())
                        else:
                            new_lines.append(line)
                    
                    with open(dovecot_users_path, 'w') as f:
                        f.write('\n'.join(new_lines))
                    self.stdout.write(f"Updated {email} in dovecot")
                else:
                    # Add new
                    with open(dovecot_users_path, 'a') as f:
                        f.write(dovecot_line)
                    self.stdout.write(f"Added {email} to dovecot")
                
                # Create mail directory
                mail_dir = f"/var/mail/vhosts/recaria.org/{user.username}"
                subprocess.run(['sudo', 'mkdir', '-p', mail_dir])
                subprocess.run(['sudo', 'chown', '-R', 'vmail:vmail', mail_dir])
                
                synced += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Failed to sync {email}: {str(e)}"
                ))
        
        # Update postfix maps
        try:
            subprocess.run(['sudo', 'postmap', '/etc/postfix/vmailbox'])
            subprocess.run(['sudo', 'postmap', '/etc/postfix/virtual'])
            subprocess.run(['sudo', 'systemctl', 'reload', 'postfix'])
            subprocess.run(['sudo', 'systemctl', 'reload', 'dovecot'])
            
            self.stdout.write(self.style.SUCCESS(
                f"✅ Synced {synced} users to email server"
            ))
            self.stdout.write(
                "Users can now access their email at username@recaria.org"
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Failed to reload services: {str(e)}"
            ))