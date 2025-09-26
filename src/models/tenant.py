"""
BiScheduler Tenant-Specific Database Models
Enhanced Core Database Schema for Venezuelan K12 Scheduling
Based on real 2025-2026 schedule analysis
"""

from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Time, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR, DECIMAL

Base = declarative_base()


class DayOfWeek(Enum):
    """Days of the week for Venezuelan schedule"""
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"


class EducationalLevel(Enum):
    """Venezuelan educational levels"""
    PREESCOLAR = "preescolar"
    PRIMARIA = "primaria"
    BACHILLERATO = "bachillerato"


class SubjectCategory(Enum):
    """Subject categories for Venezuelan curriculum"""
    MATHEMATICS = "mathematics"
    LANGUAGE = "language"
    SCIENCE = "science"
    SOCIAL_STUDIES = "social_studies"
    SPORTS = "sports"
    ARTS = "arts"
    TECHNOLOGY = "technology"
    GENERAL = "general"


class RoomType(Enum):
    """Classroom types"""
    REGULAR = "regular"
    LABORATORY = "laboratory"
    SPORTS = "sports"
    LIBRARY = "library"
    AUDITORIUM = "auditorium"
    COMPUTER_LAB = "computer_lab"


# ============================================================================
# INFRASTRUCTURE MODELS
# ============================================================================

class TimePeriod(Base):
    """
    Time periods for Venezuelan bimodal schedule (7:00-14:20)
    Enhanced from Phase 0 migration data
    """
    __tablename__ = 'time_periods'

    id = Column(Integer, primary_key=True)
    period_name = Column(String(50), nullable=False)  # P1, P2, REC1, etc.
    start_time = Column(Time, nullable=False)  # 07:00:00
    end_time = Column(Time, nullable=False)    # 07:40:00
    is_break = Column(Boolean, default=False)  # True for REC1, REC2
    schedule_type = Column(String(20), default='bimodal')
    display_order = Column(Integer, nullable=False)
    academic_year = Column(String(10), nullable=False)  # "2025-2026"
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f'<TimePeriod {self.period_name} ({self.start_time}-{self.end_time})>'

    @property
    def duration_minutes(self):
        """Calculate period duration in minutes"""
        if self.start_time and self.end_time:
            start = datetime.combine(datetime.today(), self.start_time)
            end = datetime.combine(datetime.today(), self.end_time)
            return int((end - start).total_seconds() / 60)
        return 0


class Classroom(Base):
    """
    Classroom infrastructure with Venezuelan context
    Enhanced from Phase 0 migration
    """
    __tablename__ = 'classrooms'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer)  # Reference to migrated data
    name = Column(String(100), nullable=False)  # "Aula 1", "Cancha 1"
    capacity = Column(Integer, default=35)  # Standard Venezuelan class size
    room_type = Column(SQLEnum(RoomType), default=RoomType.REGULAR)
    location = Column(String(200))  # Building/floor location
    equipment = Column(Text)  # Available equipment description
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Classroom {self.name} (cap: {self.capacity})>'


class Section(Base):
    """
    Grade sections for Venezuelan K12 structure
    Enhanced from Phase 0 migration
    """
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer)  # Reference to migrated data
    name = Column(String(50), nullable=False)  # "1er año", "3er año A"
    grade_level = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5
    section_letter = Column(String(5))  # A, B, or U (unique)
    educational_level = Column(SQLEnum(EducationalLevel), default=EducationalLevel.BACHILLERATO)
    max_students = Column(Integer, default=35)
    current_students = Column(Integer, default=0)
    academic_year = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Section {self.name} (Level {self.grade_level})>'

    @property
    def full_name(self):
        """Get formatted section name"""
        if self.section_letter and self.section_letter != 'U':
            return f"{self.grade_level}° año {self.section_letter}"
        return f"{self.grade_level}° año"


# ============================================================================
# ACADEMIC MODELS
# ============================================================================

