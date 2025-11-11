"""
Instance Identity Management
Each UNIBOS instance has a unique UUID
"""
import uuid
from django.conf import settings

class InstanceIdentity:
    """Unique identity for this UNIBOS instance"""

    def __init__(self):
        self.uuid = self._get_or_create_uuid()
        self.instance_type = getattr(settings, 'INSTANCE_TYPE', 'personal')

    def _get_or_create_uuid(self):
        # TODO: Load from database or create new
        return uuid.uuid4()
