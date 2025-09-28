"""
Unit tests for BiScheduler database models.
Tests Venezuelan K12 specific models and relationships.
"""

import pytest
from datetime import datetime, time
from src.models.tenant import (
    Teacher, Student, Subject, Section, Classroom, TimePeriod,
    ScheduleAssignment, TeacherWorkload, DayOfWeek, EducationalLevel,
    ConflictType, ScheduleConflict
)
from src.models.master import Tenant, TenantStatus


class TestTenantModels:
    """Test multi-tenant models."""

    @pytest.mark.unit
    @pytest.mark.database
    def test_tenant_creation(self, db_session):
        """Test creating a new tenant."""
        tenant = Tenant(
            domain='nueva.escuela.edu.ve',
            name='Nueva Escuela Bolivariana',
            database_name='nueva_escuela_db',
            status=TenantStatus.ACTIVE,
            institution_type='K12',
            region='Miranda'
        )
        db_session.add(tenant)
        db_session.commit()

        assert tenant.id is not None
        assert tenant.domain == 'nueva.escuela.edu.ve'
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.institution_type == 'K12'

    @pytest.mark.unit
    def test_tenant_status_enum(self):
        """Test TenantStatus enum values."""
        assert TenantStatus.PENDING.value == 'pending'
        assert TenantStatus.ACTIVE.value == 'active'
        assert TenantStatus.SUSPENDED.value == 'suspended'
        assert TenantStatus.TERMINATED.value == 'terminated'


class TestVenezuelanEducationModels:
    """Test Venezuelan K12 specific models."""

    @pytest.mark.unit
    @pytest.mark.database
    @pytest.mark.venezuelan
    def test_teacher_model(self, db_session):
        """Test Teacher model with Venezuelan attributes."""
        teacher = Teacher(
            first_name='Roberto',
            last_name='Quijada',
            email='rquijada@ueipab.edu.ve',
            employee_id='T003',
            specialization='Matemáticas y Lógica',
            cedula='V-15678902',
            phone='+58-212-1234567'
        )
        db_session.add(teacher)
        db_session.commit()

        assert teacher.id is not None
        assert teacher.cedula == 'V-15678902'
        assert teacher.specialization == 'Matemáticas y Lógica'
        assert teacher.full_name == 'Roberto Quijada'

    @pytest.mark.unit
    @pytest.mark.database
    @pytest.mark.venezuelan
    def test_student_model(self, db_session):
        """Test Student model with Venezuelan compliance fields."""
        student = Student(
            first_name='Luis',
            last_name='Hernández',
            email='lhernandez@student.edu.ve',
            student_code='S003',
            cedula_escolar='V-20051234',
            gender='M',
            birth_date=datetime(2009, 3, 15),
            grade_level=3,
            enrollment_date=datetime(2025, 9, 1)
        )
        db_session.add(student)
        db_session.commit()

        assert student.id is not None
        assert student.cedula_escolar == 'V-20051234'
        assert student.gender == 'M'
        assert student.grade_level == 3
        assert student.age >= 15  # Born in 2009

    @pytest.mark.unit
    @pytest.mark.database
    @pytest.mark.venezuelan
    def test_subject_model(self, db_session):
        """Test Subject model with Venezuelan curriculum."""
        subject = Subject(
            name='GHC PARA LA SOBERANÍA NACIONAL',
            code='GHC',
            weekly_hours=3,
            educational_level=EducationalLevel.BACHILLERATO,
            is_mandatory=True
        )
        db_session.add(subject)
        db_session.commit()

        assert subject.id is not None
        assert subject.name == 'GHC PARA LA SOBERANÍA NACIONAL'
        assert subject.educational_level == EducationalLevel.BACHILLERATO
        assert subject.is_mandatory is True

    @pytest.mark.unit
    @pytest.mark.database
    def test_time_period_model(self, db_session):
        """Test TimePeriod model for Venezuelan bimodal schedule."""
        period = TimePeriod(
            period_number=7,
            start_time=time(10, 40),
            end_time=time(11, 20),
            is_break=False
        )
        db_session.add(period)
        db_session.commit()

        assert period.id is not None
        assert period.duration_minutes == 40
        assert str(period) == 'P7 (10:40-11:20)'


