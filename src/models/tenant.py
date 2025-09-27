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

class Schedule(Base):
    """
    Schedule container for organizing assignments by academic period
    """
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    academic_year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    status = Column(String(20), default='draft')  # draft, active, archived
    created_by = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    meta_data = Column(Text)  # JSON string for additional data

    # Relationships
    assignments = relationship("ScheduleAssignment", back_populates="schedule")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'academic_year': self.academic_year,
            'semester': self.semester,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.meta_data
        }


class ScheduleAssignment(Base):
    """
    Core schedule assignment with classroom tracking
    Enhanced with critical classroom assignment from K12 analysis
    """
    __tablename__ = 'schedule_assignments'

    id = Column(Integer, primary_key=True)

    # Link to parent schedule
    schedule_id = Column(Integer, ForeignKey('schedules.id'), nullable=True)
    tenant_id = Column(Integer, nullable=False)

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
    schedule = relationship("Schedule", back_populates="assignments")
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


# ============================================================================
# PHASE 6: TEACHER SELF-SERVICE PORTAL MODELS
# ============================================================================

class PreferenceType(Enum):
    """Types of teacher preferences"""
    TIME_SLOT = "time_slot"        # Prefer specific time periods
    DAY_OF_WEEK = "day_of_week"    # Prefer specific days
    SUBJECT = "subject"            # Prefer specific subjects
    CLASSROOM = "classroom"        # Prefer specific classrooms
    SECTION = "section"            # Prefer specific grade sections


class PreferenceLevel(Enum):
    """Preference intensity levels"""
    AVOID = "avoid"          # Never assign (weight: -10)
    DISLIKE = "dislike"      # Try to avoid (weight: -5)
    NEUTRAL = "neutral"      # No preference (weight: 0)
    LIKE = "like"           # Prefer this option (weight: +5)
    PREFER = "prefer"       # Strong preference (weight: +10)


class TeacherPreference(Base):
    """
    Teacher preferences for schedule optimization
    Phase 6: Teacher Self-Service Portal
    Scoring: 40% time, 30% day, 20% subject, 10% classroom
    """
    __tablename__ = 'teacher_preferences'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)

    # Preference details
    preference_type = Column(SQLEnum(PreferenceType), nullable=False)
    preference_level = Column(SQLEnum(PreferenceLevel), nullable=False)

    # Target references (one will be set based on preference_type)
    time_period_id = Column(Integer, ForeignKey('time_periods.id'), nullable=True)
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=True)
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=True)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=True)

    # Preference context
    reason = Column(Text)  # Optional explanation from teacher
    priority_score = Column(Integer, default=0)  # Calculated preference weight

    # Validity period
    effective_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime)  # Optional expiration
    academic_year = Column(String(10), nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)  # Admin approval required
    approved_by = Column(String(100))
    approved_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    teacher = relationship("Teacher", backref="preferences")
    time_period = relationship("TimePeriod", backref="teacher_preferences")
    subject = relationship("Subject", backref="teacher_preferences")
    classroom = relationship("Classroom", backref="teacher_preferences")
    section = relationship("Section", backref="teacher_preferences")

    def __repr__(self):
        return f'<TeacherPreference {self.teacher.teacher_name}: {self.preference_type.value} = {self.preference_level.value}>'

    @property
    def weight_score(self):
        """Calculate numerical weight for preference optimization"""
        weights = {
            PreferenceLevel.AVOID: -10,
            PreferenceLevel.DISLIKE: -5,
            PreferenceLevel.NEUTRAL: 0,
            PreferenceLevel.LIKE: 5,
            PreferenceLevel.PREFER: 10
        }
        return weights.get(self.preference_level, 0)

    @property
    def type_multiplier(self):
        """Get type-based multiplier for scoring algorithm"""
        multipliers = {
            PreferenceType.TIME_SLOT: 0.40,  # 40% weight
            PreferenceType.DAY_OF_WEEK: 0.30,  # 30% weight
            PreferenceType.SUBJECT: 0.20,     # 20% weight
            PreferenceType.CLASSROOM: 0.10,   # 10% weight
            PreferenceType.SECTION: 0.05      # 5% weight
        }
        return multipliers.get(self.preference_type, 0.0)

    @property
    def final_score(self):
        """Calculate final weighted score for optimization"""
        return self.weight_score * self.type_multiplier


