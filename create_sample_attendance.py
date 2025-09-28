#!/usr/bin/env python3
"""
Create sample attendance data for testing the Venezuelan attendance system
"""

import os
import sys
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.tenant import Student, DailyAttendance, Section

def create_sample_attendance():
    """Create realistic attendance patterns for testing"""

    # Connect to tenant database
    engine = create_engine('mysql+pymysql://root:Temporal2024!@localhost/ueipab_2025_data')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get all students
        students = session.query(Student).filter_by(
            academic_year='2025-2026', is_active=True
        ).all()

        if not students:
            print("❌ No se encontraron estudiantes")
            return

        print(f"🚀 Creando datos de asistencia para {len(students)} estudiantes...")

        # Create attendance for the last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        attendance_records = 0
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends (Venezuelan schools typically run Monday-Friday)
            if current_date.weekday() < 5:  # 0-4 = Monday-Friday

                for student in students:
                    # Create realistic attendance patterns
                    # 85% base attendance rate with some variation

                    # Some students have better attendance than others
                    student_base_rate = random.uniform(0.75, 0.95)

                    # Weekly patterns (slightly lower on Mondays/Fridays)
                    day_factor = 1.0
                    if current_date.weekday() == 0:  # Monday
                        day_factor = 0.9
                    elif current_date.weekday() == 4:  # Friday
                        day_factor = 0.92

                    # Calculate probability of attendance
                    attendance_probability = student_base_rate * day_factor

                    # Determine if present
                    present = random.random() < attendance_probability

                    # If absent, sometimes it's excused
                    excused = False
                    late_arrival = False
                    absence_reason = None
                    notes = None

                    if not present:
                        # 30% chance absence is excused
                        if random.random() < 0.3:
                            excused = True
                            absence_reason = random.choice(['medical', 'family', 'transport'])
                    else:
                        # 10% chance of late arrival
                        if random.random() < 0.1:
                            late_arrival = True
                            notes = "Llegada tardía"

                    # Create attendance record using raw SQL due to model mismatch
                    sql = text("""
                    INSERT INTO daily_attendance
                    (student_id, section_id, attendance_date, present, excused, late_arrival, absence_reason, notes, teacher_id)
                    VALUES (:student_id, :section_id, :attendance_date, :present, :excused, :late_arrival, :absence_reason, :notes, :teacher_id)
                    """)

                    session.execute(sql, {
                        'student_id': student.id,
                        'section_id': student.section_id,
                        'attendance_date': current_date,
                        'present': present,
                        'excused': excused,
                        'late_arrival': late_arrival,
                        'absence_reason': absence_reason,
                        'notes': notes,
                        'teacher_id': 1  # Default teacher
                    })

                    attendance_records += 1

                # Commit daily records
                session.commit()
                print(f"   ✅ Asistencia creada para {current_date.strftime('%Y-%m-%d')} ({current_date.strftime('%A')})")

            current_date += timedelta(days=1)

        print(f"\n🎉 ¡Completado! Se crearon {attendance_records} registros de asistencia")

        # Show summary by grade
        print("\n📊 RESUMEN DE ASISTENCIA POR GRADO:")
        grades = session.query(Student.grade_level).filter_by(
            academic_year='2025-2026', is_active=True
        ).distinct().all()

        for (grade,) in sorted(grades):
            grade_students = session.query(Student).filter_by(
                grade_level=grade, academic_year='2025-2026', is_active=True
            ).all()

            total_records = 0
            present_records = 0

            for student in grade_students:
                # Query directly from database
                result = session.execute(
                    text("SELECT COUNT(*), SUM(present) FROM daily_attendance WHERE student_id = :student_id"),
                    {'student_id': student.id}
                ).fetchone()

                student_total = result[0] or 0
                student_present = result[1] or 0

                total_records += student_total
                present_records += student_present

            attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0

            print(f"   📚 Grado {grade}: {attendance_rate:.1f}% asistencia ({present_records}/{total_records})")

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Iniciando creación de datos de asistencia...")
    create_sample_attendance()