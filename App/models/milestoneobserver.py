from App.database import db
from .observer import Observer 
from .activityentry import ActivityEntry
from datetime import datetime


class MilestoneObserver(Observer):
  
  def __init__(self):
    self.milestones = {
      10: "Bronze",
      25: "Silver",
      50: "Gold"
    }

  def checkMilestone(self, total_hours):
     return self.milestones.get(total_hours)
  
  def updateMilestonse(self, record):
    milestone = self.checkMilestone(record.total_hours)
    if milestone is None:
      return
    if milestone not in record.accolades:
       record.accolades.append(milestone)
      
      entry = ActivityEntry(
        student_record_id = record.id,
        date=datetime.now(),
        hours = 0,
        logged_by = "System",
        description = f"Milestone achieved: {milestone}"
      )
      db.session.add(record)
      db.session.add(entry)
      db.session.commit()