class TeacherAvailability(Base):
    """
    Teacher availability and constraints
    Phase 6: Advanced scheduling features
    """
    __tablename__ = 'teacher_availability'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)

    # Time constraints
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)  # Available from
    end_time = Column(Time, nullable=False)    # Available until

    # Availability type
    availability_type = Column(String(20), default='available')  # available, unavailable, preferred
    reason = Column(String(200))  # Medical, personal, training, etc.

    # Validity period
    effective_date = Column(DateTime, default=datetime.now(timezone.utc))
    end_date = Column(DateTime)
    academic_year = Column(String(10), nullable=False)

    # Recurring pattern
    is_recurring = Column(Boolean, default=True)  # Weekly recurring
    specific_dates = Column(Text)  # JSON array for specific dates

    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String(100))

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    teacher = relationship("Teacher", backref="availability_periods")

    def __repr__(self):
        return f'<TeacherAvailability {self.teacher.teacher_name}: {self.day_of_week.value} {self.start_time}-{self.end_time}>'


class ScheduleChangeRequest(Base):
    """
    Teacher-initiated schedule change requests
    Phase 6: Teacher self-service functionality
    """
    __tablename__ = 'schedule_change_requests'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    assignment_id = Column(Integer, ForeignKey('schedule_assignments.id'), nullable=False)

    # Change request details
    request_type = Column(String(30), nullable=False)  # time_change, substitute_request, swap_request
    requested_change = Column(Text, nullable=False)  # Description of requested change
    justification = Column(Text, nullable=False)  # Why change is needed

    # Proposed alternative (for swaps/changes)
    proposed_time_period_id = Column(Integer, ForeignKey('time_periods.id'))
    proposed_day_of_week = Column(SQLEnum(DayOfWeek))
    proposed_classroom_id = Column(Integer, ForeignKey('classrooms.id'))
    swap_with_teacher_id = Column(Integer, ForeignKey('teachers.id'))

    # Request status
    status = Column(String(20), default='pending')  # pending, approved, denied, cancelled
    priority = Column(String(20), default='normal')  # low, normal, high, urgent

    # Processing
    reviewed_by = Column(String(100))  # Admin who reviewed
    reviewed_at = Column(DateTime)
    response_message = Column(Text)
    approved_at = Column(DateTime)
    implemented_at = Column(DateTime)

    # Validity
    requested_date = Column(DateTime, nullable=False)  # When change should take effect
    expiration_date = Column(DateTime)  # When request expires
    academic_year = Column(String(10), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    teacher = relationship("Teacher", backref="change_requests")
    assignment = relationship("ScheduleAssignment", backref="change_requests")
    proposed_time_period = relationship("TimePeriod", backref="change_requests")
    proposed_classroom = relationship("Classroom", backref="change_requests")
    swap_with_teacher = relationship("Teacher", foreign_keys=[swap_with_teacher_id], backref="incoming_swap_requests")

    def __repr__(self):
        return f'<ScheduleChangeRequest {self.teacher.teacher_name}: {self.request_type} ({self.status})>'


class TeacherDashboardStats(Base):
    """
    Teacher dashboard statistics and metrics
    Phase 6: Teacher portal analytics
    """
    __tablename__ = 'teacher_dashboard_stats'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    academic_year = Column(String(10), nullable=False)

    # Weekly statistics
    total_weekly_hours = Column(Integer, default=0)
    total_classes = Column(Integer, default=0)
    total_subjects = Column(Integer, default=0)
    total_sections = Column(Integer, default=0)

    # Preference satisfaction metrics
    preference_satisfaction_score = Column(DECIMAL(5,2), default=0.0)  # 0-100%
    time_preference_score = Column(DECIMAL(5,2), default=0.0)
    day_preference_score = Column(DECIMAL(5,2), default=0.0)
    subject_preference_score = Column(DECIMAL(5,2), default=0.0)
    classroom_preference_score = Column(DECIMAL(5,2), default=0.0)

    # Change request history
    total_change_requests = Column(Integer, default=0)
    approved_change_requests = Column(Integer, default=0)
    pending_change_requests = Column(Integer, default=0)

    # Workload metrics
    workload_balance_score = Column(DECIMAL(5,2), default=0.0)  # Even distribution across week
    consecutive_classes_max = Column(Integer, default=0)  # Max consecutive periods
    free_periods_per_week = Column(Integer, default=0)

    # Update tracking
    last_calculated = Column(DateTime, default=datetime.now(timezone.utc))
    calculation_version = Column(String(10), default='1.0')

    # Relationships
    teacher = relationship("Teacher", backref="dashboard_stats")

    def __repr__(self):
        return f'<TeacherDashboardStats {self.teacher.teacher_name}: {self.total_weekly_hours}h, {self.preference_satisfaction_score}% satisfaction>'

    def calculate_overall_satisfaction(self):
        """Calculate overall preference satisfaction score"""
        scores = [
            self.time_preference_score * 0.40,      # 40% weight
            self.day_preference_score * 0.30,       # 30% weight
            self.subject_preference_score * 0.20,   # 20% weight
            self.classroom_preference_score * 0.10  # 10% weight
        ]
        self.preference_satisfaction_score = sum(scores)
        return self.preference_satisfaction_score


# ============================================================================
# PHASE 6: EXAM SCHEDULING SYSTEM
# ============================================================================

class ExamType(Enum):
    """Venezuelan K12 exam types"""
    PARCIAL = "parcial"                    # Mid-term exam
    FINAL = "final"                        # Final exam
    RECUPERACION = "recuperacion"          # Make-up exam
    EXTRAORDINARIO = "extraordinario"      # Extraordinary exam
    DIAGNOSTICO = "diagnostico"            # Diagnostic exam
    EVALUACION_CONTINUA = "evaluacion_continua"  # Continuous assessment


class ExamStatus(Enum):
    """Exam scheduling status"""
    DRAFT = "draft"                        # Being planned
    SCHEDULED = "scheduled"                # Scheduled but not confirmed
    CONFIRMED = "confirmed"                # Confirmed and locked
    IN_PROGRESS = "in_progress"           # Currently taking place
    COMPLETED = "completed"                # Finished
    CANCELLED = "cancelled"                # Cancelled
    POSTPONED = "postponed"                # Postponed to later date


class SupervisorRole(Enum):
    """Exam supervisor roles"""
    PRIMARY = "primary"                    # Main supervisor
    SECONDARY = "secondary"                # Assistant supervisor
    OBSERVER = "observer"                  # Quality observer
    SUBSTITUTE = "substitute"              # Backup supervisor


class Exam(Base):
    """
    Venezuelan K12 Exam Scheduling
    Phase 6: Comprehensive exam management system
    """
    __tablename__ = 'exams'

    id = Column(Integer, primary_key=True)

    # Basic exam information
    exam_name = Column(String(200), nullable=False)  # "Parcial I - Matemáticas"
    exam_type = Column(SQLEnum(ExamType), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)

    # Scheduling details
    exam_date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # Expected duration

    # Location
    classroom_id = Column(Integer, ForeignKey('classrooms.id'), nullable=False)
    backup_classroom_id = Column(Integer, ForeignKey('classrooms.id'))  # In case of conflicts

    # Capacity and students
    max_students = Column(Integer, nullable=False)
    enrolled_students = Column(Integer, default=0)
    students_list = Column(Text)  # JSON array of student IDs

    # Instructions and content
    exam_instructions = Column(Text)
    materials_allowed = Column(Text)  # "Calculadora, regla, lápiz"
    materials_forbidden = Column(Text)  # "Teléfonos, libros"

    # Status and workflow
    status = Column(SQLEnum(ExamStatus), default=ExamStatus.DRAFT)
    is_published = Column(Boolean, default=False)  # Visible to students
    requires_supervisor = Column(Boolean, default=True)

    # Academic context
    academic_year = Column(String(10), nullable=False)
    academic_period = Column(String(50))  # "Primer Lapso", "Segundo Lapso"
    weight_percentage = Column(DECIMAL(5,2))  # Exam weight in final grade

    # Scheduling constraints
    min_preparation_days = Column(Integer, default=7)  # Notice period
    max_daily_exams_per_student = Column(Integer, default=2)
    min_break_between_exams = Column(Integer, default=60)  # Minutes

    # Publishing and notifications
    published_date = Column(DateTime)
    notification_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)

    # Results tracking
    graded = Column(Boolean, default=False)
    results_published = Column(Boolean, default=False)
    average_score = Column(DECIMAL(5,2))
    pass_rate = Column(DECIMAL(5,2))

    # Metadata
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    subject = relationship("Subject", backref="exams")
    section = relationship("Section", backref="exams")
    classroom = relationship("Classroom", foreign_keys=[classroom_id], backref="hosted_exams")
    backup_classroom = relationship("Classroom", foreign_keys=[backup_classroom_id], backref="backup_exams")

    def __repr__(self):
        return f'<Exam {self.exam_name} - {self.section.name} ({self.exam_date.strftime("%Y-%m-%d")})>'

    @property
    def exam_duration_formatted(self):
        """Get formatted exam duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"

    @property
    def time_slot_display(self):
        """Get formatted time slot for display"""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class ExamSupervisor(Base):
    """
    Exam supervision assignments
    Venezuelan K12 compliance requirements
    """
    __tablename__ = 'exam_supervisors'

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)

    # Supervisor details
    supervisor_role = Column(SQLEnum(SupervisorRole), default=SupervisorRole.PRIMARY)
    is_confirmed = Column(Boolean, default=False)
    confirmation_date = Column(DateTime)

    # Scheduling
    arrival_time = Column(Time)  # When supervisor should arrive
    departure_time = Column(Time)  # When supervisor can leave

    # Responsibilities
    responsibilities = Column(Text)  # Specific duties for this exam
    has_subject_expertise = Column(Boolean, default=False)  # Can answer subject questions

    # Payment and tracking
    supervision_hours = Column(DECIMAL(4,2))  # Hours worked
    hourly_rate = Column(DECIMAL(8,2))  # Payment rate
    total_payment = Column(DECIMAL(10,2))  # Calculated payment

    # Status
    attendance_status = Column(String(20), default='assigned')  # assigned, present, absent, substitute
    substitute_assigned = Column(Boolean, default=False)
    notes = Column(Text)  # Supervision notes

    # Metadata
    assigned_by = Column(String(100))
    assigned_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    exam = relationship("Exam", backref="supervisors")
    teacher = relationship("Teacher", backref="exam_supervisions")

    def __repr__(self):
        return f'<ExamSupervisor {self.teacher.teacher_name} -> {self.exam.exam_name} ({self.supervisor_role.value})>'


class ExamConflict(Base):
    """
    Exam scheduling conflict detection and resolution
    Critical for Venezuelan schedule compliance
    """
    __tablename__ = 'exam_conflicts'

    id = Column(Integer, primary_key=True)

    # Conflict type and severity
    conflict_type = Column(String(50), nullable=False)  # student_double_booking, room_conflict, supervisor_conflict
    severity = Column(String(20), default='warning')  # info, warning, error, critical

    # Conflicting exams
    exam_1_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    exam_2_id = Column(Integer, ForeignKey('exams.id'))  # Null for single-exam issues

    # Conflict details
    description = Column(Text, nullable=False)
    affected_students = Column(Text)  # JSON array of student IDs
    affected_resources = Column(Text)  # Rooms, supervisors, etc.

    # Resolution
    suggested_resolution = Column(Text)
    auto_resolvable = Column(Boolean, default=False)
    resolution_priority = Column(Integer, default=3)  # 1=urgent, 5=low

    # Status tracking
    status = Column(String(20), default='active')  # active, resolved, ignored
    resolved_by = Column(String(100))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)

    # Impact assessment
    students_affected_count = Column(Integer, default=0)
    teachers_affected_count = Column(Integer, default=0)
    classrooms_affected_count = Column(Integer, default=0)

    # Metadata
    detected_at = Column(DateTime, default=datetime.now(timezone.utc))
    academic_year = Column(String(10), nullable=False)

    # Relationships
    exam_1 = relationship("Exam", foreign_keys=[exam_1_id], backref="conflicts_as_primary")
    exam_2 = relationship("Exam", foreign_keys=[exam_2_id], backref="conflicts_as_secondary")

    def __repr__(self):
        return f'<ExamConflict {self.conflict_type} ({self.severity}) - {self.students_affected_count} students>'


class StudentExamSchedule(Base):
    """
    Individual student exam schedules with alerts
    Phase 6: Student exam dashboard support
    """
    __tablename__ = 'student_exam_schedules'

    id = Column(Integer, primary_key=True)

    # Student identification (using cedula since we don't have full student model)
    student_cedula = Column(String(20), nullable=False)
    student_name = Column(String(200), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)

    # Exam assignment
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    is_enrolled = Column(Boolean, default=True)
    enrollment_date = Column(DateTime, default=datetime.now(timezone.utc))

    # Special accommodations
    needs_accommodation = Column(Boolean, default=False)
    accommodation_type = Column(String(100))  # "Extra time", "Special room", etc.
    accommodation_details = Column(Text)

    # Preparation tracking
    notification_received = Column(Boolean, default=False)
    notification_date = Column(DateTime)
    preparation_materials_accessed = Column(Boolean, default=False)

    # Exam participation
    attendance_status = Column(String(20), default='enrolled')  # enrolled, present, absent, excused
    start_time_actual = Column(DateTime)  # When student actually started
    submission_time = Column(DateTime)  # When student finished

    # Results (basic tracking)
    exam_completed = Column(Boolean, default=False)
    score = Column(DECIMAL(5,2))  # Exam score
    grade_letter = Column(String(5))  # A, B, C, etc.
    passed = Column(Boolean)

    # Academic year
    academic_year = Column(String(10), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    exam = relationship("Exam", backref="student_schedules")
    section = relationship("Section", backref="student_exam_schedules")

    def __repr__(self):
        return f'<StudentExamSchedule {self.student_name} -> {self.exam.exam_name}>'

    @property
    def days_until_exam(self):
        """Calculate days until exam"""
        if self.exam.exam_date:
            delta = self.exam.exam_date.date() - datetime.now().date()
            return delta.days
        return None


class ExamCalendarEvent(Base):
    """
    Calendar view support for exam scheduling
    Phase 6: Calendar integration
    """
    __tablename__ = 'exam_calendar_events'

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)

    # Calendar event details
    event_title = Column(String(200), nullable=False)
    event_description = Column(Text)
    event_type = Column(String(30), default='exam')  # exam, preparation, review

    # Date and time
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False)

    # Display properties
    color_code = Column(String(10), default='#007bff')  # Hex color for calendar
    is_visible = Column(Boolean, default=True)
    display_priority = Column(Integer, default=1)

    # Recurrence (for recurring events)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # weekly, biweekly, etc.
    recurrence_end_date = Column(DateTime)

    # Reminders
    reminder_enabled = Column(Boolean, default=True)
    reminder_minutes_before = Column(Integer, default=1440)  # 24 hours default
    reminder_sent = Column(Boolean, default=False)

    # Attendees
    target_audience = Column(String(100))  # students, teachers, supervisors, all
    mandatory_attendance = Column(Boolean, default=True)

    # Metadata
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    exam = relationship("Exam", backref="calendar_events")

    def __repr__(self):
        return f'<ExamCalendarEvent {self.event_title} ({self.start_datetime.strftime("%Y-%m-%d %H:%M")})>'