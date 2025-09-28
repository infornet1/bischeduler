"""
Unit tests for BiScheduler service layer.
Tests business logic and service functions.
"""

import pytest
from datetime import datetime, time, timedelta
from unittest.mock import Mock, patch
from src.scheduling.services import (
    ScheduleService, ConflictDetectionService, WorkloadCalculator,
    PreferenceScorer, ScheduleOptimizer
)
from src.models.tenant import (
    DayOfWeek, ConflictType, EducationalLevel,
    TeacherPreference, PreferenceType
)


class TestScheduleService:
    """Test schedule management service."""

    @pytest.mark.unit
    def test_validate_assignment_no_conflicts(self, sample_venezuelan_data):
        """Test assignment validation with no conflicts."""
        service = ScheduleService()

        assignment_data = {
            'teacher_id': sample_venezuelan_data['teachers'][0].id,
            'subject_id': sample_venezuelan_data['subjects'][0].id,
            'section_id': sample_venezuelan_data['sections'][0].id,
            'classroom_id': sample_venezuelan_data['classrooms'][0].id,
            'time_period_id': sample_venezuelan_data['time_periods'][0].id,
            'day_of_week': DayOfWeek.LUNES,
            'academic_year': '2025-2026'
        }

        # Mock no existing assignments
        with patch.object(service, 'check_conflicts', return_value=[]):
            result = service.validate_assignment(assignment_data)
            assert result['valid'] is True
            assert len(result['conflicts']) == 0

    @pytest.mark.unit
    def test_validate_assignment_with_conflicts(self, sample_venezuelan_data):
        """Test assignment validation with conflicts."""
        service = ScheduleService()

        assignment_data = {
            'teacher_id': sample_venezuelan_data['teachers'][0].id,
            'subject_id': sample_venezuelan_data['subjects'][0].id,
            'section_id': sample_venezuelan_data['sections'][0].id,
            'classroom_id': sample_venezuelan_data['classrooms'][0].id,
            'time_period_id': sample_venezuelan_data['time_periods'][0].id,
            'day_of_week': DayOfWeek.MARTES,
            'academic_year': '2025-2026'
        }

        mock_conflict = {
            'type': ConflictType.TEACHER_DOUBLE_BOOKING,
            'description': 'Teacher already assigned',
            'severity': 'HIGH'
        }

        with patch.object(service, 'check_conflicts', return_value=[mock_conflict]):
            result = service.validate_assignment(assignment_data)
            assert result['valid'] is False
            assert len(result['conflicts']) == 1
            assert result['conflicts'][0]['type'] == ConflictType.TEACHER_DOUBLE_BOOKING

    @pytest.mark.unit
    @pytest.mark.venezuelan
    def test_calculate_weekly_schedule_hours(self, sample_venezuelan_data):
        """Test weekly schedule hours calculation."""
        service = ScheduleService()

        # Create mock assignments for a teacher
        assignments = []
        teacher_id = sample_venezuelan_data['teachers'][0].id

        # Add 6 math classes (6 * 40 minutes = 240 minutes = 4 hours)
        for i in range(6):
            assignments.append({
                'teacher_id': teacher_id,
                'time_period_id': sample_venezuelan_data['time_periods'][i % 4].id,
                'day_of_week': list(DayOfWeek)[i % 5],
                'duration_minutes': 40
            })

        with patch.object(service, 'get_teacher_assignments', return_value=assignments):
            hours = service.calculate_weekly_hours(teacher_id)
            assert hours == 4.0  # 240 minutes = 4 hours


class TestConflictDetectionService:
    """Test conflict detection service."""

    @pytest.mark.unit
    def test_detect_teacher_double_booking(self):
        """Test detection of teacher double booking."""
        service = ConflictDetectionService()

        existing_assignments = [
            {
                'id': 1,
                'teacher_id': 1,
                'time_period_id': 1,
                'day_of_week': DayOfWeek.LUNES,
                'section_id': 1
            }
        ]

        new_assignment = {
            'teacher_id': 1,
            'time_period_id': 1,
            'day_of_week': DayOfWeek.LUNES,
            'section_id': 2  # Different section, same time
        }

        conflicts = service.check_teacher_conflicts(new_assignment, existing_assignments)

        assert len(conflicts) == 1
        assert conflicts[0]['type'] == ConflictType.TEACHER_DOUBLE_BOOKING
        assert conflicts[0]['severity'] == 'HIGH'

    @pytest.mark.unit
    def test_detect_classroom_double_booking(self):
        """Test detection of classroom double booking."""
        service = ConflictDetectionService()

        existing_assignments = [
            {
                'id': 1,
                'classroom_id': 1,
                'time_period_id': 1,
                'day_of_week': DayOfWeek.MARTES
            }
        ]

        new_assignment = {
            'classroom_id': 1,
            'time_period_id': 1,
            'day_of_week': DayOfWeek.MARTES
        }

        conflicts = service.check_classroom_conflicts(new_assignment, existing_assignments)

        assert len(conflicts) == 1
        assert conflicts[0]['type'] == ConflictType.CLASSROOM_DOUBLE_BOOKING
        assert conflicts[0]['severity'] == 'HIGH'

    @pytest.mark.unit
    @pytest.mark.venezuelan
    def test_detect_venezuelan_compliance_conflicts(self):
        """Test detection of Venezuelan education compliance conflicts."""
        service = ConflictDetectionService()

        # Test max daily hours violation (Venezuelan standard: max 6 hours/day)
        teacher_daily_hours = 7  # Exceeds 6 hour limit

        conflict = service.check_daily_hour_limit(teacher_daily_hours, max_hours=6)

        assert conflict is not None
        assert conflict['type'] == ConflictType.MAX_DAILY_HOURS_EXCEEDED
        assert conflict['severity'] == 'MEDIUM'


