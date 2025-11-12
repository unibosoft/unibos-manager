#!/usr/bin/env python3
"""
Import users from old Unicorn database SQL backup to new UNIBOS database
"""

import os
import sys
import django
import re
from datetime import datetime

# Django setup
sys.path.append('/Users/berkhatirli/Desktop/unibos/apps/web/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from django.contrib.auth.models import User
from core.models.base import UserProfile
from django.db import transaction

def parse_sql_insert(line, table_name):
    """Parse SQL INSERT statement and extract values"""
    pattern = f"INSERT INTO `{table_name}` VALUES (.+);"
    match = re.match(pattern, line)
    if not match:
        return []
    
    values_str = match.group(1)
    # Parse the values - this is simplified and may need adjustment for complex data
    records = []
    current_record = []
    in_string = False
    current_value = ""
    paren_level = 0
    
    for char in values_str:
        if char == "'" and (len(current_value) == 0 or current_value[-1] != '\\'):
            in_string = not in_string
            current_value += char
        elif char == '(' and not in_string:
            if paren_level == 0:
                current_record = []
            paren_level += 1
        elif char == ')' and not in_string:
            paren_level -= 1
            if paren_level == 0:
                if current_value:
                    current_record.append(current_value.strip("'"))
                    current_value = ""
                records.append(current_record)
        elif char == ',' and not in_string and paren_level == 1:
            current_record.append(current_value.strip("'"))
            current_value = ""
        else:
            current_value += char
    
    return records

def import_users_from_sql():
    """Import users from SQL backup file"""
    sql_file = '/Users/berkhatirli/Desktop/unibos/import/unicorn_db_backup_v030-beta_2025_05_22_19_50.sql'
    
    # Read the SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and parse auth_user data
    users_data = []
    profiles_data = []
    
    for line in lines:
        if line.startswith("INSERT INTO `auth_user` VALUES"):
            # Extract user data manually
            # Based on the structure we saw in the SQL
            user_line = line.strip()
            # Parse the INSERT statement
            if '(1,' in user_line:  # berkhatirli
                users_data.append({
                    'id': 1,
                    'username': 'berkhatirli_old',
                    'email': 'berk@berkinatolyesi.com',
                    'first_name': 'Berk',
                    'last_name': 'Hatırlı',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                    'phone': '5323672225'
                })
            if '(4,' in user_line:  # beyhan
                users_data.append({
                    'id': 4,
                    'username': 'beyhan',
                    'email': 'beyhangndz@gmail.com',
                    'first_name': '',
                    'last_name': '',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'phone': None
                })
            if '(5,' in user_line:  # ersan
                users_data.append({
                    'id': 5,
                    'username': 'ersan',
                    'email': 'ersankolay@gmail.com',
                    'first_name': '',
                    'last_name': '',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'phone': None
                })
            if '(6,' in user_line:  # Leventhatirli
                users_data.append({
                    'id': 6,
                    'username': 'leventhatirli',
                    'email': 'leventhatirli@gmail.com',
                    'first_name': '',
                    'last_name': '',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'phone': None
                })
            if '(27,' in user_line:  # Armutdaldaasilsin
                users_data.append({
                    'id': 27,
                    'username': 'armutdaldaasilsin',
                    'email': 'muratcanb@hotmail.co.uk',
                    'first_name': '',
                    'last_name': '',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'phone': None
                })
            if '(28,' in user_line:  # gulcinhatirli
                users_data.append({
                    'id': 28,
                    'username': 'gulcinhatirli',
                    'email': 'ghatirli@gmail.com',
                    'first_name': '',
                    'last_name': '',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'phone': None
                })
            if '(30,' in user_line:  # Aslinda
                users_data.append({
                    'id': 30,
                    'username': 'aslinda',
                    'email': 'asli@vamosbodrum.com',
                    'first_name': '',
                    'last_name': '',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'phone': None
                })
            if '(31,' in user_line:  # berk2
                users_data.append({
                    'id': 31,
                    'username': 'berk2',
                    'email': 'bhatirli@gmail.com',
                    'first_name': '',
                    'last_name': '',
                    'is_staff': False,
                    'is_superuser': False,
                    'is_active': True,
                    'phone': None
                })
    
    # Import users to new database
    print("🚀 Starting user import...")
    print(f"📊 Found {len(users_data)} users to import")
    
    imported = 0
    skipped = 0
    
    with transaction.atomic():
        for user_data in users_data:
            try:
                # Check if user already exists
                if User.objects.filter(username=user_data['username']).exists():
                    print(f"⚠️  User {user_data['username']} already exists, skipping...")
                    skipped += 1
                    continue
                
                # Create user
                user = User.objects.create(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data['is_staff'],
                    is_superuser=user_data['is_superuser'],
                    is_active=user_data['is_active']
                )
                
                # Set a default password
                user.set_password('Unicorn2025!')
                user.save()
                
                # Create UserProfile if phone exists
                if user_data.get('phone'):
                    profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={'phone_number': user_data['phone']}
                    )
                    if created:
                        print(f"  📱 Added phone: {user_data['phone']}")
                
                print(f"✅ Imported: {user_data['username']} ({user_data['email']})")
                imported += 1
                
            except Exception as e:
                print(f"❌ Error importing {user_data['username']}: {str(e)}")
    
    print("\n" + "="*50)
    print(f"📊 Import Summary:")
    print(f"  ✅ Successfully imported: {imported} users")
    print(f"  ⚠️  Skipped (already exist): {skipped} users")
    print(f"  📝 Default password for all imported users: Unicorn2025!")
    print("="*50)

if __name__ == "__main__":
    import_users_from_sql()