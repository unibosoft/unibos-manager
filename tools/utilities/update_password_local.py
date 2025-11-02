#!/usr/bin/env python3
"""
Update berkhatirli user password in local database
"""

import os
import sys
import django

# Add backend to path
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Get berkhatirli user
    user = User.objects.get(username='berkhatirli')
    print(f"✓ Found user: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Active: {user.is_active}")
    print(f"  Superuser: {user.is_superuser}")
    
    # Update password
    old_password = 'unibos123'
    new_password = 'Bodrum2015*'
    
    user.set_password(new_password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    print(f"\n✅ Password updated successfully!")
    print(f"  New password: {new_password}")
    
    # Test authentication
    from django.contrib.auth import authenticate
    test_user = authenticate(username='berkhatirli', password=new_password)
    if test_user:
        print(f"✅ Authentication test successful!")
    else:
        print(f"❌ Authentication test failed!")
        
except User.DoesNotExist:
    print("❌ User 'berkhatirli' not found!")
    print("\nExisting users:")
    for u in User.objects.all()[:5]:
        print(f"  - {u.username} (active: {u.is_active})")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()