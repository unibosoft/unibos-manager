from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from modules.administration.backend.models import Role, Department, SystemSetting

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates default system roles and departments'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating default system roles...')
        
        # Create Super Admin role
        super_admin, created = Role.objects.get_or_create(
            code='super_admin',
            defaults={
                'name': 'Super Administrator',
                'description': 'Full system access with all permissions',
                'is_system': True,
                'priority': 1000,
                'can_manage_users': True,
                'can_manage_roles': True,
                'can_view_logs': True,
                'can_access_admin': True,
                'can_export_data': True,
                'can_import_data': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {super_admin.name}'))
        
        # Create Admin role
        admin, created = Role.objects.get_or_create(
            code='admin',
            defaults={
                'name': 'Administrator',
                'description': 'Administrative access with user management',
                'is_system': True,
                'priority': 900,
                'can_manage_users': True,
                'can_manage_roles': False,
                'can_view_logs': True,
                'can_access_admin': True,
                'can_export_data': True,
                'can_import_data': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {admin.name}'))
        
        # Create Manager role
        manager, created = Role.objects.get_or_create(
            code='manager',
            defaults={
                'name': 'Manager',
                'description': 'Department management and reporting',
                'is_system': True,
                'priority': 800,
                'can_manage_users': False,
                'can_manage_roles': False,
                'can_view_logs': True,
                'can_access_admin': False,
                'can_export_data': True,
                'can_import_data': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {manager.name}'))
        
        # Create Supervisor role
        supervisor, created = Role.objects.get_or_create(
            code='supervisor',
            defaults={
                'name': 'Supervisor',
                'description': 'Team supervision and limited management',
                'is_system': True,
                'priority': 700,
                'can_manage_users': False,
                'can_manage_roles': False,
                'can_view_logs': False,
                'can_access_admin': False,
                'can_export_data': True,
                'can_import_data': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {supervisor.name}'))
        
        # Create User role
        user_role, created = Role.objects.get_or_create(
            code='user',
            defaults={
                'name': 'User',
                'description': 'Standard user with basic permissions',
                'is_system': True,
                'priority': 100,
                'can_manage_users': False,
                'can_manage_roles': False,
                'can_view_logs': False,
                'can_access_admin': False,
                'can_export_data': False,
                'can_import_data': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {user_role.name}'))
        
        # Create Guest role
        guest, created = Role.objects.get_or_create(
            code='guest',
            defaults={
                'name': 'Guest',
                'description': 'Limited read-only access',
                'is_system': True,
                'priority': 10,
                'can_manage_users': False,
                'can_manage_roles': False,
                'can_view_logs': False,
                'can_access_admin': False,
                'can_export_data': False,
                'can_import_data': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {guest.name}'))
        
        # Create Developer role
        developer, created = Role.objects.get_or_create(
            code='developer',
            defaults={
                'name': 'Developer',
                'description': 'Development and debugging access',
                'is_system': True,
                'priority': 850,
                'can_manage_users': False,
                'can_manage_roles': False,
                'can_view_logs': True,
                'can_access_admin': True,
                'can_export_data': True,
                'can_import_data': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {developer.name}'))
        
        # Create Auditor role
        auditor, created = Role.objects.get_or_create(
            code='auditor',
            defaults={
                'name': 'Auditor',
                'description': 'Read-only access to logs and reports',
                'is_system': True,
                'priority': 600,
                'can_manage_users': False,
                'can_manage_roles': False,
                'can_view_logs': True,
                'can_access_admin': False,
                'can_export_data': True,
                'can_import_data': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created role: {auditor.name}'))
        
        # Create default departments
        self.stdout.write('\nCreating default departments...')
        
        # IT Department
        it_dept, created = Department.objects.get_or_create(
            code='IT',
            defaults={
                'name': 'Information Technology',
                'default_role': developer,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created department: {it_dept.name}'))
        
        # HR Department
        hr_dept, created = Department.objects.get_or_create(
            code='HR',
            defaults={
                'name': 'Human Resources',
                'default_role': manager,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created department: {hr_dept.name}'))
        
        # Finance Department
        finance_dept, created = Department.objects.get_or_create(
            code='FIN',
            defaults={
                'name': 'Finance',
                'default_role': manager,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created department: {finance_dept.name}'))
        
        # Operations Department
        ops_dept, created = Department.objects.get_or_create(
            code='OPS',
            defaults={
                'name': 'Operations',
                'default_role': supervisor,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created department: {ops_dept.name}'))
        
        # Create default system settings
        self.stdout.write('\nCreating default system settings...')
        
        settings_to_create = [
            ('max_login_attempts', 5, 'Maximum login attempts before lockout'),
            ('lockout_duration', 30, 'Lockout duration in minutes'),
            ('password_min_length', 8, 'Minimum password length'),
            ('password_require_special', True, 'Require special characters in password'),
            ('session_timeout', 3600, 'Session timeout in seconds'),
            ('enable_2fa', False, 'Enable two-factor authentication'),
            ('audit_log_retention', 90, 'Audit log retention in days'),
            ('allow_self_registration', False, 'Allow users to self-register'),
        ]
        
        for key, value, description in settings_to_create:
            setting, created = SystemSetting.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': description,
                    'is_public': False,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created setting: {key}'))
        
        # Assign super admin role to berkhatirli if exists
        try:
            berk = User.objects.get(username='berkhatirli')
            from modules.administration.backend.models import UserRole
            user_role, created = UserRole.objects.get_or_create(
                user=berk,
                role=super_admin,
                defaults={
                    'assigned_by': berk,
                    'notes': 'System owner - automatic assignment',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Assigned Super Admin role to berkhatirli'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠ User berkhatirli not found'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Default roles and departments created successfully!'))