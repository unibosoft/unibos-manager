"""
Custom password validators for enhanced security
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """Custom password validator with advanced rules"""
    
    def validate(self, password, user=None):
        # Check for minimum length (handled by MinimumLengthValidator)
        
        # Must contain at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        
        # Must contain at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        
        # Must contain at least one digit
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Password must contain at least one digit."),
                code='password_no_digit',
            )
        
        # Must contain at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."),
                code='password_no_special',
            )
        
        # Check for common patterns
        common_patterns = [
            r'12345',
            r'qwerty',
            r'asdfg',
            r'password',
            r'admin',
            r'letmein',
            r'welcome',
            r'monkey',
            r'dragon',
        ]
        
        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                raise ValidationError(
                    _("Password contains a common pattern that is too easy to guess."),
                    code='password_common_pattern',
                )
        
        # Check for repeated characters
        if re.search(r'(.)\1{2,}', password):
            raise ValidationError(
                _("Password contains too many repeated characters."),
                code='password_repeated_chars',
            )
        
        # Check for sequential characters
        for i in range(len(password) - 2):
            if ord(password[i]) + 1 == ord(password[i + 1]) == ord(password[i + 2]) - 1:
                raise ValidationError(
                    _("Password contains sequential characters."),
                    code='password_sequential',
                )
        
        # User-specific checks
        if user:
            user_attributes = [
                user.username,
                user.email.split('@')[0],
                user.first_name,
                user.last_name,
            ]
            
            for attr in user_attributes:
                if attr and len(attr) > 2 and attr.lower() in password_lower:
                    raise ValidationError(
                        _("Password is too similar to your personal information."),
                        code='password_too_similar',
                    )
    
    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character. "
            "It cannot contain common patterns or be similar to your personal information."
        )