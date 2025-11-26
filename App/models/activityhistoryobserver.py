from App.database import db
from .observer import Observer 
from .activityentry import ActivityEntry
from datetime import datetime

class ActivityHistoryObserver(Observer):
    """Observer that maintains activity history log"""

    def update(self, record):
        """
        Called when StudentRecord is updated
        Activity entries are already added by StudentRecord.add_hours()
        This observer could be used for additional logging if needed
        """
        # Activity entries are created directly in StudentRecord.add_hours()
        # This observer is here for extensibility
        pass
