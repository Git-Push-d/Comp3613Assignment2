from App.database import db
from .observer import Observer 
from .activityentry import ActivityEntry
from datetime import datetime

class ActivityHistoryObserver(Observer):
  __tablename__ = "activity_history_observer"

def updateactivityhistory(self, record):
  #record refers to the student record
  #Create a new activity entry log
  entry = ActivityEntry(
    student_record_id = record.id,
    date =datetime.now(),
    hours = 0,
    logged_by = "system",
    description = f"Student total hours updated to {record.total_hours}"
  )
  db.session.add(entry)
  db.session.commit()