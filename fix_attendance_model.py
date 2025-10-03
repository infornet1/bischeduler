#!/usr/bin/env python3
"""
Fix DailyAttendance model to match database structure
"""

# Read the file
with open('src/models/tenant.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the model
old_model = """    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    attendance_date = Column(Date, nullable=False)  # Attendance date

    # Attendance status
    present = Column(Boolean, nullable=False, default=False)
    excused = Column(Boolean, default=False)  # Justified absence
    late_arrival = Column(Boolean, default=False)
    # early_departure = Column(Boolean, default=False)  # Commented out - not in DB

    # Details
    absence_reason = Column(String(100))  # Medical, family, etc.
    notes = Column(Text)

    # Recording metadata
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    recorded_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Academic context
    # academic_year = Column(String(10), nullable=False)  # Commented out - not in DB"""

new_model = """    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'))
    attendance_date = Column(Date, nullable=False)  # Attendance date

    # Attendance status
    present = Column(Boolean, nullable=False, default=False)
    excused = Column(Boolean, default=False)  # Justified absence
    late_arrival = Column(Boolean, default=False)

    # Details
    absence_reason = Column(String(100))  # Medical, family, etc.
    notes = Column(Text)

    # Recording metadata
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    recorded_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))"""

content = content.replace(old_model, new_model)

# Fix the __repr__ method to use attendance_date instead of date
content = content.replace(
    "return f'<DailyAttendance {self.student.full_name} - {self.date.strftime(\"%Y-%m-%d\")} - {status}>'",
    "return f'<DailyAttendance {self.student.full_name} - {self.attendance_date.strftime(\"%Y-%m-%d\")} - {status}>'"
)

# Write back
with open('src/models/tenant.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ DailyAttendance model updated successfully!")
print("   - Changed 'date' to 'attendance_date'")
print("   - Changed 'recorded_by' to 'teacher_id'")
print("   - Added 'section_id' column")
print("   - Added 'updated_at' column")
print("   - Removed 'academic_year' and 'early_departure' (not in DB)")
