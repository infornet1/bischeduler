#!/usr/bin/env python3
"""
Populate Attendance Data for BiScheduler Phase 11.1
Generate realistic attendance data for September 2025
"""

import sys
import os
from datetime import datetime, date, timedelta
import random

# Add project to path
sys.path.insert(0, '/var/www/dev/bischeduler')

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.models.tenant import Student, Teacher, DailyAttendance

# Database connection
DATABASE_URL = 'mysql+pymysql://root:g)8nE>?rq-#v3Ta@localhost/ueipab_2025_data'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def get_weekdays_in_september_2025():
    """Get all weekdays (Monday-Friday) in September 2025"""
    weekdays = []
    start_date = date(2025, 9, 1)
    end_date = date(2025, 9, 30)

    current = start_date
    while current <= end_date:
        # 0 = Monday, 4 = Friday
        if current.weekday() < 5:
            weekdays.append(current)
        current += timedelta(days=1)

    return weekdays


def populate_attendance():
    """Populate realistic attendance data"""
    print("=" * 70)
    print("BiScheduler Phase 11.1 - Attendance Data Population")
    print("=" * 70)

    # Get all active students
    students = session.query(Student).filter_by(
        academic_year='2025-2026',
        is_active=True
    ).all()

    print(f"\n📊 Found {len(students)} active students")

    if not students:
        print("❌ No students found in database!")
        return

    # Get a teacher (for recorded_by)
    teacher = session.query(Teacher).filter_by(is_active=True).first()
    if not teacher:
        print("❌ No active teachers found!")
        return

    print(f"👨‍🏫 Using teacher: {teacher.teacher_name}")

    # Get weekdays in September 2025
    weekdays = get_weekdays_in_september_2025()
    print(f"📅 Weekdays in September 2025: {len(weekdays)} days")
    print(f"   Range: {weekdays[0]} to {weekdays[-1]}")

    # Check for existing attendance records
    existing_count = session.query(func.count(DailyAttendance.id)).scalar()
    if existing_count > 0:
        print(f"\n⚠️  Warning: {existing_count} attendance records already exist")
        response = input("   Delete existing records and start fresh? (y/N): ")
        if response.lower() == 'y':
            session.query(DailyAttendance).delete()
            session.commit()
            print("   ✅ Existing records deleted")
        else:
            print("   ⏭️  Keeping existing records, adding new ones")

    # Populate attendance for each student
    total_records = 0

    print(f"\n📝 Generating attendance records...")

    for student in students:
        # Assign random attendance pattern
        # 85% of students: high attendance (90-100%)
        # 10% of students: medium attendance (75-90%)
        # 5% of students: low attendance (60-75%)
        rand = random.random()
        if rand < 0.85:
            attendance_rate = random.uniform(0.90, 1.0)
        elif rand < 0.95:
            attendance_rate = random.uniform(0.75, 0.90)
        else:
            attendance_rate = random.uniform(0.60, 0.75)

        for attendance_date in weekdays:
            # Check if record already exists
            existing = session.query(DailyAttendance).filter(
                DailyAttendance.student_id == student.id,
                func.date(DailyAttendance.date) == attendance_date
            ).first()

            if existing:
                continue  # Skip if already exists

            # Randomly determine if present based on attendance rate
            present = random.random() < attendance_rate

            # If absent, 30% chance it's excused
            excused = False
            if not present:
                excused = random.random() < 0.30

            # If present, 5% chance of late arrival
            late_arrival = False
            if present:
                late_arrival = random.random() < 0.05

            # Create attendance record
            attendance = DailyAttendance(
                student_id=student.id,
                date=datetime.combine(attendance_date, datetime.min.time()),
                present=present,
                excused=excused,
                late_arrival=late_arrival,
                early_departure=False,
                absence_reason='Motivo médico' if (not present and excused) else None,
                recorded_by=teacher.id,
                recorded_at=datetime.combine(attendance_date, datetime(2025, 9, 1, 8, 0).time()),
                academic_year='2025-2026'
            )

            session.add(attendance)
            total_records += 1

        # Commit every 100 students to avoid memory issues
        if total_records % 100 == 0:
            session.commit()
            print(f"   ✓ {total_records} records created...")

    # Final commit
    session.commit()

    print(f"\n✅ Successfully populated {total_records} attendance records!")

    # Calculate statistics
    total_present = session.query(func.count(DailyAttendance.id)).filter(
        DailyAttendance.present == True
    ).scalar()

    total_absent = session.query(func.count(DailyAttendance.id)).filter(
        DailyAttendance.present == False
    ).scalar()

    total_excused = session.query(func.count(DailyAttendance.id)).filter(
        DailyAttendance.excused == True
    ).scalar()

    total_late = session.query(func.count(DailyAttendance.id)).filter(
        DailyAttendance.late_arrival == True
    ).scalar()

    overall_attendance_rate = (total_present / (total_present + total_absent) * 100) if (total_present + total_absent) > 0 else 0

    print(f"\n📊 Attendance Statistics:")
    print(f"   • Total Records:      {total_records}")
    print(f"   • Present:            {total_present}")
    print(f"   • Absent:             {total_absent}")
    print(f"   • Excused Absences:   {total_excused}")
    print(f"   • Late Arrivals:      {total_late}")
    print(f"   • Attendance Rate:    {overall_attendance_rate:.1f}%")

    print(f"\n🎯 Phase 11.1 Attendance System Ready!")
    print(f"   Dashboard: https://dev.ueipab.edu.ve/bischeduler/attendance/")


if __name__ == '__main__':
    try:
        populate_attendance()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()