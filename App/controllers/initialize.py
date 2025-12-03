from App.models import Student, Staff, Request
from App.database import db


def initialize_db(drop_first=True):
    """Initialize the database and seed sample data.

    Args:
        drop_first (bool): if True, drop all tables before creating them.

    Returns a dict with lists of created record IDs.
    """
    if drop_first:
        db.drop_all()
    db.create_all()

    # Sample students (username, email, password)
    students_data = [
        ("alice", "alice.smith@gmail.com", "password1"),
        ("bob", "bob.jones@hotmail.com", "password2"),
        ("charlie", "charlie.brown@gmail.com", "password3"),
        ("diana", "diana.lee@hotmail.com", "password4"),
        ("eve", "eve.patel@gmail.com", "password5"),
    ]

    # Sample staff (username, email, password)
    staff_data = [
        ("msmith", "mr.smith@gmail.com", "staffpass1"),
        ("mjohnson", "ms.johnson@hotmail.com", "staffpass2"),
        ("mlee", "mr.lee@gmail.com", "staffpass3"),
    ]

    students = []
    for username, email, pwd in students_data:
        s = Student(username=username, email=email, password=pwd)
        students.append(s)
        db.session.add(s)

    staff_members = []
    for username, email, pwd in staff_data:
        st = Staff(username=username, email=email, password=pwd, department="Student Affairs")
        staff_members.append(st)
        db.session.add(st)

    db.session.commit()

    # Create StudentRecord for each student (students now have IDs from commit)
    from App.models.studentrecord import StudentRecord
    for student in students:
        record = StudentRecord(student_id=student.student_id)
        db.session.add(record)

    db.session.commit()

    # Create 4 requests for first 4 students
    import random
    requests = []
    for i in range(4):
        student = students[i]
        hours = random.choice([5, 10, 12.5, 8])
        req = Request(student_id=student.user_id, hours=hours, status='pending')
        requests.append(req)
        db.session.add(req)

    db.session.commit()

    # Add logged hours
    from App.models import LoggedHours

    # Approve first two requests and create logged entries using Observer pattern
    for i, req in enumerate(requests[:2]):
        req.status = 'approved'
        staff_member = staff_members[i % len(staff_members)]
        log = LoggedHours(student_id=req.student_id, staff_id=staff_member.user_id, hours=req.hours, status='approved')
        db.session.add(log)

        # Trigger Observer pattern
        student_record = StudentRecord.query.filter_by(student_id=req.student_id).first()
        if student_record:
            student_record.add_hours(
                hours=req.hours,
                description=f"Request approved: {req.hours} hours",
                logged_by=staff_member.username
            )

    # Deny the third request (if present)
    if len(requests) >= 3:
        requests[2].status = 'denied'

    # Leave the fourth request pending

    # Add 3 extra logged hours entries using Observer pattern
    extra_logs = [
        (students[0].user_id, staff_members[0].user_id, 3.5, 'approved'),
        (students[1].user_id, staff_members[1].user_id, 7.0, 'approved'),
        (students[2].user_id, staff_members[2].user_id, 4.0, 'approved'),
    ]
    for student_id, staff_id, hours, status in extra_logs:
        log = LoggedHours(student_id=student_id, staff_id=staff_id, hours=hours, status=status)
        db.session.add(log)

        # Trigger Observer pattern
        student_record = StudentRecord.query.filter_by(student_id=student_id).first()
        if student_record:
            staff_member = Staff.query.filter_by(staff_id=staff_id).first()
            student_record.add_hours(
                hours=hours,
                description=f"Additional hours logged: {hours} hours",
                logged_by=staff_member.username if staff_member else "Staff"
            )

    db.session.commit()

    # Return ids for reference
    result = {
        'students': [s.user_id for s in students],
        'staff': [st.user_id for st in staff_members],
        'requests': [r.requestID for r in Request.query.order_by(Request.requestID).all()],
        'logged_hours': [l.id for l in LoggedHours.query.order_by(LoggedHours.id).all()]
    }

    return result


def initialize(drop_first=True):
    """Compatibility wrapper used by CLI (keeps previous name `initialize`)."""
    return initialize_db(drop_first=drop_first)

#from App.models import User,Student, Staff, Request
#from App.database import db


# def initialize():


#     db.drop_all()
#     db.create_all()
#     #create_user('bob', 'bobpass')

#     # Add sample students

#     students = [
#         Student(name='Alice', email='alice.smith@gmail.com'),
#         Student(name='Bob', email='bob.jones@hotmail.com'),
#         Student(name='Charlie', email='charlie.brown@gmail.com'),
#         Student(name='Diana', email='diana.lee@hotmail.com'),
#         Student(name='Eve', email='eve.patel@gmail.com'),
#         Student(name='Frank', email='frank.miller@gmail.com'),
#         Student(name='Grace', email='grace.wilson@hotmail.com'),
#     ]
#     db.session.add_all(students)
#     db.session.commit()

#     # Add sample staff members
#     staff_members = [
#         Staff(name='Mr. Smith', email='mr.smith@gmail.com'),
#         Staff(name='Ms. Johnson', email='ms.johnson@hotmail.com'),
#         Staff(name='Mr. Lee', email='mr.lee@gmail.com'),

#     ]
#     for staff_member in staff_members:
#         db.session.add(staff_member)
#     db.session.commit()

#     # Add sample requests for students
#     all_students = Student.query.order_by(Student.id).all()
#     requests = []
#     import random
#     for i, student in enumerate(all_students):
#         hours = random.randint(10, 60)
#         req = Request(student_id=student.id, hours=hours, status='pending')
#         requests.append(req)
#     db.session.add_all(requests)
#     db.session.commit()

#     # Add sample logged hours (approve first 2 requests by first 3 staff)
#     from App.models import LoggedHours
#     all_staff = Staff.query.order_by(Staff.id).all()
#     for i, req in enumerate(requests[:3]):
#         staff_member = all_staff[i % len(all_staff)]
#         if i < 2:
#             req.status = 'approved'
#             log = LoggedHours(student_id=req.student_id, staff_id=staff_member.id, hours=req.hours, status='approved')
#             db.session.add(log)
#         else:
#             req.status = 'denied'
#     db.session.commit()