class TestWorkloadCalculator:
    """Test teacher workload calculation."""

    @pytest.mark.unit
    def test_calculate_teacher_workload(self, sample_venezuelan_data):
        """Test teacher workload calculation."""
        calculator = WorkloadCalculator()

        teacher_id = sample_venezuelan_data['teachers'][0].id
        assignments = []

        # Create 22 hours of weekly assignments (Venezuelan teacher standard)
        for day in range(5):  # Monday to Friday
            for period in range(4):  # 4 periods per day
                if len(assignments) < 33:  # 33 * 40min = 22 hours
                    assignments.append({
                        'teacher_id': teacher_id,
                        'duration_minutes': 40,
                        'day_of_week': list(DayOfWeek)[day]
                    })

        workload = calculator.calculate(teacher_id, assignments)

        assert workload['total_hours'] == 22.0
        assert workload['daily_average'] == 4.4  # 22 hours / 5 days
        assert workload['is_compliant'] is True  # Within Venezuelan standards

    @pytest.mark.unit
    @pytest.mark.venezuelan
    def test_venezuelan_workload_limits(self):
        """Test Venezuelan teacher workload limits."""
        calculator = WorkloadCalculator()

        # Test minimum hours (12 hours/week)
        assert calculator.validate_workload(11) == {'valid': False, 'reason': 'Below minimum'}
        assert calculator.validate_workload(12) == {'valid': True}

        # Test maximum hours (32 hours/week for full-time)
        assert calculator.validate_workload(32) == {'valid': True}
        assert calculator.validate_workload(33) == {'valid': False, 'reason': 'Exceeds maximum'}


class TestPreferenceScorer:
    """Test teacher preference scoring system."""

    @pytest.mark.unit
    def test_calculate_preference_score(self):
        """Test preference score calculation with Venezuelan weightings."""
        scorer = PreferenceScorer()

        preferences = {
            'time_preference': 0.8,  # 80% match
            'day_preference': 0.6,   # 60% match
            'subject_preference': 0.9, # 90% match
            'classroom_preference': 0.5  # 50% match
        }

        # Venezuelan weightings: 40% time, 30% day, 20% subject, 10% classroom
        score = scorer.calculate_score(
            preferences,
            weights={'time': 0.4, 'day': 0.3, 'subject': 0.2, 'classroom': 0.1}
        )

        expected = (0.8 * 0.4) + (0.6 * 0.3) + (0.9 * 0.2) + (0.5 * 0.1)
        assert abs(score - expected) < 0.01  # 0.73

    @pytest.mark.unit
    def test_preference_satisfaction_level(self):
        """Test preference satisfaction level categorization."""
        scorer = PreferenceScorer()

        assert scorer.get_satisfaction_level(0.85) == 'Excellent'
        assert scorer.get_satisfaction_level(0.75) == 'Good'
        assert scorer.get_satisfaction_level(0.65) == 'Satisfactory'
        assert scorer.get_satisfaction_level(0.45) == 'Poor'


class TestScheduleOptimizer:
    """Test schedule optimization algorithms."""

    @pytest.mark.unit
    def test_genetic_algorithm_initialization(self):
        """Test genetic algorithm initialization."""
        optimizer = ScheduleOptimizer(algorithm='genetic')

        population_size = 50
        chromosome_length = 100

        population = optimizer.initialize_population(population_size, chromosome_length)

        assert len(population) == population_size
        assert all(len(chrom) == chromosome_length for chrom in population)

    @pytest.mark.unit
    def test_constraint_solver_validation(self):
        """Test constraint solver validation."""
        optimizer = ScheduleOptimizer(algorithm='constraint')

        constraints = [
            {'type': 'max_daily_hours', 'value': 6},
            {'type': 'min_weekly_hours', 'value': 12},
            {'type': 'max_consecutive_hours', 'value': 3}
        ]

        schedule = {
            'monday': [1, 2, 3, 4],  # 4 consecutive hours
            'tuesday': [1, 2],
            'wednesday': [1, 2, 3],
            'thursday': [1, 2],
            'friday': [1, 2, 3]
        }

        violations = optimizer.check_constraint_violations(schedule, constraints)

        assert len(violations) > 0
        assert any(v['constraint'] == 'max_consecutive_hours' for v in violations)

    @pytest.mark.unit
    @pytest.mark.venezuelan
    def test_venezuelan_optimization_objectives(self):
        """Test optimization objectives for Venezuelan K12."""
        optimizer = ScheduleOptimizer()

        objectives = optimizer.get_venezuelan_objectives()

        assert 'minimize_gaps' in objectives
        assert 'balance_workload' in objectives
        assert 'maximize_preference_satisfaction' in objectives
        assert 'comply_with_regulations' in objectives

        # Check Venezuelan-specific weightings
        assert objectives['comply_with_regulations']['weight'] == 1.0  # Highest priority
        assert objectives['maximize_preference_satisfaction']['weight'] >= 0.7