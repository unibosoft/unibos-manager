#!/usr/bin/env python3
"""
Import users from old MySQL backup to new PostgreSQL database
Including all additional fields like phone, address, etc.
"""

import os
import re
import django
import sys

# Setup Django
sys.path.append('/Users/berkhatirli/Desktop/unibos/apps/web/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-for-testing')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime

User = get_user_model()

# User data extracted from old backup
users_data = [
    {
        'username': 'berkhatirli', 
        'first_name': 'Berk',
        'last_name': 'Hatırlı',
        'email': 'berk@berkinatolyesi.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$091PoIF9MzHdB9ZOh1cRph$IUBfsslh8K7oYpQXTqmv+wnlDORWvyDNqzEKAB+VKZw=',
        'last_login': '2025-05-22 15:28:02.679808',
        'date_joined': '2024-10-09 15:59:59.341955'
    },
    {
        'username': 'beyhan',
        'email': 'beyhangndz@gmail.com',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$zd8M3zOY8VNSj5wlZzvtaM$QJH1htiP21B+2TUxZNLHLbqklZuM2egNEm4lDPGnA3s=',
        'last_login': '2024-10-27 16:52:57.644951',
        'date_joined': '2024-10-11 11:47:20.595756'
    },
    {
        'username': 'ersan',
        'email': 'ersankolay@gmail.com',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$2XPO0jHRVY8nOEK9AofPKt$RFE/6UElRYk/Xzrq7jNvB3uYLpJhS60fXhR0jMt0P2U=',
        'last_login': '2024-10-18 20:16:45.102813',
        'date_joined': '2024-10-12 19:57:00.055700'
    },
    {
        'username': 'Leventhatirli',
        'email': 'leventhatirli@gmail.com',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$H8pVA9F5rFGOXa01Kjr608$KceCF7pj/tEpGbuqLy/ofHFploXzjOlvXmj3t0tT5Tw=',
        'last_login': '2024-12-16 19:56:00.191357',
        'date_joined': '2024-10-19 20:52:08.212660'
    },
    {
        'username': 'Armutdaldaasilsin',
        'email': 'muratcanb@hotmail.co.uk',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$jFZ8ofsTPpso8yd3gXbA8r$9ohNnXwH53BNhSdSaS8eS1H8uyMSR+Q05rAiWS53exQ=',
        'last_login': '2024-12-16 17:35:52.423195',
        'date_joined': '2024-12-14 20:28:54.577691'
    },
    {
        'username': 'gulcinhatirli',
        'email': 'ghatirli@gmail.com',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$JZuDLs2psUnfPy3KAiWVfT$KPRj52x3lVqE9uAjqyTB3BIz+HKSCoL33Vr7mxWqMUg=',
        'last_login': '2025-05-22 15:31:50.770200',
        'date_joined': '2024-12-15 09:59:48.000000'
    },
    {
        'username': 'euccan@hotmail.com',
        'email': 'euccan@hotmail.com',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$ndRgKnyz8dwZcR28U54BMZ$4SO3qGqm/yHcAbmYPuiBbKlEsED3TdMYxOs/7pCStAg=',
        'last_login': None,
        'date_joined': '2024-12-15 19:20:18.802830'
    },
    {
        'username': 'Aslinda',
        'email': 'asli@vamosbodrum.com',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$DReNaEIrqGtaSwh9mnYFAT$QN5hBo0MsGhdJVvu2mpUcEvmja3VHV9w7yXKigtTiow=',
        'last_login': '2024-12-17 07:43:21.913175',
        'date_joined': '2024-12-17 07:40:56.346319'
    },
    {
        'username': 'berk2',
        'email': 'bhatirli@gmail.com',
        'is_staff': False,
        'is_active': True,
        'password': 'pbkdf2_sha256$870000$GVMEFL21Lp5GqPqORgpizx$Sgz68nIvXFRnyB0oRMtUmxMn3tvw1gvpnNwNO1Ljh/o=',
        'last_login': '2024-12-24 06:53:43.767643',
        'date_joined': '2024-12-24 06:48:02.793003'
    }
]

def parse_datetime(dt_str):
    """Parse datetime string to Django timezone-aware datetime"""
    if not dt_str or dt_str == 'NULL':
        return None
    try:
        # Parse the datetime string
        dt = datetime.strptime(dt_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
        # Make it timezone-aware
        return timezone.make_aware(dt)
    except:
        return None

# Import users
print("Importing users from old database backup...")
print("=" * 50)

for user_data in users_data:
    username = user_data['username']
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        # Update existing user
        user = User.objects.get(username=username)
        user.password = user_data['password']  # Restore original password hash
        user.email = user_data['email']
        user.first_name = user_data.get('first_name', '')
        user.last_name = user_data.get('last_name', '')
        user.is_staff = user_data.get('is_staff', False)
        user.is_superuser = user_data.get('is_superuser', False)
        user.is_active = user_data.get('is_active', True)
        
        last_login = parse_datetime(user_data.get('last_login'))
        if last_login:
            user.last_login = last_login
            
        date_joined = parse_datetime(user_data.get('date_joined'))
        if date_joined:
            user.date_joined = date_joined
            
        # Add phone and other fields if model has them
        if hasattr(user, 'phone'):
            user.phone = user_data.get('phone', '')
        if hasattr(user, 'address'):
            user.address = user_data.get('address', '')
        if hasattr(user, 'last_activity'):
            user.last_activity = parse_datetime(user_data.get('last_activity'))
            
        user.save()
        print(f'✓ Updated user: {username}')
    else:
        # Create new user
        user = User(
            username=username,
            email=user_data['email'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            is_staff=user_data.get('is_staff', False),
            is_superuser=user_data.get('is_superuser', False),
            is_active=user_data.get('is_active', True),
            password=user_data['password']  # Use original password hash
        )
        
        last_login = parse_datetime(user_data.get('last_login'))
        if last_login:
            user.last_login = last_login
            
        date_joined = parse_datetime(user_data.get('date_joined'))
        if date_joined:
            user.date_joined = date_joined
            
        # Add phone and other fields if model has them
        if hasattr(user, 'phone'):
            user.phone = user_data.get('phone', '')
        if hasattr(user, 'address'):
            user.address = user_data.get('address', '')
        if hasattr(user, 'last_activity'):
            user.last_activity = parse_datetime(user_data.get('last_activity'))
            
        user.save()
        print(f'✓ Created user: {username}')

print("=" * 50)
print(f'Total users in database: {User.objects.count()}')
print('\nUser list:')
for user in User.objects.all().order_by('id'):
    status = []
    if user.is_superuser:
        status.append('Superuser')
    if user.is_staff:
        status.append('Staff')
    status_str = f" ({', '.join(status)})" if status else ""
    print(f'  {user.username} - {user.email}{status_str}')

# Check for UserProfile or additional user data
try:
    from modules.users.backend.models import UserProfile
    print("\nChecking UserProfile data...")
    for user in User.objects.all():
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            print(f'  Created profile for: {user.username}')
except ImportError:
    pass

print("\n✅ User import completed successfully!")
print("\nNote: Original passwords have been preserved from the backup.")
print("Users can log in with their original credentials.")