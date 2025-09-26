"""
BiScheduler Data Importer
Import Venezuelan education data from Phase 0 migration
Enhanced for real K12 schedule requirements
"""

import csv
import logging
from datetime import datetime, timezone, time
from typing import Dict, List, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.models.tenant import (
    Base, TimePeriod, Classroom, Section, Subject, Teacher,
    TeacherSubject, TeacherWorkload, EducationalLevel,
    SubjectCategory, RoomType
)

logger = logging.getLogger(__name__)


class VenezuelanDataImporter:
    """
    Import Venezuelan K12 education data from Phase 0 migration
    Handles real curriculum data extracted from existing systems
    """

    def __init__(self, tenant_database_url: str, academic_year: str = "2025-2026"):
        self.database_url = tenant_database_url
        self.academic_year = academic_year
        self.engine = create_engine(tenant_database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def initialize_tenant_database(self):
        """Create all tenant database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tenant database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create tenant database tables: {str(e)}")
            return False

    def import_time_periods(self, data_file_path: str) -> int:
        """
        Import Venezuelan bimodal time periods from Phase 0 migration

        Expected format: source_id, period_name, start_time, end_time, is_break, schedule_type
        """
        session = self.SessionLocal()
        imported_count = 0

        try:
            with open(data_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')

                for row_num, row in enumerate(reader, 1):
                    try:
                        # Parse time strings (format: HH:MM:SS)
                        start_time = datetime.strptime(row['start_time'], '%H:%M:%S').time()
                        end_time = datetime.strptime(row['end_time'], '%H:%M:%S').time()

                        time_period = TimePeriod(
                            period_name=row['period_name'],
                            start_time=start_time,
                            end_time=end_time,
                            is_break=bool(int(row['is_break'])),
                            schedule_type=row['schedule_type'],
                            display_order=row_num,
                            academic_year=self.academic_year
                        )

                        session.add(time_period)
                        imported_count += 1

                    except Exception as e:
                        logger.error(f"Error importing time period row {row_num}: {str(e)}")

                session.commit()
                logger.info(f"Imported {imported_count} time periods")
                return imported_count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to import time periods: {str(e)}")
            return 0
        finally:
            session.close()

    def import_classrooms(self, data_file_path: str) -> int:
        """
        Import classroom infrastructure from Phase 0 migration

        Expected format: source_id, name, capacity, room_type, is_active
        """
        session = self.SessionLocal()
        imported_count = 0

        try:
            with open(data_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')

                for row in reader:
                    try:
                        # Map room type string to enum
                        room_type = RoomType.REGULAR
                        if row['room_type'] == 'sports':
                            room_type = RoomType.SPORTS
                        elif row['room_type'] == 'laboratory':
                            room_type = RoomType.LABORATORY

                        classroom = Classroom(
                            source_id=int(row['source_id']),
                            name=row['name'],
                            capacity=int(row['capacity']),
                            room_type=room_type,
                            is_active=bool(int(row['is_active']))
                        )

                        session.add(classroom)
                        imported_count += 1

                    except Exception as e:
                        logger.error(f"Error importing classroom: {str(e)}")

                session.commit()
                logger.info(f"Imported {imported_count} classrooms")
                return imported_count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to import classrooms: {str(e)}")
            return 0
        finally:
            session.close()

    def import_sections(self, data_file_path: str) -> int:
        """
        Import grade sections from Phase 0 migration

        Expected format: source_id, name, grade_level, section_letter
        """
        session = self.SessionLocal()
        imported_count = 0

        try:
            with open(data_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')

                for row in reader:
                    try:
                        section = Section(
                            source_id=int(row['source_id']),
                            name=row['name'],
                            grade_level=int(row['grade_level']),
                            section_letter=row['section_letter'],
                            educational_level=EducationalLevel.BACHILLERATO,
                            academic_year=self.academic_year
                        )

                        session.add(section)
                        imported_count += 1

                    except Exception as e:
                        logger.error(f"Error importing section: {str(e)}")

                session.commit()
                logger.info(f"Imported {imported_count} sections")
                return imported_count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to import sections: {str(e)}")
            return 0
        finally:
            session.close()

    def import_subjects(self, data_file_path: str) -> int:
        """
        Import Venezuelan curriculum subjects from Phase 0 migration

        Expected format: source_id, subject_name, curriculum_level, subject_category, is_core_subject, weekly_hours_default
        """
        session = self.SessionLocal()
        imported_count = 0

        try:
            with open(data_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')

                for row in reader:
                    try:
                        # Map category string to enum
                        category_map = {
                            'mathematics': SubjectCategory.MATHEMATICS,
                            'language': SubjectCategory.LANGUAGE,
                            'science': SubjectCategory.SCIENCE,
                            'social_studies': SubjectCategory.SOCIAL_STUDIES,
                            'sports': SubjectCategory.SPORTS,
                            'general': SubjectCategory.GENERAL
                        }

                        subject_category = category_map.get(row['subject_category'], SubjectCategory.GENERAL)

                        subject = Subject(
                            source_id=int(row['source_id']),
                            subject_name=row['subject_name'],
                            short_name=row['subject_name'][:50],  # Create short name
                            curriculum_level=EducationalLevel.BACHILLERATO,
                            subject_category=subject_category,
                            is_core_subject=bool(int(row['is_core_subject'])),
                            weekly_hours_default=int(row['weekly_hours_default']),
                            academic_year=self.academic_year
                        )

                        session.add(subject)
                        imported_count += 1

                    except Exception as e:
                        logger.error(f"Error importing subject: {str(e)}")

                session.commit()
                logger.info(f"Imported {imported_count} subjects")
                return imported_count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to import subjects: {str(e)}")
            return 0
        finally:
            session.close()

    def import_teachers(self, data_file_path: str) -> int:
        """
        Import Venezuelan teachers from Phase 0 migration

        Expected format: source_id, teacher_name, area_name, specialization, is_active, confirmed_in_excel
        """
        session = self.SessionLocal()
        imported_count = 0

        try:
            with open(data_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')

                for row in reader:
                    try:
                        # Parse teacher name
                        full_name = row['teacher_name'].strip()
                        name_parts = full_name.split()
                        first_name = name_parts[0] if name_parts else ""
                        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                        teacher = Teacher(
                            source_id=int(row['source_id']),
                            teacher_name=full_name,
                            first_name=first_name,
                            last_name=last_name,
                            area_specialization=row['specialization'],
                            is_active=bool(int(row['is_active'])),
                            academic_year=self.academic_year
                        )

                        session.add(teacher)
                        imported_count += 1

                    except Exception as e:
                        logger.error(f"Error importing teacher: {str(e)}")

                session.commit()
                logger.info(f"Imported {imported_count} teachers")
                return imported_count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to import teachers: {str(e)}")
            return 0
        finally:
            session.close()

    def create_enhanced_teacher_subject_relationships(self) -> int:
        """
        Create teacher-subject relationships based on K12 schedule analysis
        Maps teachers to their specialized subjects with hour allocations
        """
        session = self.SessionLocal()
        created_count = 0

        try:
            # Enhanced teacher-subject mappings based on real 2025-2026 data
            teacher_subject_mappings = [
                # Mathematics teachers
                ("MARIA NIETO", "MATEMÁTICAS", 22),
                ("RAMON BELLO", "MATEMÁTICAS", 14),
                ("RAMON BELLO", "LÓGICA MATEMÁTICA", 4),

                # Language teachers
                ("ISMARY ARCILA", "CASTELLANO Y LITERATURA", 26),
                ("STEFANY ROMERO", "IDIOMAS", 26),
                ("GIOVANNY VEZZA", "IDIOMAS", 26),

                # Science teachers
                ("FLORMAR HERNANDEZ", "QUÍMICA", 22),
                ("AUDREY GARCIA", "BIOLOGÍA AMBIENTE Y TECNOLOGÍA", 12),
                ("VIRGINIA VERDE", "BIOLOGÍA AMBIENTE Y TECNOLOGÍA", 20),
                ("LUISA ABREU", "FÍSICA", 24),

                # Social Studies
                ("MARIA FIGUERA", "GHC PARA LA SOBERANÍA NACIONAL", 32),

                # Physical Education
                ("EMILIO ISEA", "EDUCACIÓN FÍSICA", 26),
                ("LEYDIMAR ARAY", "EDUCACIÓN FÍSICA", 16),

                # Other subjects
                ("ROBERT QUIJADA", "EDUCACIÓN FINANCIERA", 15),
                ("ROBERT QUIJADA", "LÓGICA MATEMÁTICA", 14),
                ("JESUS DI CESARE", "MÚSICA", 17),
                ("LUIS RODRIGUEZ", "CASTELLANO Y LITERATURA", 16),
            ]

            for teacher_name, subject_name, weekly_hours in teacher_subject_mappings:
                try:
                    # Find teacher and subject
                    teacher = session.query(Teacher).filter_by(teacher_name=teacher_name).first()
                    subject = session.query(Subject).filter_by(subject_name=subject_name).first()

                    if teacher and subject:
                        # Check if relationship already exists
                        existing = session.query(TeacherSubject).filter_by(
                            teacher_id=teacher.id,
                            subject_id=subject.id,
                            academic_year=self.academic_year
                        ).first()

                        if not existing:
                            teacher_subject = TeacherSubject(
                                teacher_id=teacher.id,
                                subject_id=subject.id,
                                weekly_hours=weekly_hours,
                                is_primary_subject=(weekly_hours >= 20),  # Primary if 20+ hours
                                academic_year=self.academic_year
                            )

                            session.add(teacher_subject)
                            created_count += 1

                            # Update teacher's current weekly hours
                            teacher.current_weekly_hours = (teacher.current_weekly_hours or 0) + weekly_hours

                    else:
                        logger.warning(f"Teacher '{teacher_name}' or subject '{subject_name}' not found")

                except Exception as e:
                    logger.error(f"Error creating teacher-subject relationship: {str(e)}")

            session.commit()
            logger.info(f"Created {created_count} teacher-subject relationships")
            return created_count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create teacher-subject relationships: {str(e)}")
            return 0
        finally:
            session.close()

    def create_teacher_workload_records(self) -> int:
        """
        Create workload validation records for all teachers
        Based on K12 schedule analysis findings
        """
        session = self.SessionLocal()
        created_count = 0

        try:
            teachers = session.query(Teacher).filter_by(academic_year=self.academic_year).all()

            for teacher in teachers:
                # Calculate total hours from teacher-subject relationships
                total_hours = session.query(TeacherSubject).filter_by(
                    teacher_id=teacher.id,
                    academic_year=self.academic_year
                ).with_entities(TeacherSubject.weekly_hours).all()

                calculated_hours = sum([hours[0] for hours in total_hours])

                workload = TeacherWorkload(
                    teacher_id=teacher.id,
                    academic_year=self.academic_year,
                    total_weekly_hours=calculated_hours,
                    max_allowed_hours=40,  # Standard Venezuelan limit
                    calculated_hours=calculated_hours,
                    mppe_hours_requirement=20  # Ministry minimum
                )

                workload.validate_workload()
                session.add(workload)
                created_count += 1

                # Update teacher's current hours
                teacher.current_weekly_hours = calculated_hours

            session.commit()
            logger.info(f"Created {created_count} teacher workload records")
            return created_count

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create teacher workload records: {str(e)}")
            return 0
        finally:
            session.close()

    def import_complete_dataset(self, migration_data_path: str) -> Dict[str, int]:
        """
        Import complete Venezuelan education dataset from Phase 0 migration

        Args:
            migration_data_path: Path to migration_workspace/extracted_data/

        Returns:
            Dict with import counts for each data type
        """
        results = {}

        logger.info(f"Starting complete dataset import for academic year {self.academic_year}")

        # Initialize database
        if not self.initialize_tenant_database():
            return {"error": "Failed to initialize database"}

        # Import in dependency order
        results['time_periods'] = self.import_time_periods(f"{migration_data_path}/time_periods.txt")
        results['classrooms'] = self.import_classrooms(f"{migration_data_path}/classrooms.txt")
        results['sections'] = self.import_sections(f"{migration_data_path}/sections.txt")
        results['subjects'] = self.import_subjects(f"{migration_data_path}/subjects.txt")
        results['teachers'] = self.import_teachers(f"{migration_data_path}/teachers.txt")

        # Create enhanced relationships
        results['teacher_subjects'] = self.create_enhanced_teacher_subject_relationships()
        results['teacher_workloads'] = self.create_teacher_workload_records()

        logger.info("Complete dataset import finished")
        logger.info(f"Import results: {results}")

        return results

    def get_import_summary(self) -> Dict[str, any]:
        """Get summary of imported data"""
        session = self.SessionLocal()

        try:
            summary = {
                'academic_year': self.academic_year,
                'time_periods': session.query(TimePeriod).count(),
                'classrooms': session.query(Classroom).count(),
                'sections': session.query(Section).count(),
                'subjects': session.query(Subject).count(),
                'teachers': session.query(Teacher).count(),
                'teacher_subjects': session.query(TeacherSubject).count(),
                'teacher_workloads': session.query(TeacherWorkload).count(),
                'import_timestamp': datetime.now(timezone.utc).isoformat()
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to get import summary: {str(e)}")
            return {'error': str(e)}
        finally:
            session.close()