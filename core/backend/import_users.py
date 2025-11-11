#!/usr/bin/env python
"""
Import users from PostgreSQL dump to SQLite database
"""

import os
import sys
import django
import uuid
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# User data from PostgreSQL dump
users_data = [
    {
        'username': 'berkhatirli',
        'password': 'pbkdf2_sha256$720000$K1kngUEfoZXw0fmZDeRuY0$qpIXNi6Stky26xKvwfo/Ii7zW+p5EoqLOPpl1iKU7Jw=',
        'email': 'berk@unibos.com',
        'first_name': 'Berk',
        'last_name': 'Hatırlı',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
        'date_joined': '2025-08-09 08:56:20.712157+03',
        'last_login': '2025-08-19 10:10:25.522759+03'
    },
    {
        'username': 'admin',
        'password': 'pbkdf2_sha256$720000$GAeKTx6kvEZM4MgKHUNXYN$cuDqNYPs2BUI8CYNzbBZ4xRhuvdOw2J/nTQGAazhlpY=',
        'email': 'admin@unibos.com',
        'first_name': '',
        'last_name': '',
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
        'date_joined': '2025-08-19 09:40:56.232978+03',
        'last_login': None
    }
]

def parse_datetime(dt_str):
    """Parse datetime string from PostgreSQL format"""
    if not dt_str:
        return None
    # Remove timezone info for simplicity
    dt_str = dt_str.replace('+03', '')
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
    except:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

def import_users():
    """Import users from PostgreSQL data"""
    
    for user_data in users_data:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User {username} already exists, skipping...")
            continue
        
        # Create user with UUID
        user = User(
            id=uuid.uuid4(),
            username=username,
            password=user_data['password'],  # Already hashed
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            is_superuser=user_data.get('is_superuser', False),
            is_staff=user_data.get('is_staff', False),
            is_active=user_data.get('is_active', True),
            is_verified=True,  # Custom field
            
            # Default values for custom fields
            phone_number='',
            bio='',
            country='TR',
            city='Istanbul',
            user_timezone='Europe/Istanbul',
            language='tr',
            theme='light',
            notifications_enabled=True,
            email_notifications=True,
            verification_token='',
            require_password_change=False,
            login_count=0,
        )
        
        # Set datetime fields
        if user_data.get('date_joined'):
            user.date_joined = parse_datetime(user_data['date_joined'])
        if user_data.get('last_login'):
            user.last_login = parse_datetime(user_data['last_login'])
        
        # Set last_password_change to date_joined
        user.last_password_change = user.date_joined
        
        # Save user
        user.save()
        print(f"✅ Created user: {username} ({user.email})")
        
        # Also check/create screen lock for berkhatirli
        if username == 'berkhatirli':
            from modules.administration.backend.models import ScreenLock
            screen_lock, created = ScreenLock.objects.get_or_create(
                user=user,
                defaults={
                    'is_enabled': True,
                    'lock_password': 'lplp',  # The known password
                    'failed_attempts': 0,
                    'max_failed_attempts': 5,
                    'lockout_duration': 60,
                }
            )
            if created:
                print(f"  ✅ Created screen lock for {username} with password: lplp")
            else:
                # Update existing screen lock password
                screen_lock.lock_password = 'lplp'
                screen_lock.is_enabled = True
                screen_lock.save()
                print(f"  ✅ Updated screen lock for {username} with password: lplp")

if __name__ == '__main__':
    print("=== Importing Users from PostgreSQL Dump ===")
    import_users()
    
    # Show all users
    print("\n=== All Users in Database ===")
    for user in User.objects.all():
        print(f"- {user.username}: {user.email} (superuser: {user.is_superuser})")
