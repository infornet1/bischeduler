"""
Pytest configuration and fixtures for BiScheduler testing suite.
Provides common fixtures for unit, integration, and e2e tests.
"""

import os
import sys
import pytest
from datetime import datetime, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask_jwt_extended import create_access_token

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.app import create_app, db
from src.models.master import Tenant, TenantStatus
from src.models.tenant import (
    Teacher, Student, Classroom, Subject, Section, TimePeriod,
    ScheduleAssignment, TeacherWorkload, DayOfWeek, EducationalLevel,
    StudentGrade, DailyAttendance, User, UserRole
)


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')

    # Override test configuration
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'MASTER_DATABASE_URI': 'sqlite:///:memory:'
    })

    return app


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def test_tenant(db_session):
    """Create test tenant for multi-tenant testing."""
    tenant = Tenant(
        domain='test.ueipab.edu.ve',
        name='Test School',
        database_name='test_school_db',
        status=TenantStatus.ACTIVE,
        institution_type='K12',
        region='Caracas',
        created_at=datetime.utcnow()
    )
    db_session.add(tenant)
    db_session.commit()
    return tenant


@pytest.fixture(scope='function')
def auth_headers(app, test_user):
    """Create authentication headers for API testing."""
    with app.app_context():
        access_token = create_access_token(
            identity=str(test_user.id),
            additional_claims={
                'role': test_user.role.value,
                'tenant_id': test_user.tenant_id
            }
        )
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture(scope='function')
def test_user(db_session):
    """Create test user."""
    user = User(
        email='test@ueipab.edu.ve',
        username='testuser',
        first_name='Test',
        last_name='User',
        role=UserRole.TEACHER,
        is_active=True
    )
    user.set_password('testpass123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_admin(db_session):
    """Create test admin user."""
    admin = User(
        email='admin@ueipab.edu.ve',
        username='testadmin',
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN,
        is_active=True
    )
    admin.set_password('adminpass123')
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture(scope='function')
def sample_venezuelan_data(db_session):
    """Create sample Venezuelan K12 data for testing."""
    # Create time periods (Venezuelan bimodal schedule)
    time_periods = [
        TimePeriod(period_number=1, start_time=time(7, 0), end_time=time(7, 40), is_break=False),
        TimePeriod(period_number=2, start_time=time(7, 40), end_time=time(8, 20), is_break=False),
        TimePeriod(period_number=3, start_time=time(8, 20), end_time=time(9, 0), is_break=False),
        TimePeriod(period_number=4, start_time=time(9, 0), end_time=time(9, 40), is_break=False),
        TimePeriod(period_number=5, start_time=time(9, 40), end_time=time(10, 0), is_break=True),
        TimePeriod(period_number=6, start_time=time(10, 0), end_time=time(10, 40), is_break=False),
    ]

    # Create subjects (Venezuelan curriculum)
    subjects = [
        Subject(name='MATEMÁTICAS', code='MAT', weekly_hours=6, educational_level=EducationalLevel.BACHILLERATO),
        Subject(name='CASTELLANO Y LITERATURA', code='CAS', weekly_hours=4, educational_level=EducationalLevel.BACHILLERATO),
        Subject(name='BIOLOGÍA', code='BIO', weekly_hours=4, educational_level=EducationalLevel.BACHILLERATO),
        Subject(name='QUÍMICA', code='QUI', weekly_hours=4, educational_level=EducationalLevel.BACHILLERATO),
    ]

    # Create classrooms
    classrooms = [
        Classroom(name='Aula 1', code='A1', capacity=35, building='Principal', has_projector=True),
        Classroom(name='Aula 2', code='A2', capacity=30, building='Principal', has_projector=False),
        Classroom(name='Laboratorio', code='LAB', capacity=25, building='Ciencias', has_projector=True),
    ]

    # Create sections (Venezuelan grade levels)
    sections = [
        Section(name='1er Año A', grade_level=1, max_students=30, academic_year='2025-2026'),
        Section(name='2do Año A', grade_level=2, max_students=30, academic_year='2025-2026'),
        Section(name='3er Año A', grade_level=3, max_students=30, academic_year='2025-2026'),
    ]

    # Create teachers
    teachers = [
        Teacher(
            first_name='María', last_name='Nieto', email='mnieto@ueipab.edu.ve',
            employee_id='T001', specialization='Matemáticas', cedula='12345678'
        ),
        Teacher(
            first_name='Ismary', last_name='Arcila', email='iarcila@ueipab.edu.ve',
            employee_id='T002', specialization='Lengua y Literatura', cedula='87654321'
        ),
    ]

    # Create students
    students = [
        Student(
            first_name='Carlos', last_name='González', email='cgonzalez@student.edu.ve',
            student_code='S001', cedula_escolar='V-20001234', gender='M',
            birth_date=datetime(2010, 5, 15), grade_level=1
        ),
        Student(
            first_name='Ana', last_name='Rodríguez', email='arodriguez@student.edu.ve',
            student_code='S002', cedula_escolar='V-20005678', gender='F',
            birth_date=datetime(2010, 8, 22), grade_level=1
        ),
    ]

    # Add all to session
    for item in time_periods + subjects + classrooms + sections + teachers + students:
        db_session.add(item)

    db_session.commit()

    return {
        'time_periods': time_periods,
        'subjects': subjects,
        'classrooms': classrooms,
        'sections': sections,
        'teachers': teachers,
        'students': students
    }