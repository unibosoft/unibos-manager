#!/usr/bin/env python3
"""
Import users from old Unicorn MySQL backup to new UNIBOS PostgreSQL database
"""

import re
import sys
import os

# Add backend to path (updated for monorepo structure)
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/apps/web/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')

import django
django.setup()

from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

# SQL data from unicorn backup
user_data_sql = """INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$870000$091PoIF9MzHdB9ZOh1cRph$IUBfsslh8K7oYpQXTqmv+wnlDORWvyDNqzEKAB+VKZw=','2025-05-22 15:28:02.679808',1,'berkhatirli','Berk','Hatırlı','berk@berkinatolyesi.com',1,1,'2024-10-09 15:59:59.341955'),(4,'pbkdf2_sha256$870000$zd8M3zOY8VNSj5wlZzvtaM$QJH1htiP21B+2TUxZNLHLbqklZuM2egNEm4lDPGnA3s=','2024-10-27 16:52:57.644951',0,'beyhan','','','beyhangndz@gmail.com',0,1,'2024-10-11 11:47:20.595756'),(5,'pbkdf2_sha256$870000$2XPO0jHRVY8nOEK9AofPKt$RFE/6UElRYk/Xzrq7jNvB3uYLpJhS60fXhR0jMt0P2U=','2024-10-18 20:16:45.102813',0,'ersan','','','ersankolay@gmail.com',0,1,'2024-10-12 19:57:00.055700'),(6,'pbkdf2_sha256$870000$H8pVA9F5rFGOXa01Kjr608$KceCF7pj/tEpGbuqLy/ofHFploXzjOlvXmj3t0tT5Tw=','2024-12-16 19:56:00.191357',0,'Leventhatirli','','','leventhatirli@gmail.com',0,1,'2024-10-19 20:52:08.212660'),(27,'pbkdf2_sha256$870000$jFZ8ofsTPpso8yd3gXbA8r$9ohNnXwH53BNhSdSaS8eS1H8uyMSR+Q05rAiWS53exQ=','2024-12-16 17:35:52.423195',0,'Armutdaldaasilsin','','','muratcanb@hotmail.co.uk',0,1,'2024-12-14 20:28:54.577691'),(28,'pbkdf2_sha256$870000$JZuDLs2psUnfPy3KAiWVfT$KPRj52x3lVqE9uAjqyTB3BIz+HKSCoL33Vr7mxWqMUg=','2025-05-22 15:31:50.770200',0,'gulcinhatirli','','','ghatirli@gmail.com',0,1,'2024-12-15 09:59:48.000000'),(29,'pbkdf2_sha256$870000$ndRgKnyz8dwZcR28U54BMZ$4SO3qGqm/yHcAbmYPuiBbKlEsED3TdMYxOs/7pCStAg=',NULL,0,'euccan@hotmail.com','','','euccan@hotmail.com',0,1,'2024-12-15 19:20:18.802830'),(30,'pbkdf2_sha256$870000$DReNaEIrqGtaSwh9mnYFAT$QN5hBo0MsGhdJVvu2mpUcEvmja3VHV9w7yXKigtTiow=','2024-12-17 07:43:21.913175',0,'Aslinda','','','asli@vamosbodrum.com',0,1,'2024-12-17 07:40:56.346319'),(31,'pbkdf2_sha256$870000$GVMEFL21Lp5GqPqORgpizx$Sgz68nIvXFRnyB0oRMtUmxMn3tvw1gvpnNwNO1Ljh/o=','2024-12-24 06:53:43.767643',0,'berk2','','','bhatirli@gmail.com',0,1,'2024-12-24 06:48:02.793003'),(154,'pbkdf2_sha256$870000$9zmyJ4yYd0JuiiQ6U2JhH0$4eTmJUbz1OTlezJ9jhLB/z9zZ5is9s/ZtMRVG/nWCQg=',NULL,0,'MyName','','','kwbireley@gmail.com',0,1,'2025-05-19 09:16:05.227932'),(155,'pbkdf2_sha256$870000$BdzpHhDhZugZm9oqlficBs$YOok9N3IARiIvpekZjw2o8Cjl3cFXLrMOVAsyWTQpOY=',NULL,0,'John','','','cyndy22222@aol.com',0,1,'2025-05-19 10:39:37.238648'),(156,'pbkdf2_sha256$870000$13tat9gN816VRaWIQquiot$DtazaOavTVNQ3AKXno7jJX9fAf+upaJKXertecdviZs=',NULL,0,'Alice','','','scollofelice@gmail.com',0,1,'2025-05-19 11:29:43.887505'),(157,'pbkdf2_sha256$870000$2GDetgf350ocJIRde83BUP$7D4i14s4HqTCw3C3OBkp+KQtHnpN18Pu3u+dUI3gSpw=',NULL,0,'Hello','','','nprcsc@gmail.com',0,1,'2025-05-19 12:45:49.864399'),(158,'pbkdf2_sha256$870000$ATaqqkGWWmpDDYCxNLFLi6$UXxRSLo2rkZMFHBEvvCF4Mej4Pkt2YsQyKkO7FwIwxo=',NULL,0,'TestUser','','','gayeglass@gmail.com',0,1,'2025-05-19 13:14:26.297426');"""