class Subject(Base):
    """
    Venezuelan curriculum subjects
    Enhanced from Phase 0 migration with real subject data
    """
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer)  # Reference to migrated data
    subject_name = Column(String(200), nullable=False)  # "MATEMÁTICAS", "CASTELLANO Y LITERATURA"
    short_name = Column(String(50))  # "MATEMÁTICA", "CASTELLANO"
    curriculum_level = Column(SQLEnum(EducationalLevel), default=EducationalLevel.BACHILLERATO)
    subject_category = Column(SQLEnum(SubjectCategory), default=SubjectCategory.GENERAL)
    is_core_subject = Column(Boolean, default=False)  # Required subjects
    weekly_hours_default = Column(Integer, default=3)  # Default weekly hours

    # Venezuelan curriculum context
    mppe_code = Column(String(20))  # Ministry of Education code
    curriculum_area = Column(String(100))  # Curriculum area classification
    is_elective = Column(Boolean, default=False)

    # Prerequisites and relationships
    prerequisite_subjects = Column(Text)  # JSON array of prerequisite subject IDs
    academic_year = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Subject {self.subject_name} ({self.curriculum_level.value})>'


class Teacher(Base):
    """
    Venezuelan K12 teachers with specializations
    Enhanced from Phase 0 migration
    """
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer)  # Reference to migrated data
    teacher_name = Column(String(255), nullable=False)  # "MARIA NIETO"
    first_name = Column(String(100))
    last_name = Column(String(155))

    # Venezuelan identification
    cedula = Column(String(20), unique=True)  # Venezuelan ID number
    professional_id = Column(String(50))  # Professional registration

    # Professional information
    area_specialization = Column(String(100))  # "bachillerato", "primaria"
    education_level = Column(String(100))  # Education background
    years_experience = Column(Integer)

    # Contact information
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)

    # Employment details
    hire_date = Column(DateTime)
    employment_type = Column(String(50), default='full_time')  # full_time, part_time, substitute
    max_weekly_hours = Column(Integer, default=40)  # Maximum allowed hours
    current_weekly_hours = Column(Integer, default=0)  # Calculated from assignments

    # Platform access
    user_id = Column(String(100))  # Reference to authentication system
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    academic_year = Column(String(10), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Teacher {self.teacher_name} ({self.area_specialization})>'

    @property
    def weekly_hours_available(self):
        """Calculate available weekly hours"""
        return max(0, self.max_weekly_hours - self.current_weekly_hours)


# ============================================================================
# ENHANCED RELATIONSHIP MODELS (Phase 2 Enhancements)
# ============================================================================

class TeacherSubject(Base):
    """
    Enhanced Teacher-Subject relationship with hour tracking
    Critical enhancement from K12 schedule analysis
    """
    __tablename__ = 'teacher_subjects'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)

    # Hour allocation per subject (Key enhancement)
    weekly_hours = Column(Integer, nullable=False)  # Hours per week for this subject
    is_primary_subject = Column(Boolean, default=False)  # Main specialization
    competency_level = Column(String(20), default='expert')  # expert, qualified, substitute

    # Administrative
    academic_year = Column(String(10), nullable=False)
    assigned_date = Column(DateTime, default=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    teacher = relationship("Teacher", backref="teacher_subjects")
    subject = relationship("Subject", backref="subject_teachers")

    def __repr__(self):
        return f'<TeacherSubject {self.teacher.teacher_name} -> {self.subject.subject_name} ({self.weekly_hours}h)>'


class TeacherWorkload(Base):
    """
    Teacher workload validation and tracking
    Critical enhancement for Venezuelan compliance
    """
    __tablename__ = 'teacher_workload'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    academic_year = Column(String(10), nullable=False)

    # Hour tracking
    total_weekly_hours = Column(Integer, default=0)  # Total assigned hours
    max_allowed_hours = Column(Integer, default=40)  # Legal/contract limit
    calculated_hours = Column(Integer, default=0)  # Auto-calculated from schedule

    # Venezuelan compliance
    mppe_hours_requirement = Column(Integer, default=20)  # Ministry requirement
    overtime_hours = Column(Integer, default=0)

    # Validation status
    is_valid = Column(Boolean, default=True)
    validation_notes = Column(Text)
    last_calculated = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    teacher = relationship("Teacher", backref="workload_records")

    def __repr__(self):
        return f'<TeacherWorkload {self.teacher.teacher_name} ({self.total_weekly_hours}h)>'

    def validate_workload(self):
        """Validate teacher workload against limits"""
        self.is_valid = self.calculated_hours <= self.max_allowed_hours
        self.overtime_hours = max(0, self.calculated_hours - self.max_allowed_hours)
        self.last_calculated = datetime.now(timezone.utc)


# ============================================================================
# CORE SCHEDULING MODEL (Enhanced)
# ============================================================================

class ScheduleAssignment(Base):
    """
    Core schedule assignment with classroom tracking
    Enhanced with critical classroom assignment from K12 analysis
    """
    __tablename__ = 'schedule_assignments'

    id = Column(Integer, primary_key=True)

    # Core scheduling components
    time_period_id = Column(Integer, ForeignKey('time_periods.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)  # CRITICAL ENHANCEMENT

    # Schedule timing
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=False)
    academic_year = Column(String(10), nullable=False)
    effective_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime)  # For schedule changes

    # Assignment metadata
    assignment_type = Column(String(20), default='regular')  # regular, substitute, makeup
    priority = Column(Integer, default=1)  # For conflict resolution
    notes = Column(Text)  # Special instructions

    # Validation and status
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)  # Prevent changes
    conflict_status = Column(String(20), default='none')  # none, warning, error

    # Audit trail
    created_by = Column(String(100))  # User who created assignment
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    time_period = relationship("TimePeriod", backref="assignments")
    teacher = relationship("Teacher", backref="schedule_assignments")
    subject = relationship("Subject", backref="schedule_assignments")
    section = relationship("Section", backref="schedule_assignments")
    classroom = relationship("Classroom", backref="schedule_assignments")

    def __repr__(self):
        return f'<ScheduleAssignment {self.subject.subject_name} - {self.teacher.teacher_name} ({self.day_of_week.value})>'

    @property
    def display_time(self):
        """Get formatted time display"""
        return f"{self.time_period.start_time.strftime('%H:%M')} - {self.time_period.end_time.strftime('%H:%M')}"

    @property
    def schedule_cell_content(self):
        """Get formatted content for schedule cell (Venezuelan format)"""
        return {
            'subject': self.subject.subject_name,
            'teacher': self.teacher.teacher_name,
            'classroom': f"({self.classroom.name})",
            'section': self.section.name,
            'time': self.display_time
        }