class TestScheduleModels:
    """Test schedule-related models."""

    @pytest.mark.unit
    @pytest.mark.database
    def test_schedule_assignment(self, db_session, sample_venezuelan_data):
        """Test creating schedule assignments."""
        teacher = sample_venezuelan_data['teachers'][0]
        subject = sample_venezuelan_data['subjects'][0]
        section = sample_venezuelan_data['sections'][0]
        classroom = sample_venezuelan_data['classrooms'][0]
        time_period = sample_venezuelan_data['time_periods'][0]

        assignment = ScheduleAssignment(
            teacher_id=teacher.id,
            subject_id=subject.id,
            section_id=section.id,
            classroom_id=classroom.id,
            time_period_id=time_period.id,
            day_of_week=DayOfWeek.LUNES,
            academic_year='2025-2026'
        )
        db_session.add(assignment)
        db_session.commit()

        assert assignment.id is not None
        assert assignment.day_of_week == DayOfWeek.LUNES
        assert assignment.academic_year == '2025-2026'

    @pytest.mark.unit
    @pytest.mark.database
    def test_teacher_workload(self, db_session, sample_venezuelan_data):
        """Test teacher workload tracking."""
        teacher = sample_venezuelan_data['teachers'][0]

        workload = TeacherWorkload(
            teacher_id=teacher.id,
            academic_year='2025-2026',
            total_weekly_hours=22,
            assigned_hours=18,
            max_daily_hours=6,
            preferred_hours=20
        )
        db_session.add(workload)
        db_session.commit()

        assert workload.id is not None
        assert workload.available_hours == 4  # 22 - 18
        assert workload.is_overloaded is False

    @pytest.mark.unit
    @pytest.mark.database
    def test_schedule_conflict(self, db_session, sample_venezuelan_data):
        """Test schedule conflict detection."""
        assignment = ScheduleAssignment(
            teacher_id=sample_venezuelan_data['teachers'][0].id,
            subject_id=sample_venezuelan_data['subjects'][0].id,
            section_id=sample_venezuelan_data['sections'][0].id,
            classroom_id=sample_venezuelan_data['classrooms'][0].id,
            time_period_id=sample_venezuelan_data['time_periods'][0].id,
            day_of_week=DayOfWeek.MARTES,
            academic_year='2025-2026'
        )
        db_session.add(assignment)
        db_session.commit()

        conflict = ScheduleConflict(
            assignment_id=assignment.id,
            conflict_type=ConflictType.TEACHER_DOUBLE_BOOKING,
            conflicting_assignment_id=assignment.id,
            description='Teacher assigned to multiple classes at same time',
            severity='HIGH'
        )
        db_session.add(conflict)
        db_session.commit()

        assert conflict.id is not None
        assert conflict.conflict_type == ConflictType.TEACHER_DOUBLE_BOOKING
        assert conflict.severity == 'HIGH'
        assert conflict.resolved is False


class TestRelationships:
    """Test model relationships."""

    @pytest.mark.unit
    @pytest.mark.database
    def test_teacher_subject_relationship(self, db_session, sample_venezuelan_data):
        """Test many-to-many relationship between teachers and subjects."""
        teacher = sample_venezuelan_data['teachers'][0]
        math_subject = sample_venezuelan_data['subjects'][0]
        bio_subject = sample_venezuelan_data['subjects'][2]

        teacher.subjects.append(math_subject)
        teacher.subjects.append(bio_subject)
        db_session.commit()

        assert len(teacher.subjects) == 2
        assert math_subject in teacher.subjects
        assert bio_subject in teacher.subjects

    @pytest.mark.unit
    @pytest.mark.database
    def test_section_student_relationship(self, db_session, sample_venezuelan_data):
        """Test section-student relationships."""
        section = sample_venezuelan_data['sections'][0]
        students = sample_venezuelan_data['students']

        for student in students:
            student.section_id = section.id

        db_session.commit()

        assert len(section.students) == 2
        assert students[0].section == section
        assert students[1].section == section

    @pytest.mark.unit
    @pytest.mark.database
    def test_cascade_deletion(self, db_session, sample_venezuelan_data):
        """Test cascade deletion behavior."""
        teacher = sample_venezuelan_data['teachers'][0]
        teacher_id = teacher.id

        # Create workload for teacher
        workload = TeacherWorkload(
            teacher_id=teacher_id,
            academic_year='2025-2026',
            total_weekly_hours=20
        )
        db_session.add(workload)
        db_session.commit()

        # Delete teacher and check cascade
        db_session.delete(teacher)
        db_session.commit()

        assert db_session.query(Teacher).filter_by(id=teacher_id).first() is None
        assert db_session.query(TeacherWorkload).filter_by(teacher_id=teacher_id).first() is None