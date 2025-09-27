"""
Substitute Teacher Management Service
Phase 5: Substitute Teacher Management System

Handles substitute teacher registration, absence workflow, automatic matching,
and substitute portal functionality for Venezuelan K12 institutions.

Key Features:
- Substitute pool registry with qualifications
- Automated absence workflow and substitute matching
- Performance scoring and cost calculation
- Substitute portal for assignments and earnings tracking
"""

from datetime import datetime, timezone, time, timedelta, date
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json
import logging

from ..models.tenant import (
    Teacher, Subject, Classroom, Section, TimePeriod, ScheduleAssignment,
    DayOfWeek, AcademicPeriod
)

logger = logging.getLogger(__name__)


class SubstituteTeacher:
    """
    Model for substitute teacher (stored in database as special Teacher with substitute flag)
    """
    def __init__(self, teacher_id: int, qualifications: List[str], hourly_rate: float,
                 availability_score: float = 100.0, performance_score: float = 100.0):
        self.teacher_id = teacher_id
        self.qualifications = qualifications  # Subject specializations
        self.hourly_rate = hourly_rate
        self.availability_score = availability_score
        self.performance_score = performance_score


class SubstituteAssignment:
    """
    Model for substitute assignment
    """
    def __init__(self, assignment_id: int, substitute_teacher_id: int, absent_teacher_id: int,
                 date: date, time_period_id: int, subject_id: int, section_id: int, classroom_id: int,
                 status: str = 'pending', hourly_rate: float = 0.0):
        self.assignment_id = assignment_id
        self.substitute_teacher_id = substitute_teacher_id
        self.absent_teacher_id = absent_teacher_id
        self.date = date
        self.time_period_id = time_period_id
        self.subject_id = subject_id
        self.section_id = section_id
        self.classroom_id = classroom_id
        self.status = status  # pending, accepted, declined, completed
        self.hourly_rate = hourly_rate
        self.created_at = datetime.now(timezone.utc)


class TeacherAbsence:
    """
    Model for teacher absence requests
    """
    def __init__(self, teacher_id: int, start_date: date, end_date: date,
                 reason: str, absence_type: str = 'sick', status: str = 'pending'):
        self.teacher_id = teacher_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.absence_type = absence_type  # sick, personal, training, vacation
        self.status = status  # pending, approved, denied
        self.requested_at = datetime.now(timezone.utc)


