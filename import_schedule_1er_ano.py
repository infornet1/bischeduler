#!/usr/bin/env python3
"""
Import Real Schedule Data for 1er Año from Excel
BiScheduler - UEIPAB 2025-2026
"""

import pandas as pd
import mysql.connector
import re
from datetime import datetime, time
import sys
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Temporal2024!',
    'database': 'ueipab_2025_data',
    'charset': 'utf8mb4'
}

EXCEL_FILE = '/home/ftpuser/bischeduler-ftp/Horarios de Estudiantes a\udcf1o 2025 - 2026.xlsx'
TARGET_SHEET = '1er año'
TARGET_SECTION = '1er. Año'  # Database section name

def connect_to_db():
    """Connect to the tenant database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def get_section_id(cursor, section_name):
    """Get section ID from database"""
    cursor.execute("SELECT id FROM sections WHERE name = %s AND is_active = TRUE", (section_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_teacher_id(cursor, teacher_name):
    """Get teacher ID from database, trying different name variations"""
    # Clean up the teacher name
    teacher_name = teacher_name.strip().upper()

    # Teacher name mappings for common variations
    teacher_mapping = {
        'LUISA ABREU': 'LUISA ELENA ABREU',
        'LUISA  ABREU': 'LUISA ELENA ABREU',  # Double space
        'ROBERT QUIJADA': 'ROBERT QUIJADA',
        'MARÍA NIETO': 'MARIA NIETO',
        'MARIA NIETO': 'MARIA NIETO',
        'LUIS RODRÍGUEZ': 'LUIS RODRIGUEZ',
        'LUIS RODRíGUEZ': 'LUIS RODRIGUEZ'
    }

    # Use mapping if available
    mapped_teacher = teacher_mapping.get(teacher_name, teacher_name)

    # Try exact match first
    cursor.execute("SELECT id FROM teachers WHERE UPPER(teacher_name) = %s AND is_active = TRUE", (mapped_teacher,))
    result = cursor.fetchone()
    if result:
        return result[0]

    # Try partial match (first name + last name)
    words = mapped_teacher.split()
    if len(words) >= 2:
        # Try "FIRST LAST" pattern
        partial_name = f"{words[0]} {words[-1]}"
        cursor.execute("SELECT id FROM teachers WHERE UPPER(teacher_name) LIKE %s AND is_active = TRUE", (f"%{partial_name}%",))
        result = cursor.fetchone()
        if result:
            return result[0]

    print(f"⚠️  Teacher not found: {teacher_name} (mapped to: {mapped_teacher})")
    return None

def get_subject_id(cursor, subject_name):
    """Get subject ID from database"""
    # Clean up subject name
    subject_name = subject_name.strip().upper()

    # Subject mapping for common variations
    subject_mapping = {
        'MATEMÁTICA': 'MATEMÁTICAS',
        'MATEMATICAS': 'MATEMÁTICAS',
        'IDIOMAS': 'INGLÉS',
        'INGLES': 'INGLÉS',
        'BIOLOGÍA AMBIENTE Y TECNOLOGÍA': 'BIOLOGÍA AMBIENTE Y TECNOLOGÍA',
        'CASTELLANO Y LITERATURA': 'CASTELLANO Y LITERATURA',
        'EDUCACIÓN FÍSICA': 'EDUCACIÓN FÍSICA',
        'EDUCACION FISICA': 'EDUCACIÓN FÍSICA',
        'LÓGICA MATEMÁTICA': 'LOGICA MATEMÁNTICA',
        'LOGICA MATEMATICA': 'LOGICA MATEMÁNTICA',
        'FÍSICA': 'FISICA',
        'FISICA': 'FISICA',
        'QUÍMICA': 'QUIMICA',
        'QUIMICA': 'QUIMICA',
        'GHC PARA LA SOBERANÍA NACIONAL': 'GHC PARA LA SOBERANIA NACIONAL',
        'INNOVACIÓN TP': 'Innovación TP',
        'ORIENTACIÓN VOCACIONAL': 'Orientacion Vocacional'
    }

    # Use mapping if available
    mapped_subject = subject_mapping.get(subject_name, subject_name)

    cursor.execute("SELECT id FROM subjects WHERE UPPER(subject_name) = %s AND is_active = TRUE", (mapped_subject,))
    result = cursor.fetchone()

    if not result:
        print(f"⚠️  Subject not found: {subject_name} (mapped to: {mapped_subject})")
        return None

    return result[0]

def get_time_period_id(cursor, start_time, end_time):
    """Get time period ID from database"""
    cursor.execute("""
        SELECT id FROM time_periods
        WHERE start_time = %s AND end_time = %s
        AND academic_year = '2025-2026' AND is_active = TRUE
        ORDER BY id LIMIT 1
    """, (start_time, end_time))
    result = cursor.fetchone()
    return result[0] if result else None

def get_classroom_id(cursor):
    """Get a default classroom ID"""
    cursor.execute("SELECT id FROM classrooms WHERE is_active = TRUE ORDER BY id LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result else 1

def parse_time_range(time_str):
    """Parse time range string like '7:00:00 - 7:40:00' or '1:00:00 - 1:40:00'"""
    try:
        start_str, end_str = time_str.split(' - ')

        # Convert 1:xx:xx format to 13:xx:xx (afternoon)
        if start_str.startswith('1:') and len(start_str.split(':')[0]) == 1:
            start_str = '13' + start_str[1:]
        if end_str.startswith('1:') and len(end_str.split(':')[0]) == 1:
            end_str = '13' + end_str[1:]

        start_time = datetime.strptime(start_str, '%H:%M:%S').time()
        end_time = datetime.strptime(end_str, '%H:%M:%S').time()
        return start_time, end_time
    except:
        print(f"⚠️  Could not parse time: {time_str}")
        return None, None

def parse_subject_teacher(cell_content):
    """Parse subject and teacher from cell content like 'MATEMÁTICA\\nMARÍA NIETO'"""
    if pd.isna(cell_content) or str(cell_content).strip() == '---':
        return None, None

    content = str(cell_content).strip()

    # Skip break periods
    if 'RECESO' in content.upper():
        return None, None

    # Split by newline to separate subject and teacher
    lines = content.split('\\n')
    if len(lines) < 2:
        lines = content.split('\n')

    if len(lines) >= 2:
        subject = lines[0].strip()
        teacher = lines[1].strip()
        return subject, teacher
    else:
        # If no teacher specified, just subject
        return content, None

def clear_existing_schedule(cursor, section_id):
    """Clear existing schedule assignments for the section"""
    cursor.execute("""
        DELETE FROM schedule_assignments
        WHERE section_id = %s AND academic_year = '2025-2026'
    """, (section_id,))
    print(f"🗑️  Cleared existing schedule assignments for section {section_id}")

def import_schedule():
    """Main import function"""
    print("🚀 Starting import of 1er Año schedule from Excel...")

    # Connect to database
    conn = connect_to_db()
    if not conn:
        return False

    cursor = conn.cursor(buffered=True)

    try:
        # Get section ID
        section_id = get_section_id(cursor, TARGET_SECTION)
        if not section_id:
            print(f"❌ Section '{TARGET_SECTION}' not found in database")
            return False

        print(f"📋 Found section: {TARGET_SECTION} (ID: {section_id})")

        # Clear existing schedule
        clear_existing_schedule(cursor, section_id)
        conn.commit()

        # Read Excel file
        print(f"📖 Reading Excel file: {TARGET_SHEET}")
        df = pd.read_excel(EXCEL_FILE, sheet_name=TARGET_SHEET, header=None)

        # Day mapping
        days = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']

        imported_count = 0
        skipped_count = 0

        # Process each row (starting from row 2, as rows 0-1 are headers)
        for row_idx in range(2, len(df)):
            time_cell = df.iloc[row_idx, 0]

            if pd.isna(time_cell):
                continue

            time_str = str(time_cell).strip()

            # Skip break periods
            if 'RECESO' in time_str.upper():
                print(f"⏸️  Skipping break period: {time_str}")
                continue

            # Parse time range
            start_time, end_time = parse_time_range(time_str)
            if not start_time or not end_time:
                print(f"⚠️  Skipping invalid time: {time_str}")
                continue

            # Get time period ID
            time_period_id = get_time_period_id(cursor, start_time, end_time)
            if not time_period_id:
                print(f"⚠️  Time period not found: {start_time}-{end_time}")
                continue

            # Process each day
            for day_idx, day in enumerate(days):
                if day_idx + 1 >= len(df.columns):
                    break

                cell_content = df.iloc[row_idx, day_idx + 1]
                subject_name, teacher_name = parse_subject_teacher(cell_content)

                if not subject_name:
                    skipped_count += 1
                    continue

                # Get database IDs
                subject_id = get_subject_id(cursor, subject_name)
                teacher_id = get_teacher_id(cursor, teacher_name) if teacher_name else None
                classroom_id = get_classroom_id(cursor)

                if not subject_id:
                    print(f"⚠️  Skipping - Subject not found: {subject_name}")
                    skipped_count += 1
                    continue

                if not teacher_id:
                    print(f"⚠️  Skipping - Teacher not found: {teacher_name}")
                    skipped_count += 1
                    continue

                # Insert schedule assignment
                try:
                    cursor.execute("""
                        INSERT INTO schedule_assignments
                        (tenant_id, section_id, subject_id, teacher_id, classroom_id, time_period_id,
                         day_of_week, academic_year, assignment_type, is_active, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        1, section_id, subject_id, teacher_id, classroom_id, time_period_id,
                        day, '2025-2026', 'regular', True, datetime.now()
                    ))

                    imported_count += 1
                    print(f"✅ {day.upper()} {time_str}: {subject_name} - {teacher_name}")

                except Exception as e:
                    print(f"❌ Error inserting assignment: {e}")
                    skipped_count += 1

        # Commit changes
        conn.commit()

        print(f"\n🎉 Import completed!")
        print(f"   ✅ Imported: {imported_count} assignments")
        print(f"   ⚠️  Skipped: {skipped_count} assignments")

        return True

    except Exception as e:
        print(f"❌ Error during import: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = import_schedule()
    sys.exit(0 if success else 1)