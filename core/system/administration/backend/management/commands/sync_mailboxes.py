"""
sync mailboxes between database and mail server
manages provisioning and status updates
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.system.administration.backend.models import RecariaMailbox
from core.system.administration.backend.mail_service import MailProvisioner


class Command(BaseCommand):
    help = 'sync recaria.org mailboxes with mail server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provision',
            action='store_true',
            help='provision pending mailboxes on server'
        )
        parser.add_argument(
            '--update-stats',
            action='store_true',
            help='update mailbox usage statistics'
        )
        parser.add_argument(
            '--check-server',
            action='store_true',
            help='check mail server status'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='process specific email address'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='show what would be done without making changes'
        )

    def handle(self, *args, **options):
        provisioner = MailProvisioner()
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('dry run mode - no changes will be made'))

        if options['check_server']:
            self.check_server_status(provisioner)

        if options['provision']:
            self.provision_pending(provisioner, options['email'], dry_run)

        if options['update_stats']:
            self.update_statistics(provisioner, options['email'], dry_run)

        if not any([options['provision'], options['update_stats'], options['check_server']]):
            self.stdout.write('usage: sync_mailboxes --provision | --update-stats | --check-server')
            self.stdout.write('  --provision     create mailboxes on server that are not yet created')
            self.stdout.write('  --update-stats  update storage usage from server')
            self.stdout.write('  --check-server  check mail server status')
            self.stdout.write('  --email EMAIL   process only specified email')
            self.stdout.write('  --dry-run       show what would be done')

    def check_server_status(self, provisioner):
        """check and display mail server status"""
        self.stdout.write('\n=== mail server status ===')

        status = provisioner.get_server_status()

        self.stdout.write(f"connection: {'OK' if status['connection'] else 'FAILED'}")
        self.stdout.write(f"postfix: {'running' if status['postfix'] else 'stopped'}")
        self.stdout.write(f"dovecot: {'running' if status['dovecot'] else 'stopped'}")
        self.stdout.write(f"opendkim: {'running' if status['opendkim'] else 'stopped'}")
        self.stdout.write(f"mailbox count: {status['mailbox_count']}")
        self.stdout.write(f"disk usage: {status['disk_usage']}")

        if status['connection'] and status['postfix'] and status['dovecot']:
            self.stdout.write(self.style.SUCCESS('\nmail server is healthy'))
        else:
            self.stdout.write(self.style.ERROR('\nmail server has issues'))

    def provision_pending(self, provisioner, email_filter, dry_run):
        """provision mailboxes that are not yet created on server"""
        self.stdout.write('\n=== provisioning pending mailboxes ===')

        # get mailboxes not yet created
        mailboxes = RecariaMailbox.objects.filter(mailbox_created=False)

        if email_filter:
            mailboxes = mailboxes.filter(email_address=email_filter)

        if not mailboxes.exists():
            self.stdout.write('no pending mailboxes to provision')
            return

        for mailbox in mailboxes:
            self.stdout.write(f'\nprocessing: {mailbox.email_address}')

            if dry_run:
                self.stdout.write(f'  would create mailbox for {mailbox.user.username}')
                continue

            success, message, password = provisioner.create_mailbox(
                email=mailbox.email_address,
                quota_mb=mailbox.mailbox_size_mb
            )

            if success:
                mailbox.mailbox_created = True
                mailbox.password_set = True
                mailbox.save()

                self.stdout.write(self.style.SUCCESS(f'  created: {message}'))
                self.stdout.write(f'  temporary password: {password}')
                self.stdout.write(self.style.WARNING('  user should change password after first login'))
            else:
                self.stdout.write(self.style.ERROR(f'  failed: {message}'))

    def update_statistics(self, provisioner, email_filter, dry_run):
        """update mailbox usage statistics from server"""
        self.stdout.write('\n=== updating mailbox statistics ===')

        mailboxes = RecariaMailbox.objects.filter(mailbox_created=True, is_active=True)

        if email_filter:
            mailboxes = mailboxes.filter(email_address=email_filter)

        if not mailboxes.exists():
            self.stdout.write('no active mailboxes to update')
            return

        for mailbox in mailboxes:
            self.stdout.write(f'\nchecking: {mailbox.email_address}')

            if dry_run:
                self.stdout.write(f'  would fetch usage stats')
                continue

            success, stats = provisioner.get_mailbox_usage(mailbox.email_address)

            if success:
                mailbox.current_usage_mb = stats['size_mb']
                mailbox.messages_received = stats.get('message_count', mailbox.messages_received)
                mailbox.save()

                usage_pct = mailbox.usage_percentage
                self.stdout.write(f'  size: {stats["size_mb"]}mb ({usage_pct:.1f}% of {mailbox.mailbox_size_mb}mb)')
                self.stdout.write(f'  messages: {stats["message_count"]}')

                if usage_pct > 90:
                    self.stdout.write(self.style.WARNING(f'  WARNING: mailbox is over 90% full'))
            else:
                self.stdout.write(self.style.ERROR(f'  failed to get stats: {stats.get("error", "unknown")}'))
