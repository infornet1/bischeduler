#!/usr/bin/env python3
"""
Import Student Data from Real UEIPAB Excel File
Fixes data consistency issues by importing actual student data
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, '/var/www/dev/bischeduler')

from src.core.app import create_app, db
from src.models.tenant import Student, Section
from src.models.master import Tenant
from src.tenants.middleware import get_current_tenant

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
    logger.info("🎓 Starting student data import from real UEIPAB Excel file")

    # File path to the most recent student list (September 26, 2025 - 215 students)
    file_path = '/home/ftpuser/bischeduler-ftp/lista_de_estudiantes20250926-1-12p9kcj.xls'

    if not os.path.exists(file_path):
        logger.error(f"Student file not found: {file_path}")
        return False

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

                # Create student code
                student_code = f"EST{2025}{grade_level or 0:02d}{imported_count + 1:03d}"

                # Create student record (based on actual Student model fields)
                # Find or create a section for this student
                section = db.session.query(Section).filter_by(
                    grade_level=grade_level if grade_level is not None else 1,
                    section_letter=section_letter
                ).first()

                if not section:
                    # Create section if it doesn't exist
                    section = Section(
                        name=f"{grade_level if grade_level is not None else 1}° año {section_letter}",
                        grade_level=grade_level if grade_level is not None else 1,
                        section_letter=section_letter,
                        max_students=35,
                        academic_year='2025-2026',
                        is_active=True
                    )
                    db.session.add(section)
                    db.session.flush()  # Get the section ID

                student = Student(
                    first_name=first_name,
                    last_name=last_name or '',
                    full_name=full_name,
                    cedula_escolar=cedula,
                    fecha_nacimiento=birth_date,
                    gender=gender,
                    grade_level=grade_level if grade_level is not None else 1,
                    section_id=section.id,
                    parent_phone=phone,
                    enrollment_date=datetime(2025, 9, 1).date(),
                    academic_year='2025-2026',
                    is_active=True
                )

                db.session.add(student)
                imported_count += 1

                if imported_count % 50 == 0:
                    logger.info(f"Imported {imported_count} students...")

            except Exception as e:
                logger.warning(f"Error importing student at row {idx}: {e}")
                skipped_count += 1
                continue

        # Commit all students
        db.session.commit()
        logger.info(f"✅ Successfully imported {imported_count} students")
        logger.info(f"⚠️ Skipped {skipped_count} invalid records")

        return True

    except Exception as e:
        logger.error(f"Error importing students: {e}")
        db.session.rollback()
        return False


def verify_import():
    """Verify the student import results"""
    logger.info("🔍 Verifying student import...")

    try:
        total_students = db.session.query(Student).count()
        active_students = db.session.query(Student).filter(Student.is_active == True).count()

        logger.info(f"Total students in database: {total_students}")
        logger.info(f"Active students: {active_students}")

        # Grade distribution
        from sqlalchemy import func
        grade_dist = db.session.query(
            Student.grade_level,
            func.count(Student.id)
        ).group_by(Student.grade_level).all()

        logger.info("Grade distribution:")
        for grade, count in grade_dist:
            logger.info(f"  Grade {grade}: {count} students")

        return True

    except Exception as e:
        logger.error(f"Error verifying import: {e}")
        return False


def main():
    """Main import process"""
    logger.info("🚀 Starting student data import process")

    # Create Flask app context
    app = create_app('development')

    # Override database URI to point to tenant database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Temporal2024!@localhost/ueipab_2025_data'

    with app.app_context():
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