"""
Import users from Unicorn backup SQL file
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()
import re


class Command(BaseCommand):
    help = 'Import users from Unicorn SQL backup'
    
    def handle(self, *args, **options):
        sql_file = '/Users/berkhatirli/Desktop/unibos/archive/external_backups/unicorn_backup_2025_08_07/unicorn_db_backup_v030-beta_2025_05_22_19_50.sql'
        
        self.stdout.write('Reading SQL file...')
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract user data
        user_pattern = r"INSERT INTO `auth_user` VALUES \((.*?)\);"
        user_match = re.search(user_pattern, content, re.DOTALL)
        
        if not user_match:
            self.stdout.write(self.style.ERROR('No user data found'))
            return
        
        # Parse user data
        users_data = user_match.group(1)
        
        # Split by ),( to get individual user records
        user_records = users_data.split('),(')
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for record in user_records:
                # Clean up the record
                record = record.strip('()')
                
                # Parse fields (be careful with quotes)
                parts = []
                current = ''
                in_quotes = False
                escape_next = False
                
                for char in record:
                    if escape_next:
                        current += char
                        escape_next = False
                    elif char == '\\':
                        escape_next = True
                        current += char
                    elif char == "'" and not escape_next:
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        parts.append(current.strip("'"))
                        current = ''
                    else:
                        current += char
                
                if current:
                    parts.append(current.strip("'"))
                
                if len(parts) < 11:
                    continue
                
                # Parse user fields
                user_id = int(parts[0])
                password = parts[1]
                last_login = parts[2] if parts[2] != 'NULL' else None
                is_superuser = parts[3] == '1'
                username = parts[4]
                first_name = parts[5]
                last_name = parts[6]
                email = parts[7]
                is_staff = parts[8] == '1'
                is_active = parts[9] == '1'
                date_joined = parts[10]
                
                # Create or update user
                user, created = User.objects.update_or_create(
                    username=username,
                    defaults={
                        'password': password,  # Already hashed
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_staff': is_staff,
                        'is_active': is_active,
                        'is_superuser': is_superuser,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created user: {username}')
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated user: {username}')
        
        # Now import UserProfile data
        profile_pattern = r"INSERT INTO `user_userprofile` VALUES \((.*?)\);"
        profile_match = re.search(profile_pattern, content, re.DOTALL)
        
        if profile_match:
            from modules.core.backend.models import UserProfile
            
            profiles_data = profile_match.group(1)
            profile_records = profiles_data.split('),(')
            
            for record in profile_records:
                record = record.strip('()')
                parts = record.split(',')
                
                if len(parts) < 7:
                    continue
                
                profile_id = int(parts[0])
                phone_number = parts[1].strip("'") if parts[1] != 'NULL' else None
                user_id = int(parts[2])
                mail_verified = parts[3] == '1'
                phone_verified = parts[4] == '1'
                preferred_language = parts[5].strip("'")
                
                # Find the user by their original ID mapping
                try:
                    # Map old user_id to username first
                    username_for_id = None
                    for u_record in user_records:
                        u_parts = []
                        current = ''
                        in_quotes = False
                        
                        for char in u_record.strip('()'):
                            if char == "'" and not escape_next:
                                in_quotes = not in_quotes
                            elif char == ',' and not in_quotes:
                                u_parts.append(current.strip("'"))
                                current = ''
                            else:
                                current += char
                        if current:
                            u_parts.append(current.strip("'"))
                        
                        if len(u_parts) > 4 and int(u_parts[0]) == user_id:
                            username_for_id = u_parts[4]
                            break
                    
                    if username_for_id:
                        user = User.objects.get(username=username_for_id)
                        
                        UserProfile.objects.update_or_create(
                            user=user,
                            defaults={
                                'phone_number': phone_number,
                                'mail_verified': mail_verified,
                                'phone_verified': phone_verified,
                                'preferred_language': preferred_language,
                            }
                        )
                        self.stdout.write(f'Created/updated profile for: {user.username}')
                except User.DoesNotExist:
                    self.stdout.write(f'User not found for profile with original ID: {user_id}')
                except Exception as e:
                    self.stdout.write(f'Error creating profile: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nImport complete!\n'
                f'Created: {created_count} users\n'
                f'Updated: {updated_count} users'
            )
        )