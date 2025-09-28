#!/usr/bin/env python3
"""
Direct Student Data Import - Bypassing Flask App
Import students directly into the ueipab_2025_data database
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
        '1er grupo': 0,
        '2do grupo': 0,
        '3er grupo': 0,

        # Primaria (Grado)
        '1er. grado': 1,
        '1er grado': 1,
        '2do. grado': 2,
        '2do grado': 2,
        '3er. grado': 3,
        '3er grado': 3,
        '4to. grado': 4,
        '4to grado': 4,
        '5to. grado': 5,
        '5to grado': 5,
        '6to. grado': 6,
        '6to grado': 6,

        # Bachillerato (Año)
        '1er. año': 7,
        '1er año': 7,
        '2do. año': 8,
        '2do año': 8,
        '3er. año': 9,
        '3er año': 9,
        '4to. año': 10,
        '4to año': 10,
        '5to. año': 11,
        '5to año': 11,
    }

    return grade_mapping.get(grado_str, None)


def normalize_section_letter(seccion_str):
    """Normalize section letters"""
    if pd.isna(seccion_str):
        return 'U'  # Única (single section)

    seccion_str = str(seccion_str).strip().upper()
    if seccion_str in ['A', 'B', 'C', 'D']:
        return seccion_str
    else:
        return 'U'


def parse_birth_date(date_str):
    """Parse birth date from various formats"""
    if pd.isna(date_str):
        return None

    try:
        if isinstance(date_str, datetime):
            return date_str.date()

        date_str = str(date_str).strip()

        # Try different date formats
        formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        for fmt in formats:
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

    cedula_str = str(cedula_str).strip()
    # Remove extra characters and normalize
    cedula_str = cedula_str.replace(' ', '').replace('-', '')

    if len(cedula_str) > 20:  # Too long, probably malformed
        return None

    return cedula_str if cedula_str else None


def determine_gender(genero_str):
    """Determine gender from Spanish text"""
    if pd.isna(genero_str):
        return 'U'  # Unknown

    genero_str = str(genero_str).strip().lower()

    if 'femenino' in genero_str or 'f' == genero_str:
        return 'F'
    elif 'masculino' in genero_str or 'm' == genero_str:
        return 'M'
    else:
        return 'U'


def import_students_from_excel():
    """Import students from real UEIPAB Excel file"""
    logger.info("🎓 Starting direct student data import from real UEIPAB Excel file")

    # File path to the most recent student list (September 26, 2025 - 215 students)
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
        # Read Excel file, skipping header rows
        df = pd.read_excel(file_path, skiprows=2)
        logger.info(f"Read {len(df)} rows from Excel file")

        # Filter valid students (those with names)
        valid_students = df[df['Nombre'].notna() & (df['Nombre'] != '')]
        logger.info(f"Found {len(valid_students)} valid students with names")

        imported_count = 0
        skipped_count = 0

        for idx, row in valid_students.iterrows():
            try:
                # Parse basic student information
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

                # Find or create a section for this student
                result = session.execute(text("""
                    SELECT id FROM sections
                    WHERE grade_level = :grade_level AND section_letter = :section_letter
                    LIMIT 1
                """), {
                    'grade_level': grade_level if grade_level is not None else 1,
                    'section_letter': section_letter
                })
                section_row = result.fetchone()

                if not section_row:
                    # Create section if it doesn't exist
                    section_insert = text("""
                        INSERT INTO sections (name, grade_level, section_letter, max_students, academic_year, is_active, created_at)
                        VALUES (:name, :grade_level, :section_letter, 35, '2025-2026', TRUE, NOW())
                    """)
                    session.execute(section_insert, {
                        'name': f"{grade_level if grade_level is not None else 1}° año {section_letter}",
                        'grade_level': grade_level if grade_level is not None else 1,
                        'section_letter': section_letter
                    })
                    session.commit()

                    # Get the newly created section ID
                    result = session.execute(text("""
                        SELECT id FROM sections
                        WHERE grade_level = :grade_level AND section_letter = :section_letter
                        LIMIT 1
                    """), {
                        'grade_level': grade_level if grade_level is not None else 1,
                        'section_letter': section_letter
                    })
                    section_row = result.fetchone()

                section_id = section_row[0]

                # Insert student record
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

                session.execute(student_insert, {
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
                })

                imported_count += 1

                if imported_count % 50 == 0:
                    logger.info(f"Imported {imported_count} students...")

            except Exception as e:
                logger.warning(f"Error importing student at row {idx}: {e}")
                skipped_count += 1
                continue

        # Commit all students
        session.commit()
        logger.info(f"✅ Successfully imported {imported_count} students")
        logger.info(f"⚠️ Skipped {skipped_count} invalid records")

        return True

    except Exception as e:
        logger.error(f"Error importing students: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def verify_import():
    """Verify the student import results"""
    logger.info("🔍 Verifying student import...")

    # Create direct database connection
    database_url = 'mysql+pymysql://root:Temporal2024!@localhost/ueipab_2025_data'
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get total students
        result = session.execute(text("SELECT COUNT(*) FROM students"))
        total_students = result.scalar()

        result = session.execute(text("SELECT COUNT(*) FROM students WHERE is_active = TRUE"))
        active_students = result.scalar()

        logger.info(f"Total students in database: {total_students}")
        logger.info(f"Active students: {active_students}")

        # Grade distribution
        result = session.execute(text("""
            SELECT grade_level, COUNT(*) as count
            FROM students
            GROUP BY grade_level
            ORDER BY grade_level
        """))

        logger.info("Grade distribution:")
        for row in result:
            logger.info(f"  Grade {row[0]}: {row[1]} students")

        return True

    except Exception as e:
        logger.error(f"Error verifying import: {e}")
        return False
    finally:
        session.close()


def main():
    """Main import process"""
    logger.info("🚀 Starting direct student data import process")

    try:
        # Import students
        if import_students_from_excel():
            # Verify import
            verify_import()
            logger.info("✅ Student data import completed successfully")
        else:
            logger.error("❌ Student data import failed")

    except Exception as e:
        logger.error(f"Critical error during import: {e}")
        return False

    return True


if __name__ == "__main__":
    main()