"""
recaria.org mail server provisioning service
manages postfix/dovecot mailboxes via ssh commands
"""

import subprocess
import logging
import hashlib
import secrets
import string
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from django.conf import settings

logger = logging.getLogger('unibos.mail')


@dataclass
class MailConfig:
    """mail server configuration"""
    mail_server: str = 'mail.recaria.org'
    ssh_user: str = 'ubuntu'
    ssh_key_path: str = '/home/ubuntu/.ssh/id_ed25519'
    domain: str = 'recaria.org'
    vmail_path: str = '/var/mail/vhosts'
    vmailbox_file: str = '/etc/postfix/vmailbox'
    dovecot_users_file: str = '/etc/dovecot/users'
    use_ssh: bool = True  # set to false for local testing
    local_mode: bool = False  # set to true when mail server is localhost


def get_mail_config() -> MailConfig:
    """get mail configuration from settings or defaults"""
    mail_server = getattr(settings, 'MAIL_SERVER_HOST', 'mail.recaria.org')

    # detect if mail server is local (same machine)
    local_hosts = ['localhost', '127.0.0.1', 'mail.recaria.org']
    is_local = mail_server in local_hosts

    return MailConfig(
        mail_server=mail_server,
        ssh_user=getattr(settings, 'MAIL_SERVER_SSH_USER', 'ubuntu'),
        ssh_key_path=getattr(settings, 'MAIL_SERVER_SSH_KEY', '/home/ubuntu/.ssh/id_ed25519'),
        domain=getattr(settings, 'MAIL_DOMAIN', 'recaria.org'),
        use_ssh=getattr(settings, 'MAIL_USE_SSH', True),
        local_mode=is_local,
    )


