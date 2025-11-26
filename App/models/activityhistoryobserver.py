from App.database import db
from .observer import Observer 
from .activityentry import ActivityEntry
from datetime import datetime

class ActivityHistoryObserver(Observer):

def updateactivityhistory(self, record):
  #record refers to the student record
  #Create a new activity entry log
  entry = ActivityEntry(
    student_record_id = record.id,
    date =datetime.now()
  )
  db.session.add(entry)
  #db.session.commit()