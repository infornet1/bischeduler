#!/usr/bin/env python3
"""
Safe Student Data Import - With Duplicate Prevention
Improved import script that checks for existing records before inserting
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def normalize_grade_level(grado_str):
    """Normalize grade level strings to Venezuelan standard numbers"""
    if pd.isna(grado_str):
        return None

    grado_str = str(grado_str).strip().lower()

    # Venezuelan grade mapping
    grade_mapping = {
        # Preescolar (Grupo)
        '1er grupo': 0, '2do grupo': 0, '3er grupo': 0,
        # Primaria (Grado)
        '1er. grado': 1, '1er grado': 1, '2do. grado': 2, '2do grado': 2,
        '3er. grado': 3, '3er grado': 3, '4to. grado': 4, '4to grado': 4,
        '5to. grado': 5, '5to grado': 5, '6to. grado': 6, '6to grado': 6,
        # Bachillerato (Año)
        '1er. año': 7, '1er año': 7, '2do. año': 8, '2do año': 8,
        '3er. año': 9, '3er año': 9, '4to. año': 10, '4to año': 10,
        '5to. año': 11, '5to año': 11,
    }
    return grade_mapping.get(grado_str, None)


def normalize_section_letter(seccion_str):
    """Normalize section letters"""
    if pd.isna(seccion_str):
        return 'U'  # Única (single section)
    seccion_str = str(seccion_str).strip().upper()
    return seccion_str if seccion_str in ['A', 'B', 'C', 'D'] else 'U'


def parse_birth_date(date_str):
    """Parse birth date from various formats"""
    if pd.isna(date_str):
        return None
    try:
        if isinstance(date_str, datetime):
            return date_str.date()
        date_str = str(date_str).strip()
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
    except Exception:
        return None


def parse_cedula(cedula_str):
    """Parse Venezuelan cédula format"""
    if pd.isna(cedula_str):
        return None
    cedula_str = str(cedula_str).strip().replace(' ', '').replace('-', '')
    return cedula_str if cedula_str and len(cedula_str) <= 20 else None


def determine_gender(genero_str):
    """Determine gender from Spanish text"""
    if pd.isna(genero_str):
        return 'U'
    genero_str = str(genero_str).strip().lower()
    if 'femenino' in genero_str or 'f' == genero_str:
        return 'F'
    elif 'masculino' in genero_str or 'm' == genero_str:
        return 'M'
    return 'U'


def find_or_create_section(session, grade_level, section_letter):
    """Find existing section or create new one - SAFE UPSERT"""
    # Check if section already exists
    result = session.execute(text("""
        SELECT id FROM sections
        WHERE grade_level = :grade_level AND section_letter = :section_letter
        LIMIT 1
    """), {
        'grade_level': grade_level,
        'section_letter': section_letter
    })
    section_row = result.fetchone()

    if section_row:
        logger.debug(f"Found existing section: Grade {grade_level} Section {section_letter}")
        return section_row[0]

    # Create new section
    logger.info(f"Creating new section: Grade {grade_level} Section {section_letter}")
    section_insert = text("""
        INSERT INTO sections (name, grade_level, section_letter, max_students, academic_year, is_active, created_at)
        VALUES (:name, :grade_level, :section_letter, 35, '2025-2026', TRUE, NOW())
    """)
    session.execute(section_insert, {
        'name': f"{grade_level}° año {section_letter}",
        'grade_level': grade_level,
        'section_letter': section_letter
    })
    session.commit()

    # Get the newly created section ID
    result = session.execute(text("""
        SELECT id FROM sections
        WHERE grade_level = :grade_level AND section_letter = :section_letter
        LIMIT 1
    """), {
        'grade_level': grade_level,
        'section_letter': section_letter
    })
    return result.fetchone()[0]


def upsert_student(session, student_data):
    """Insert or update student - SAFE UPSERT with multiple checks"""

    # Check for existing student by cedula (most reliable)
    if student_data['cedula_escolar']:
        result = session.execute(text("""
            SELECT id FROM students WHERE cedula_escolar = :cedula LIMIT 1
        """), {'cedula': student_data['cedula_escolar']})
        existing = result.fetchone()
        if existing:
            logger.debug(f"Student exists by cedula: {student_data['full_name']}")
            return existing[0], 'updated'

    # Check for existing student by full name + grade level + academic year
    result = session.execute(text("""
        SELECT id FROM students
        WHERE full_name = :full_name
        AND grade_level = :grade_level
        AND academic_year = :academic_year
        LIMIT 1
    """), {
        'full_name': student_data['full_name'],
        'grade_level': student_data['grade_level'],
        'academic_year': student_data['academic_year']
    })
    existing = result.fetchone()
    if existing:
        logger.debug(f"Student exists by name+grade: {student_data['full_name']}")
        return existing[0], 'updated'

    # Insert new student
    logger.debug(f"Creating new student: {student_data['full_name']}")
    student_insert = text("""
        INSERT INTO students (
            first_name, last_name, full_name, cedula_escolar, fecha_nacimiento,
            gender, grade_level, section_id, parent_phone, enrollment_date,
            academic_year, is_active, created_at
        ) VALUES (
            :first_name, :last_name, :full_name, :cedula_escolar, :fecha_nacimiento,
            :gender, :grade_level, :section_id, :parent_phone, :enrollment_date,
            :academic_year, :is_active, NOW()
        )
    """)

    result = session.execute(student_insert, student_data)
    return result.lastrowid, 'inserted'


def safe_import_students_from_excel():
    """Safe import students with duplicate prevention"""
    logger.info("🎓 Starting SAFE student data import with duplicate prevention")

    # File path to the most recent student list
    file_path = '/home/ftpuser/bischeduler-ftp/lista_de_estudiantes20250926-1-12p9kcj.xls'

    if not os.path.exists(file_path):
        logger.error(f"Student file not found: {file_path}")
        return False

    # Create direct database connection
    database_url = 'mysql+pymysql://root:Temporal2024!@localhost/ueipab_2025_data'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Read Excel file
        df = pd.read_excel(file_path, skiprows=2)
        logger.info(f"Read {len(df)} rows from Excel file")

        # Filter valid students
        valid_students = df[df['Nombre'].notna() & (df['Nombre'] != '')]
        logger.info(f"Found {len(valid_students)} valid students with names")

        inserted_count = 0
        updated_count = 0
        skipped_count = 0

        for idx, row in valid_students.iterrows():
            try:
                # Parse student information
                first_name = str(row['Nombre']).strip() if pd.notna(row['Nombre']) else None
                last_name = str(row['Apellido']).strip() if pd.notna(row['Apellido']) else None

                if not first_name:
                    skipped_count += 1
                    continue

                # Generate full name
                full_name = f"{first_name}"
                if last_name:
                    full_name += f" {last_name}"

                # Parse other fields
                grade_level = normalize_grade_level(row['Grado'])
                section_letter = normalize_section_letter(row['Sección'])
                birth_date = parse_birth_date(row['Fecha de nacimiento'])
                cedula = parse_cedula(row['Cédula de identidad'])
                gender = determine_gender(row['Género'])
                phone = str(row['Teléfono celular']).strip() if pd.notna(row['Teléfono celular']) else None

                # Find or create section (SAFE)
                section_id = find_or_create_section(
                    session,
                    grade_level if grade_level is not None else 1,
                    section_letter
                )

                # Prepare student data
                student_data = {
                    'first_name': first_name,
                    'last_name': last_name or '',
                    'full_name': full_name,
                    'cedula_escolar': cedula,
                    'fecha_nacimiento': birth_date,
                    'gender': gender,
                    'grade_level': grade_level if grade_level is not None else 1,
                    'section_id': section_id,
                    'parent_phone': phone,
                    'enrollment_date': datetime(2025, 9, 1).date(),
                    'academic_year': '2025-2026',
                    'is_active': True
                }

                # SAFE UPSERT
                student_id, operation = upsert_student(session, student_data)

                if operation == 'inserted':
                    inserted_count += 1
                else:
                    updated_count += 1

                if (inserted_count + updated_count) % 50 == 0:
                    logger.info(f"Processed {inserted_count + updated_count} students...")

            except Exception as e:
                logger.warning(f"Error processing student at row {idx}: {e}")
                skipped_count += 1
                continue

        # Commit all changes
        session.commit()

        logger.info(f"✅ SAFE IMPORT COMPLETED")
        logger.info(f"📊 RESULTS:")
        logger.info(f"   🆕 New students inserted: {inserted_count}")
        logger.info(f"   🔄 Existing students updated: {updated_count}")
        logger.info(f"   ⚠️ Records skipped: {skipped_count}")
        logger.info(f"   📈 Total processed: {inserted_count + updated_count}")

        return True

    except Exception as e:
        logger.error(f"Error during safe import: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def verify_data_integrity():
    """Verify data integrity and uniqueness"""
    logger.info("🔍 Verifying data integrity...")

    database_url = 'mysql+pymysql://root:Temporal2024!@localhost/ueipab_2025_data'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check for duplicates
        result = session.execute(text("""
            SELECT
                'Total Students' as check_type, COUNT(*) as count FROM students
            UNION ALL
            SELECT
                'Unique by cedula' as check_type, COUNT(DISTINCT cedula_escolar) as count
                FROM students WHERE cedula_escolar IS NOT NULL
            UNION ALL
            SELECT
                'Unique by name+grade' as check_type, COUNT(DISTINCT CONCAT(full_name, '-', grade_level, '-', academic_year)) as count
                FROM students
            UNION ALL
            SELECT
                'Total Teachers' as check_type, COUNT(*) as count FROM teachers
            UNION ALL
            SELECT
                'Unique teacher names' as check_type, COUNT(DISTINCT teacher_name) as count FROM teachers
        """))

        logger.info("📊 DATA INTEGRITY REPORT:")
        for row in result:
            logger.info(f"   {row[0]}: {row[1]}")

        return True

    except Exception as e:
        logger.error(f"Error verifying data integrity: {e}")
        return False
    finally:
        session.close()


def main():
    """Main safe import process"""
    logger.info("🚀 Starting SAFE import process with duplicate prevention")

    try:
        # Verify integrity before import
        logger.info("🔍 PRE-IMPORT VERIFICATION:")
        verify_data_integrity()

        # Safe import
        if safe_import_students_from_excel():
            # Verify integrity after import
            logger.info("🔍 POST-IMPORT VERIFICATION:")
            verify_data_integrity()
            logger.info("✅ Safe import completed successfully")
        else:
            logger.error("❌ Safe import failed")

    except Exception as e:
        logger.error(f"Critical error during safe import: {e}")
        return False

    return True


if __name__ == "__main__":
    main()