def generate_password(length: int = 16) -> str:
    """generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password_dovecot(password: str) -> str:
    """generate sha512-crypt hash for dovecot"""
    # using passlib if available, fallback to subprocess
    try:
        from passlib.hash import sha512_crypt
        return sha512_crypt.hash(password)
    except ImportError:
        # fallback using doveadm if available
        try:
            result = subprocess.run(
                ['doveadm', 'pw', '-s', 'SHA512-CRYPT', '-p', password],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # last resort: use python hashlib (less secure but functional)
        salt = secrets.token_hex(8)
        return f"$6${salt}${hashlib.sha512((salt + password).encode()).hexdigest()}"


def run_ssh_command(command: str, config: Optional[MailConfig] = None) -> Tuple[bool, str]:
    """run a command on the mail server via ssh or locally"""
    if config is None:
        config = get_mail_config()

    if not config.use_ssh:
        # development mode - just log commands
        logger.info(f"[dev mode] would run: {command}")
        return True, "dev mode - command logged"

    # if mail server is local, run command directly (no SSH needed)
    if config.local_mode:
        try:
            result = subprocess.run(
                ['bash', '-c', command],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                logger.error(f"local command failed: {result.stderr}")
                return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            logger.error("local command timed out")
            return False, "command timed out"
        except Exception as e:
            logger.error(f"local command error: {e}")
            return False, str(e)

    # remote mode - use SSH
    ssh_cmd = [
        'ssh',
        '-i', config.ssh_key_path,
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'BatchMode=yes',
        f'{config.ssh_user}@{config.mail_server}',
        command
    ]

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            logger.error(f"ssh command failed: {result.stderr}")
            return False, result.stderr.strip()

    except subprocess.TimeoutExpired:
        logger.error("ssh command timed out")
        return False, "command timed out"
    except Exception as e:
        logger.error(f"ssh command error: {e}")
        return False, str(e)


class MailProvisioner:
    """handles mail server provisioning operations"""

    def __init__(self, config: Optional[MailConfig] = None):
        self.config = config or get_mail_config()

    def create_mailbox(
        self,
        email: str,
        password: Optional[str] = None,
        quota_mb: int = 1024
    ) -> Tuple[bool, str, Optional[str]]:
        """
        create a new mailbox on the mail server
        returns (success, message, password)
        """
        if not email.endswith(f'@{self.config.domain}'):
            return False, f"email must end with @{self.config.domain}", None

        username = email.split('@')[0]

        # generate password if not provided
        if not password:
            password = generate_password()

        password_hash = hash_password_dovecot(password)

        # step 1: add to vmailbox (postfix)
        vmailbox_entry = f"{email} {self.config.domain}/{username}/"
        cmd_vmailbox = f"echo '{vmailbox_entry}' | sudo tee -a {self.config.vmailbox_file}"

        success, msg = run_ssh_command(cmd_vmailbox, self.config)
        if not success:
            return False, f"failed to add vmailbox entry: {msg}", None

        # step 2: add to dovecot users file
        # format: email:password_hash:uid:gid::home:
        dovecot_entry = f"{email}:{password_hash}:5000:5000::{self.config.vmail_path}/{self.config.domain}/{username}:"
        cmd_dovecot = f"echo '{dovecot_entry}' | sudo tee -a {self.config.dovecot_users_file}"

        success, msg = run_ssh_command(cmd_dovecot, self.config)
        if not success:
            return False, f"failed to add dovecot user: {msg}", None

        # step 3: create maildir structure
        maildir = f"{self.config.vmail_path}/{self.config.domain}/{username}"
        cmd_maildir = f"sudo mkdir -p {maildir}/{{cur,new,tmp}} && sudo chown -R vmail:vmail {maildir}"

        success, msg = run_ssh_command(cmd_maildir, self.config)
        if not success:
            return False, f"failed to create maildir: {msg}", None

        # step 4: set quota
        quota_bytes = quota_mb * 1024 * 1024
        cmd_quota = f"sudo setquota -u vmail {quota_bytes} {quota_bytes} 0 0 /var/mail 2>/dev/null || true"
        run_ssh_command(cmd_quota, self.config)  # quota is optional

        # step 5: reload postfix
        cmd_reload = "sudo postmap /etc/postfix/vmailbox && sudo systemctl reload postfix"
        success, msg = run_ssh_command(cmd_reload, self.config)
        if not success:
            logger.warning(f"postfix reload warning: {msg}")

        logger.info(f"mailbox created successfully: {email}")
        return True, f"mailbox {email} created successfully", password

    def delete_mailbox(self, email: str, delete_data: bool = False) -> Tuple[bool, str]:
        """delete a mailbox from the mail server"""
        if not email.endswith(f'@{self.config.domain}'):
            return False, f"email must end with @{self.config.domain}"

        username = email.split('@')[0]

        # remove from vmailbox
        cmd_vmailbox = f"sudo sed -i '/{email}/d' {self.config.vmailbox_file}"
        success, msg = run_ssh_command(cmd_vmailbox, self.config)
        if not success:
            return False, f"failed to remove vmailbox entry: {msg}"

        # remove from dovecot users
        cmd_dovecot = f"sudo sed -i '/^{email}:/d' {self.config.dovecot_users_file}"
        success, msg = run_ssh_command(cmd_dovecot, self.config)
        if not success:
            return False, f"failed to remove dovecot user: {msg}"

        # optionally delete mail data
        if delete_data:
            maildir = f"{self.config.vmail_path}/{self.config.domain}/{username}"
            cmd_delete = f"sudo rm -rf {maildir}"
            run_ssh_command(cmd_delete, self.config)

        # reload postfix
        cmd_reload = "sudo postmap /etc/postfix/vmailbox && sudo systemctl reload postfix"
        run_ssh_command(cmd_reload, self.config)

        logger.info(f"mailbox deleted: {email}")
        return True, f"mailbox {email} deleted"

    def change_password(self, email: str, new_password: str) -> Tuple[bool, str]:
        """change password for an existing mailbox"""
        if not email.endswith(f'@{self.config.domain}'):
            return False, f"email must end with @{self.config.domain}"

        password_hash = hash_password_dovecot(new_password)

        # update dovecot users file - replace the password hash
        # format is email:hash:uid:gid::home:
        cmd = f"sudo sed -i 's|^{email}:[^:]*:|{email}:{password_hash}:|' {self.config.dovecot_users_file}"

        success, msg = run_ssh_command(cmd, self.config)
        if not success:
            return False, f"failed to update password: {msg}"

        logger.info(f"password changed for: {email}")
        return True, "password updated successfully"

    def set_forwarding(
        self,
        email: str,
        forward_to: str,
        keep_copy: bool = True
    ) -> Tuple[bool, str]:
        """set up email forwarding"""
        if not email.endswith(f'@{self.config.domain}'):
            return False, f"email must end with @{self.config.domain}"

        virtual_file = '/etc/postfix/virtual'

        # remove existing forward if any
        cmd_remove = f"sudo sed -i '/^{email}/d' {virtual_file}"
        run_ssh_command(cmd_remove, self.config)

        if forward_to:
            # add new forwarding rule
            if keep_copy:
                # forward and keep local copy
                forward_rule = f"{email} {email},{forward_to}"
            else:
                # forward only
                forward_rule = f"{email} {forward_to}"

            cmd_add = f"echo '{forward_rule}' | sudo tee -a {virtual_file}"
            success, msg = run_ssh_command(cmd_add, self.config)
            if not success:
                return False, f"failed to set forwarding: {msg}"

            # rebuild virtual map
            cmd_postmap = "sudo postmap /etc/postfix/virtual && sudo systemctl reload postfix"
            run_ssh_command(cmd_postmap, self.config)

        logger.info(f"forwarding set for {email} -> {forward_to}")
        return True, f"forwarding {'enabled' if forward_to else 'disabled'}"

    def set_auto_responder(
        self,
        email: str,
        enabled: bool,
        message: str = ""
    ) -> Tuple[bool, str]:
        """configure vacation/auto-responder"""
        if not email.endswith(f'@{self.config.domain}'):
            return False, f"email must end with @{self.config.domain}"

        username = email.split('@')[0]
        vacation_dir = f"/var/spool/vacation/{username}"

        if enabled and message:
            # create vacation message
            cmd_mkdir = f"sudo mkdir -p {vacation_dir}"
            run_ssh_command(cmd_mkdir, self.config)

            # escape message for shell
            escaped_message = message.replace("'", "'\\''")
            cmd_msg = f"echo '{escaped_message}' | sudo tee {vacation_dir}/.vacation.msg"
            success, msg = run_ssh_command(cmd_msg, self.config)
            if not success:
                return False, f"failed to create vacation message: {msg}"

            # enable vacation
            cmd_enable = f"sudo touch {vacation_dir}/.vacation.db && sudo chown -R vmail:vmail {vacation_dir}"
            run_ssh_command(cmd_enable, self.config)

            logger.info(f"auto-responder enabled for: {email}")
            return True, "auto-responder enabled"
        else:
            # disable vacation
            cmd_disable = f"sudo rm -f {vacation_dir}/.vacation.db"
            run_ssh_command(cmd_disable, self.config)

            logger.info(f"auto-responder disabled for: {email}")
            return True, "auto-responder disabled"

    def get_mailbox_usage(self, email: str) -> Tuple[bool, Dict[str, Any]]:
        """get mailbox storage usage"""
        if not email.endswith(f'@{self.config.domain}'):
            return False, {"error": f"email must end with @{self.config.domain}"}

        username = email.split('@')[0]
        maildir = f"{self.config.vmail_path}/{self.config.domain}/{username}"

        # get directory size
        cmd = f"sudo du -sb {maildir} 2>/dev/null | cut -f1"
        success, output = run_ssh_command(cmd, self.config)

        if success and output.isdigit():
            size_bytes = int(output)
            size_mb = size_bytes / (1024 * 1024)

            # count messages
            cmd_count = f"find {maildir} -type f 2>/dev/null | wc -l"
            _, count_output = run_ssh_command(cmd_count, self.config)
            message_count = int(count_output) if count_output.isdigit() else 0

            return True, {
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 2),
                "message_count": message_count
            }

        return False, {"error": "could not get mailbox usage"}

    def suspend_mailbox(self, email: str, suspend: bool = True) -> Tuple[bool, str]:
        """suspend or unsuspend a mailbox"""
        if not email.endswith(f'@{self.config.domain}'):
            return False, f"email must end with @{self.config.domain}"

        username = email.split('@')[0]
        maildir = f"{self.config.vmail_path}/{self.config.domain}/{username}"

        if suspend:
            # move mail to suspended state (rename directory)
            cmd = f"sudo mv {maildir} {maildir}.suspended 2>/dev/null || true"
        else:
            # restore from suspended state
            cmd = f"sudo mv {maildir}.suspended {maildir} 2>/dev/null || true"

        success, msg = run_ssh_command(cmd, self.config)

        action = "suspended" if suspend else "activated"
        logger.info(f"mailbox {action}: {email}")
        return True, f"mailbox {action}"

    def test_connection(self) -> Tuple[bool, str]:
        """test ssh connection to mail server"""
        success, output = run_ssh_command("echo 'connection ok'", self.config)
        return success, output

    def get_server_status(self) -> Dict[str, Any]:
        """get mail server status information"""
        status = {
            "postfix": False,
            "dovecot": False,
            "opendkim": False,
            "connection": False,
            "mailbox_count": 0,
            "disk_usage": "unknown"
        }

        # test connection
        success, _ = self.test_connection()
        status["connection"] = success

        if not success:
            return status

        # check postfix
        success, _ = run_ssh_command("systemctl is-active postfix", self.config)
        status["postfix"] = success

        # check dovecot
        success, _ = run_ssh_command("systemctl is-active dovecot", self.config)
        status["dovecot"] = success

        # check opendkim
        success, _ = run_ssh_command("systemctl is-active opendkim", self.config)
        status["opendkim"] = success

        # count mailboxes
        success, output = run_ssh_command(
            f"wc -l < {self.config.dovecot_users_file} 2>/dev/null || echo 0",
            self.config
        )
        if success and output.isdigit():
            status["mailbox_count"] = int(output)

        # get disk usage
        success, output = run_ssh_command(
            f"df -h {self.config.vmail_path} | tail -1 | awk '{{print $5}}'",
            self.config
        )
        if success:
            status["disk_usage"] = output

        return status


# convenience functions
def create_mailbox(email: str, password: Optional[str] = None, quota_mb: int = 1024):
    """convenience function to create a mailbox"""
    provisioner = MailProvisioner()
    return provisioner.create_mailbox(email, password, quota_mb)


def delete_mailbox(email: str, delete_data: bool = False):
    """convenience function to delete a mailbox"""
    provisioner = MailProvisioner()
    return provisioner.delete_mailbox(email, delete_data)


def change_password(email: str, new_password: str):
    """convenience function to change password"""
    provisioner = MailProvisioner()
    return provisioner.change_password(email, new_password)


def get_server_status():
    """convenience function to get server status"""
    provisioner = MailProvisioner()
    return provisioner.get_server_status()