class SubstituteManagementService:
    """
    Core service for substitute teacher management
    Venezuelan K12 substitute teacher workflow and assignment system
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.current_academic_year = "2025-2026"

        # Venezuelan K12 substitute rates (in Bolívares per hour)
        self.default_rates = {
            'regular': 50.0,
            'specialist': 75.0,
            'emergency': 100.0,
            'weekend': 150.0
        }

    # ============================================================================
    # SUBSTITUTE TEACHER REGISTRY
    # ============================================================================

    def register_substitute_teacher(self, teacher_data: Dict) -> Dict:
        """
        Register a new substitute teacher with qualifications
        """
        try:
            # Create teacher record with substitute flag
            teacher = Teacher(
                teacher_name=teacher_data['teacher_name'],
                teacher_email=teacher_data.get('teacher_email'),
                phone=teacher_data.get('phone'),
                cedula=teacher_data.get('cedula'),
                specialization=teacher_data['specialization'],
                department=teacher_data.get('department'),
                is_substitute=True,
                is_active=True,
                hourly_rate=teacher_data.get('hourly_rate', self.default_rates['regular']),
                available_start_time=teacher_data.get('available_start_time', time(7, 0)),
                available_end_time=teacher_data.get('available_end_time', time(14, 20)),
                qualifications=json.dumps(teacher_data.get('qualifications', [])),
                max_daily_hours=teacher_data.get('max_daily_hours', 6),
                preferred_subjects=json.dumps(teacher_data.get('preferred_subjects', [])),
                emergency_contact=teacher_data.get('emergency_contact'),
                notes=teacher_data.get('notes', '')
            )

            self.db.add(teacher)
            self.db.commit()

            logger.info(f"Registered substitute teacher: {teacher.teacher_name}")

            return {
                'success': True,
                'substitute_id': teacher.id,
                'message': f"Substitute teacher {teacher.teacher_name} registered successfully"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error registering substitute teacher: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_substitute_pool(self, subject_id: Optional[int] = None,
                          available_date: Optional[date] = None) -> List[Dict]:
        """
        Get available substitute teachers, optionally filtered by subject and date
        """
        try:
            query = self.db.query(Teacher).filter(
                and_(
                    Teacher.is_substitute == True,
                    Teacher.is_active == True
                )
            )

            substitutes = query.all()

            # Convert to dictionaries with additional info
            substitute_list = []
            for sub in substitutes:
                qualifications = json.loads(sub.qualifications or '[]')
                preferred_subjects = json.loads(sub.preferred_subjects or '[]')

                # Filter by subject if specified
                if subject_id and str(subject_id) not in preferred_subjects:
                    continue

                substitute_data = {
                    'id': sub.id,
                    'teacher_name': sub.teacher_name,
                    'specialization': sub.specialization,
                    'hourly_rate': sub.hourly_rate or self.default_rates['regular'],
                    'qualifications': qualifications,
                    'preferred_subjects': preferred_subjects,
                    'phone': sub.phone,
                    'email': sub.teacher_email,
                    'max_daily_hours': sub.max_daily_hours or 6,
                    'availability_score': self.calculate_availability_score(sub.id, available_date),
                    'performance_score': self.calculate_performance_score(sub.id),
                    'total_assignments': self.get_substitute_assignment_count(sub.id),
                    'last_assignment': self.get_last_assignment_date(sub.id)
                }

                substitute_list.append(substitute_data)

            # Sort by performance and availability
            substitute_list.sort(key=lambda x: (x['performance_score'], x['availability_score']), reverse=True)

            return substitute_list

        except Exception as e:
            logger.error(f"Error getting substitute pool: {e}")
            return []

    # ============================================================================
    # ABSENCE WORKFLOW SYSTEM
    # ============================================================================

    def submit_absence_request(self, absence_data: Dict) -> Dict:
        """
        Submit teacher absence request and trigger substitute assignment workflow
        """
        try:
            # Create absence record (simplified - in real implementation would be a separate table)
            absence = TeacherAbsence(
                teacher_id=absence_data['teacher_id'],
                start_date=absence_data['start_date'],
                end_date=absence_data['end_date'],
                reason=absence_data['reason'],
                absence_type=absence_data.get('absence_type', 'sick')
            )

            logger.info(f"Processing absence request for teacher {absence_data['teacher_id']}")

            # Get affected schedule assignments
            affected_assignments = self.get_affected_assignments(
                absence_data['teacher_id'],
                absence_data['start_date'],
                absence_data['end_date']
            )

            # Find substitutes for each affected assignment
            substitute_assignments = []
            for assignment in affected_assignments:
                substitute_match = self.find_best_substitute(assignment, absence_data['start_date'])
                if substitute_match:
                    substitute_assignments.append(substitute_match)

            return {
                'success': True,
                'absence_id': f"ABS_{absence_data['teacher_id']}_{absence_data['start_date']}",
                'affected_assignments': len(affected_assignments),
                'substitute_matches': len(substitute_assignments),
                'assignments': substitute_assignments,
                'message': f"Absence request processed. {len(substitute_assignments)} substitutes assigned."
            }

        except Exception as e:
            logger.error(f"Error processing absence request: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_affected_assignments(self, teacher_id: int, start_date: date, end_date: date) -> List[Dict]:
        """
        Get all schedule assignments affected by teacher absence
        """
        try:
            # Get current academic period
            academic_period = self.db.query(AcademicPeriod).filter(
                AcademicPeriod.is_active == True
            ).first()

            if not academic_period:
                return []

            # Get all assignments for the teacher
            assignments = self.db.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.teacher_id == teacher_id,
                    ScheduleAssignment.academic_period_id == academic_period.id
                )
            ).all()

            affected_assignments = []
            current_date = start_date

            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    day_name = current_date.strftime('%A').lower()

                    for assignment in assignments:
                        if assignment.day_of_week.value == day_name:
                            affected_assignments.append({
                                'assignment_id': assignment.id,
                                'date': current_date,
                                'day_of_week': assignment.day_of_week,
                                'time_period_id': assignment.time_period_id,
                                'subject_id': assignment.subject_id,
                                'section_id': assignment.section_id,
                                'classroom_id': assignment.classroom_id,
                                'subject_name': assignment.subject.subject_name,
                                'section_name': assignment.section.name,
                                'classroom_name': assignment.classroom.classroom_name,
                                'time_period': f"{assignment.time_period.start_time.strftime('%H:%M')} - {assignment.time_period.end_time.strftime('%H:%M')}"
                            })

                current_date += timedelta(days=1)

            return affected_assignments

        except Exception as e:
            logger.error(f"Error getting affected assignments: {e}")
            return []

    # ============================================================================
    # SUBSTITUTE MATCHING ALGORITHM
    # ============================================================================

    def find_best_substitute(self, assignment: Dict, absence_date: date) -> Optional[Dict]:
        """
        Find the best substitute teacher for a specific assignment using Venezuelan K12 criteria
        """
        try:
            # Get available substitutes for the subject
            available_substitutes = self.get_substitute_pool(
                subject_id=assignment['subject_id'],
                available_date=absence_date
            )

            if not available_substitutes:
                logger.warning(f"No substitutes available for assignment {assignment['assignment_id']}")
                return None

            # Score each substitute
            scored_substitutes = []
            for substitute in available_substitutes:
                score = self.calculate_substitute_match_score(substitute, assignment, absence_date)
                if score > 0:  # Only consider viable substitutes
                    scored_substitutes.append({
                        'substitute': substitute,
                        'match_score': score,
                        'assignment': assignment
                    })

            if not scored_substitutes:
                return None

            # Sort by match score and select best
            scored_substitutes.sort(key=lambda x: x['match_score'], reverse=True)
            best_match = scored_substitutes[0]

            # Create substitute assignment
            substitute_assignment = SubstituteAssignment(
                assignment_id=assignment['assignment_id'],
                substitute_teacher_id=best_match['substitute']['id'],
                absent_teacher_id=assignment.get('teacher_id', 0),
                date=absence_date,
                time_period_id=assignment['time_period_id'],
                subject_id=assignment['subject_id'],
                section_id=assignment['section_id'],
                classroom_id=assignment['classroom_id'],
                status='pending',
                hourly_rate=best_match['substitute']['hourly_rate']
            )

            return {
                'substitute_assignment': substitute_assignment,
                'substitute_teacher': best_match['substitute'],
                'match_score': best_match['match_score'],
                'assignment_details': assignment
            }

        except Exception as e:
            logger.error(f"Error finding substitute: {e}")
            return None

    def calculate_substitute_match_score(self, substitute: Dict, assignment: Dict, date: date) -> float:
        """
        Calculate match score for substitute teacher assignment
        Scoring criteria:
        - Subject expertise: 40%
        - Availability: 30%
        - Performance history: 20%
        - Cost efficiency: 10%
        """
        try:
            score = 0.0

            # Subject expertise score (40%)
            preferred_subjects = substitute.get('preferred_subjects', [])
            if str(assignment['subject_id']) in preferred_subjects:
                score += 40.0
            elif assignment['subject_id'] in substitute.get('qualifications', []):
                score += 30.0
            else:
                score += 10.0  # General teaching capability

            # Availability score (30%)
            availability = substitute.get('availability_score', 100.0)
            score += (availability / 100.0) * 30.0

            # Performance history score (20%)
            performance = substitute.get('performance_score', 100.0)
            score += (performance / 100.0) * 20.0

            # Cost efficiency score (10%)
            # Lower cost gets higher score
            max_rate = self.default_rates['emergency']
            cost_score = max(0, (max_rate - substitute['hourly_rate']) / max_rate)
            score += cost_score * 10.0

            return min(100.0, score)

        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 0.0

    # ============================================================================
    # PERFORMANCE AND AVAILABILITY CALCULATIONS
    # ============================================================================

    def calculate_availability_score(self, substitute_id: int, date: Optional[date] = None) -> float:
        """
        Calculate availability score for substitute teacher
        """
        try:
            # For demo purposes, return random-ish score based on ID
            # In real implementation, would check actual availability calendar
            base_score = 100.0 - ((substitute_id % 10) * 5)

            # Reduce score if recently assigned
            recent_assignments = self.get_substitute_assignment_count(substitute_id, days=7)
            if recent_assignments > 3:
                base_score -= 20.0

            return max(50.0, base_score)

        except Exception as e:
            logger.error(f"Error calculating availability score: {e}")
            return 100.0

    def calculate_performance_score(self, substitute_id: int) -> float:
        """
        Calculate performance score based on assignment history
        """
        try:
            # For demo purposes, return score based on substitute characteristics
            # In real implementation, would analyze completion rates, ratings, etc.

            substitute = self.db.query(Teacher).get(substitute_id)
            if not substitute:
                return 50.0

            # Base score from specialization
            base_score = 80.0
            if 'MATEMÁTICAS' in substitute.specialization:
                base_score += 10.0
            if 'FÍSICA' in substitute.specialization or 'QUÍMICA' in substitute.specialization:
                base_score += 5.0

            return min(100.0, base_score)

        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 75.0

    def get_substitute_assignment_count(self, substitute_id: int, days: Optional[int] = None) -> int:
        """
        Get total assignments for substitute teacher
        """
        try:
            # In real implementation, would query substitute_assignments table
            # For demo, return mock count
            return (substitute_id % 5) + 1

        except Exception as e:
            logger.error(f"Error getting assignment count: {e}")
            return 0

    def get_last_assignment_date(self, substitute_id: int) -> Optional[str]:
        """
        Get last assignment date for substitute teacher
        """
        try:
            # For demo purposes, return recent date
            days_ago = (substitute_id % 10) + 1
            last_date = datetime.now() - timedelta(days=days_ago)
            return last_date.strftime('%Y-%m-%d')

        except Exception as e:
            logger.error(f"Error getting last assignment date: {e}")
            return None

    # ============================================================================
    # SUBSTITUTE PORTAL FUNCTIONS
    # ============================================================================

    def get_substitute_dashboard(self, substitute_id: int) -> Dict:
        """
        Get dashboard data for substitute teacher
        """
        try:
            substitute = self.db.query(Teacher).filter(
                and_(
                    Teacher.id == substitute_id,
                    Teacher.is_substitute == True
                )
            ).first()

            if not substitute:
                return {'error': 'Substitute teacher not found'}

            # Get pending assignments
            pending_assignments = self.get_pending_assignments(substitute_id)

            # Get earnings data
            monthly_earnings = self.calculate_monthly_earnings(substitute_id)

            # Get performance metrics
            performance_data = self.get_performance_metrics(substitute_id)

            return {
                'substitute_info': {
                    'id': substitute.id,
                    'name': substitute.teacher_name,
                    'specialization': substitute.specialization,
                    'hourly_rate': substitute.hourly_rate or self.default_rates['regular'],
                    'phone': substitute.phone,
                    'email': substitute.teacher_email
                },
                'pending_assignments': pending_assignments,
                'monthly_earnings': monthly_earnings,
                'performance': performance_data,
                'availability_score': self.calculate_availability_score(substitute_id),
                'total_assignments': self.get_substitute_assignment_count(substitute_id)
            }

        except Exception as e:
            logger.error(f"Error getting substitute dashboard: {e}")
            return {'error': str(e)}

    def get_pending_assignments(self, substitute_id: int) -> List[Dict]:
        """
        Get pending assignments for substitute teacher
        """
        # Mock pending assignments for demo
        return [
            {
                'id': 1,
                'date': '2025-09-27',
                'time': '7:00 - 7:40',
                'subject': 'MATEMÁTICAS',
                'section': '3er año A',
                'classroom': 'Aula 3',
                'absent_teacher': 'MARIA NIETO',
                'hourly_rate': 60.0,
                'status': 'pending'
            },
            {
                'id': 2,
                'date': '2025-09-28',
                'time': '10:00 - 10:40',
                'subject': 'FÍSICA',
                'section': '4to año B',
                'classroom': 'Lab Física',
                'absent_teacher': 'CARLOS RODRIGUEZ',
                'hourly_rate': 75.0,
                'status': 'pending'
            }
        ]

    def calculate_monthly_earnings(self, substitute_id: int) -> Dict:
        """
        Calculate monthly earnings for substitute teacher
        """
        # Mock earnings calculation for demo
        current_month_hours = (substitute_id % 10) + 15
        hourly_rate = self.default_rates['regular'] + (substitute_id % 4) * 10

        return {
            'current_month_hours': current_month_hours,
            'hourly_rate': hourly_rate,
            'current_month_earnings': current_month_hours * hourly_rate,
            'last_month_earnings': (current_month_hours - 5) * hourly_rate,
            'year_to_date': current_month_hours * hourly_rate * 9,
            'pending_payment': current_month_hours * hourly_rate * 0.3
        }

    def get_performance_metrics(self, substitute_id: int) -> Dict:
        """
        Get performance metrics for substitute teacher
        """
        return {
            'completion_rate': min(100, 85 + (substitute_id % 10)),
            'punctuality_score': min(100, 90 + (substitute_id % 8)),
            'student_feedback': min(5.0, 4.0 + (substitute_id % 10) / 10),
            'admin_rating': min(5.0, 4.2 + (substitute_id % 8) / 10),
            'total_assignments_completed': self.get_substitute_assignment_count(substitute_id),
            'cancellation_rate': max(0, 15 - (substitute_id % 8))
        }

    # ============================================================================
    # ASSIGNMENT ACCEPTANCE/DECLINE
    # ============================================================================

    def accept_assignment(self, substitute_id: int, assignment_id: int) -> Dict:
        """
        Accept substitute assignment
        """
        try:
            # In real implementation, would update assignment status in database
            logger.info(f"Substitute {substitute_id} accepted assignment {assignment_id}")

            return {
                'success': True,
                'message': 'Assignment accepted successfully',
                'assignment_id': assignment_id,
                'next_steps': [
                    'Arrive 15 minutes early',
                    'Check in with administration',
                    'Review lesson plans if available',
                    'Report any issues to academic coordinator'
                ]
            }

        except Exception as e:
            logger.error(f"Error accepting assignment: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def decline_assignment(self, substitute_id: int, assignment_id: int, reason: str) -> Dict:
        """
        Decline substitute assignment and trigger re-assignment
        """
        try:
            # In real implementation, would update assignment and find new substitute
            logger.info(f"Substitute {substitute_id} declined assignment {assignment_id}: {reason}")

            return {
                'success': True,
                'message': 'Assignment declined. Finding alternative substitute...',
                'assignment_id': assignment_id
            }

        except Exception as e:
            logger.error(f"Error declining assignment: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ============================================================================
    # COST AND RATE MANAGEMENT
    # ============================================================================

    def calculate_assignment_cost(self, substitute_id: int, hours: float, assignment_type: str = 'regular') -> Dict:
        """
        Calculate cost for substitute assignment
        """
        try:
            substitute = self.db.query(Teacher).get(substitute_id)
            base_rate = substitute.hourly_rate if substitute else self.default_rates[assignment_type]

            # Apply multipliers for special circumstances
            multiplier = 1.0
            if assignment_type == 'emergency':
                multiplier = 1.5
            elif assignment_type == 'weekend':
                multiplier = 2.0
            elif assignment_type == 'specialist':
                multiplier = 1.25

            total_cost = hours * base_rate * multiplier

            return {
                'hours': hours,
                'base_rate': base_rate,
                'multiplier': multiplier,
                'total_cost': total_cost,
                'assignment_type': assignment_type
            }

        except Exception as e:
            logger.error(f"Error calculating assignment cost: {e}")
            return {
                'hours': hours,
                'base_rate': self.default_rates['regular'],
                'multiplier': 1.0,
                'total_cost': hours * self.default_rates['regular'],
                'assignment_type': 'regular'
            }