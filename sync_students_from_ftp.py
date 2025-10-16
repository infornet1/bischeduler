#!/usr/bin/env python3
"""
Sync Student Data from Academic Management System XLS Export
Handles incremental updates from FTP directory
Combines first name and last name columns into full student_name
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
from sqlalchemy import func

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def normalize_grade_level(grado_str):
    """Normalize grade level strings to integer for database"""
    if pd.isna(grado_str):
        return None

    grado_str = str(grado_str).strip().lower()

    # Venezuelan grade mapping to integers
    # Preescolar = 0, Primaria = 1-6, Bachillerato = 1-5 (using 7-11 to distinguish from primaria)
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

        # Bachillerato (Año) - stored as 1-5 based on existing data
        '1er. año': 1,
        '1er año': 1,
        '2do. año': 2,
        '2do año': 2,
        '3er. año': 3,
        '3er año': 3,
        '4to. año': 4,
        '4to año': 4,
        '5to. año': 5,
        '5to año': 5,
    }

    return grade_mapping.get(grado_str, 1)


def normalize_section_name(seccion_str):
    """Normalize section letters"""
    if pd.isna(seccion_str):
        return 'U'  # Única (single section)

    seccion_str = str(seccion_str).strip().upper()
    if seccion_str in ['A', 'B', 'C', 'D', 'U']:
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
        formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
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
        return None

    genero_str = str(genero_str).strip().lower()

    if 'femenino' in genero_str or 'f' == genero_str:
        return 'F'
    elif 'masculino' in genero_str or 'm' == genero_str:
        return 'M'
    else:
        return None


def get_or_create_section(grade_level_int, section_name):
    """Get or create a section for the given grade and section"""
    if grade_level_int is None:
        grade_level_int = 1

    # Create section name based on grade level
    if grade_level_int == 0:
        grade_name = "Grupo"
    elif grade_level_int <= 6:
        grade_name = f"{grade_level_int}° Grado"
    else:
        grade_name = f"{grade_level_int}° año"

    section_full_name = f"{grade_name} {section_name}" if section_name != 'U' else grade_name

    section = db.session.query(Section).filter_by(
        grade_level=grade_level_int,
        section_letter=section_name
    ).first()

    if not section:
        logger.info(f"Creating new section: {section_full_name} (grade_level={grade_level_int}, letter={section_name})")
        section = Section(
            name=section_full_name,
            grade_level=grade_level_int,
            section_letter=section_name,
            max_students=35,
            is_active=True
        )
        # Set academic_year manually since it's not in the model
        section.academic_year = '2025-2026'
        db.session.add(section)
        db.session.flush()  # Get the section ID

    return section


def sync_students_from_excel():
    """Sync students from the latest Academic Management System export"""
    logger.info("🎓 Starting student data sync from Academic Management System")

    # Use the latest student file from FTP directory
    file_path = '/home/ftpuser/bischeduler-ftp/lista_de_estudiantes20251016-1-1htd8jp.xls'

    if not os.path.exists(file_path):
        logger.error(f"Student file not found: {file_path}")
        return False

    try:
        # Read Excel file, skipping the first 2 rows (school info and year)
        # Row 2 (index 2) contains the actual headers
        df = pd.read_excel(file_path, skiprows=2)
        logger.info(f"Read {len(df)} rows from Excel file")

        # Filter valid students (those with names)
        valid_students = df[df['Nombre'].notna() & (df['Nombre'] != '')]
        logger.info(f"Found {len(valid_students)} valid students with names")

        stats = {
            'new': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        for idx, row in valid_students.iterrows():
            try:
                # Parse basic student information
                first_name = str(row['Nombre']).strip() if pd.notna(row['Nombre']) else None
                last_name = str(row['Apellido']).strip() if pd.notna(row['Apellido']) else None

                if not first_name:
                    stats['skipped'] += 1
                    continue

                # Combine first and last name into full name
                full_name = f"{first_name} {last_name}".strip() if last_name else first_name

                # Parse other fields
                grade_level_int = normalize_grade_level(row['Grado'])
                section_name = normalize_section_name(row['Sección'])
                birth_date = parse_birth_date(row['Fecha de nacimiento'])
                cedula_escolar = parse_cedula(row['Cédula de identidad'])
                gender = determine_gender(row.get('Género', None))
                if not gender:
                    gender = 'M'  # Default if not specified
                parent_phone = str(row['Teléfono celular']).strip() if pd.notna(row.get('Teléfono celular')) else None

                # Get or create section
                section = get_or_create_section(grade_level_int, section_name)

                # Check if student already exists (by cedula or full name)
                existing_student = None
                if cedula_escolar:
                    existing_student = db.session.query(Student).filter_by(cedula_escolar=cedula_escolar).first()

                if not existing_student and full_name:
                    existing_student = db.session.query(Student).filter_by(full_name=full_name).first()

                if existing_student:
                    # Update existing student
                    existing_student.first_name = first_name
                    existing_student.last_name = last_name or ''
                    existing_student.full_name = full_name
                    existing_student.cedula_escolar = cedula_escolar
                    existing_student.fecha_nacimiento = birth_date
                    existing_student.gender = gender
                    existing_student.grade_level = grade_level_int
                    existing_student.section_id = section.id
                    existing_student.parent_phone = parent_phone
                    existing_student.is_active = True
                    stats['updated'] += 1

                    if stats['updated'] % 20 == 0:
                        logger.info(f"Updated {stats['updated']} students...")
                else:
                    # Create new student
                    # Note: academic_year is set via raw SQL due to model/DB mismatch
                    student = Student(
                        first_name=first_name,
                        last_name=last_name or '',
                        full_name=full_name,
                        cedula_escolar=cedula_escolar,
                        fecha_nacimiento=birth_date,
                        gender=gender,
                        grade_level=grade_level_int,
                        section_id=section.id,
                        parent_phone=parent_phone,
                        is_active=True
                    )
                    # Set academic_year manually since it's not in the model
                    student.academic_year = '2025-2026'

                    db.session.add(student)
                    stats['new'] += 1

                    if stats['new'] % 20 == 0:
                        logger.info(f"Added {stats['new']} new students...")

            except Exception as e:
                logger.warning(f"Error processing student at row {idx + 3}: {e}")
                stats['errors'] += 1
                continue

        # Commit all changes
        db.session.commit()

        logger.info("=" * 60)
        logger.info("✅ STUDENT SYNC COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"📊 Statistics:")
        logger.info(f"   • New students added:      {stats['new']}")
        logger.info(f"   • Existing students updated: {stats['updated']}")
        logger.info(f"   • Records skipped:         {stats['skipped']}")
        logger.info(f"   • Errors encountered:      {stats['errors']}")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ Critical error during sync: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return False


def verify_sync():
    """Verify the student sync results"""
    logger.info("🔍 Verifying student sync...")

    try:
        total_students = db.session.query(Student).count()
        active_students = db.session.query(Student).filter(Student.is_active == True).count()

        logger.info(f"📊 Database Status:")
        logger.info(f"   • Total students:  {total_students}")
        logger.info(f"   • Active students: {active_students}")

        # Section distribution
        section_dist = db.session.query(
            Section.name,
            func.count(Student.id)
        ).join(Student).group_by(Section.name).order_by(Section.name).all()

        logger.info(f"\n📚 Section Distribution:")
        for section_name, count in section_dist:
            logger.info(f"   • {section_name}: {count} students")

        return True

    except Exception as e:
        logger.error(f"Error verifying sync: {e}")
        return False


def main():
    """Main sync process"""
    logger.info("🚀 BiScheduler - Student Data Sync Tool")
    logger.info("=" * 60)

    # Create Flask app context
    app = create_app('development')

    # Override database URI to point to tenant database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Temporal2024!@localhost/ueipab_2025_data'

    with app.app_context():
        try:
            # Sync students
            if sync_students_from_excel():
                # Verify sync
                logger.info("")
                verify_sync()
                logger.info("")
                logger.info("✅ Student data sync completed successfully!")
                return True
            else:
                logger.error("❌ Student data sync failed")
                return False

        except Exception as e:
            logger.error(f"Critical error during sync: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
