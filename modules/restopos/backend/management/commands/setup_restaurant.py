"""
Management command to set up initial restaurant and staff records
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from modules.restopos.backend.models import Restaurant, Staff
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a restaurant and assign staff members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--restaurant-name',
            type=str,
            required=True,
            help='Name of the restaurant'
        )
        parser.add_argument(
            '--branch-code',
            type=str,
            required=True,
            help='Unique branch code for the restaurant'
        )
        parser.add_argument(
            '--manager-username',
            type=str,
            required=True,
            help='Username of the manager user'
        )
        parser.add_argument(
            '--city',
            type=str,
            default='New York',
            help='City where restaurant is located'
        )
        parser.add_argument(
            '--country',
            type=str,
            default='USA',
            help='Country where restaurant is located'
        )
        parser.add_argument(
            '--currency',
            type=str,
            default='USD',
            help='Currency code (e.g., USD, EUR)'
        )

    def handle(self, *args, **options):
        restaurant_name = options['restaurant_name']
        branch_code = options['branch_code']
        manager_username = options['manager_username']
        city = options['city']
        country = options['country']
        currency = options['currency']

        # Check if user exists
        try:
            manager_user = User.objects.get(username=manager_username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with username "{manager_username}" does not exist')
            )
            return

        # Check if restaurant with branch code already exists
        if Restaurant.objects.filter(branch_code=branch_code).exists():
            self.stdout.write(
                self.style.ERROR(f'Restaurant with branch code "{branch_code}" already exists')
            )
            return

        # Create restaurant
        restaurant = Restaurant.objects.create(
            name=restaurant_name,
            slug=slugify(f"{restaurant_name}-{branch_code}"),
            branch_code=branch_code,
            address='123 Main Street',  # Default address
            city=city,
            country=country,
            postal_code='10001',
            phone='+1-555-0100',
            email=f'{slugify(restaurant_name)}@example.com',
            currency=currency,
            operating_hours={
                'monday': {'open': '09:00', 'close': '22:00'},
                'tuesday': {'open': '09:00', 'close': '22:00'},
                'wednesday': {'open': '09:00', 'close': '22:00'},
                'thursday': {'open': '09:00', 'close': '22:00'},
                'friday': {'open': '09:00', 'close': '23:00'},
                'saturday': {'open': '10:00', 'close': '23:00'},
                'sunday': {'open': '10:00', 'close': '21:00'},
            }
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created restaurant: {restaurant.name} ({restaurant.branch_code})')
        )

        # Check if staff record already exists
        if Staff.objects.filter(restaurant=restaurant, user=manager_user).exists():
            self.stdout.write(
                self.style.WARNING(f'Staff record already exists for {manager_user.username} at {restaurant.name}')
            )
            return

        # Create staff record for manager
        from datetime import date
        staff = Staff.objects.create(
            restaurant=restaurant,
            user=manager_user,
            employee_id=f'EMP-{branch_code}-001',
            role='manager',
            can_manage_orders=True,
            can_manage_tables=True,
            can_manage_menu=True,
            can_process_payments=True,
            can_view_reports=True,
            is_active=True,
            hired_date=date.today()
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully assigned {manager_user.username} as manager of {restaurant.name}')
        )
        
        # Display summary
        self.stdout.write('\n' + self.style.SUCCESS('Setup Complete!'))
        self.stdout.write(f'Restaurant: {restaurant.name}')
        self.stdout.write(f'Branch Code: {restaurant.branch_code}')
        self.stdout.write(f'Manager: {manager_user.username}')
        self.stdout.write(f'Employee ID: {staff.employee_id}')
        self.stdout.write('\nYou can now access the RestoPOS module with this user.')