# ============================================================================
# CONFLICT DETECTION MODEL
# ============================================================================

class ScheduleConflict(Base):
    """
    Automatic conflict detection and resolution
    Essential for Venezuelan schedule management
    """
    __tablename__ = 'schedule_conflicts'

    id = Column(Integer, primary_key=True)
    conflict_type = Column(String(50), nullable=False)  # teacher_double_booking, classroom_conflict, etc.
    severity = Column(String(20), default='warning')  # info, warning, error, critical

    # Conflicting assignments
    assignment_1_id = Column(Integer, ForeignKey('schedule_assignments.id'))
    assignment_2_id = Column(Integer, ForeignKey('schedule_assignments.id'))

    # Conflict details
    description = Column(Text, nullable=False)
    suggested_resolution = Column(Text)
    auto_resolvable = Column(Boolean, default=False)

    # Status tracking
    status = Column(String(20), default='active')  # active, resolved, ignored
    resolved_by = Column(String(100))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)

    # Metadata
    detected_at = Column(DateTime, default=datetime.now(timezone.utc))
    academic_year = Column(String(10), nullable=False)

    # Relationships
    assignment_1 = relationship("ScheduleAssignment", foreign_keys=[assignment_1_id])
    assignment_2 = relationship("ScheduleAssignment", foreign_keys=[assignment_2_id])

    def __repr__(self):
        return f'<ScheduleConflict {self.conflict_type} ({self.severity})>'