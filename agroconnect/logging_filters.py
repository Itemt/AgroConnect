"""
Custom logging filters for AgroConnect
"""
import logging


class ExcludeNotificationsFilter(logging.Filter):
    """
    Filter to exclude notification polling requests from logs
    """
    
    def filter(self, record):
        # Check if this is a request log record
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            # Exclude notification polling requests
            if '/core/notifications/list/' in message:
                return False
        return True