def parse_datetime(dt_str):
    """Parse datetime string or return None"""
    if dt_str == 'NULL' or not dt_str:
        return None
    # Remove quotes if present
    dt_str = dt_str.strip("'\"")
    # Parse the datetime
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
    except:
        try:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

def import_users():
    """Import users from SQL data"""
    
    # Parse the SQL INSERT statement
    # Remove the INSERT INTO part and get just the values
    values_str = user_data_sql.replace("INSERT INTO `auth_user` VALUES ", "")
    
    # Split by ),( to get individual user records
    user_records = re.split(r'\),\(', values_str)
    
    imported = 0
    skipped = 0
    errors = 0
    
    for record in user_records:
        # Clean up the record
        record = record.strip('();')
        
        # Parse the values using regex to handle quotes properly
        # Pattern to match values including those with commas inside quotes
        pattern = r"(?:^|,)(?:'([^']*)'|([^,]*))"
        matches = re.findall(pattern, record)
        
        # Extract values
        values = []
        for match in matches:
            if match[0]:  # Quoted value
                values.append(match[0])
            else:  # Unquoted value
                val = match[1].strip()
                if val == 'NULL':
                    values.append(None)
                elif val in ['0', '1']:
                    values.append(int(val))
                else:
                    values.append(val)
        
        if len(values) < 10:
            print(f"Skipping incomplete record: {record[:50]}...")
            errors += 1
            continue
        
        # Map values to user fields
        old_id = int(values[0]) if values[0] else None
        password_hash = values[1]
        last_login = parse_datetime(values[2])
        is_superuser = bool(int(values[3])) if values[3] else False
        username = values[4]
        first_name = values[5] or ''
        last_name = values[6] or ''
        email = values[7]
        is_staff = bool(int(values[8])) if values[8] else False
        is_active = bool(int(values[9])) if values[9] else True
        date_joined = parse_datetime(values[10]) if len(values) > 10 else None
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists, skipping...")
            skipped += 1
            continue
        
        if User.objects.filter(email=email).exists():
            print(f"Email '{email}' already exists, skipping...")
            skipped += 1
            continue
        
        try:
            # Create the user
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_superuser=is_superuser,
                is_staff=is_staff,
                is_active=is_active,
                password=password_hash,  # Already hashed
                last_login=last_login,
            )
            
            if date_joined:
                user.date_joined = date_joined
            
            user.save()
            
            print(f"✓ Imported user: {username} ({email})")
            imported += 1
            
        except Exception as e:
            print(f"✗ Error importing user {username}: {e}")
            errors += 1
    
    print("\n" + "="*60)
    print(f"Import Summary:")
    print(f"  - Successfully imported: {imported} users")
    print(f"  - Skipped (already exists): {skipped} users")
    print(f"  - Errors: {errors}")
    print("="*60)
    
    # List all users in database
    print("\nAll users in database now:")
    print("-"*60)
    for user in User.objects.all().order_by('date_joined'):
        print(f"  {user.username:20} - {user.email:30} - Admin: {user.is_superuser}")

if __name__ == "__main__":
    print("Starting import of Unicorn users to UNIBOS database...")
    print("="*60)
    import_users()