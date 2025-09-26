"""
BiScheduler Schedule Management Services
Core scheduling functionality for Venezuelan K12 platform
Enhanced with conflict detection and workload validation
"""

from datetime import datetime, timezone, time
from typing import Dict, List, Optional, Tuple, Set
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_
from enum import Enum

from src.models.tenant import (
    ScheduleAssignment, ScheduleConflict, TimePeriod, Teacher, Subject,
    Section, Classroom, TeacherSubject, TeacherWorkload, DayOfWeek
)


class ConflictType(Enum):
    """Types of scheduling conflicts"""
    TEACHER_DOUBLE_BOOKING = "teacher_double_booking"
    CLASSROOM_CONFLICT = "classroom_conflict"
    SECTION_OVERLAP = "section_overlap"
    WORKLOAD_VIOLATION = "workload_violation"
    TIME_PERIOD_INVALID = "time_period_invalid"
    TEACHER_SUBJECT_MISMATCH = "teacher_subject_mismatch"


class ConflictSeverity(Enum):
    """Severity levels for conflicts"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ScheduleManager:
    """
    Core schedule management for Venezuelan K12 institutions
    Handles assignment creation, conflict detection, and workload validation
    """

    def __init__(self, tenant_db_url: str, academic_year: str = "2025-2026"):
        self.tenant_db_url = tenant_db_url
        self.academic_year = academic_year
        self.engine = create_engine(tenant_db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_schedule_assignment(
        self,
        teacher_id: int,
        subject_id: int,
        section_id: int,
        classroom_id: int,
        time_period_id: int,
        day_of_week: DayOfWeek,
        created_by: str = None,
        validate_conflicts: bool = True
    ) -> Dict[str, any]:
        """
        Create a new schedule assignment with conflict validation

        Args:
            teacher_id: Teacher ID
            subject_id: Subject ID
            section_id: Section ID
            classroom_id: Classroom ID
            time_period_id: Time period ID
            day_of_week: Day of the week
            created_by: User who created the assignment
            validate_conflicts: Whether to check for conflicts

        Returns:
            Result dictionary with assignment and conflict information
        """
        session = self.SessionLocal()

        try:
            # Create assignment object
            assignment = ScheduleAssignment(
                teacher_id=teacher_id,
                subject_id=subject_id,
                section_id=section_id,
                classroom_id=classroom_id,
                time_period_id=time_period_id,
                day_of_week=day_of_week,
                academic_year=self.academic_year,
                created_by=created_by,
                effective_date=datetime.now(timezone.utc)
            )

            # Validate conflicts if requested
            conflicts = []
            if validate_conflicts:
                conflicts = self._detect_assignment_conflicts(session, assignment)

            # Determine if assignment can be created
            critical_conflicts = [c for c in conflicts if c['severity'] == ConflictSeverity.CRITICAL.value]

            if critical_conflicts:
                return {
                    'status': 'error',
                    'message': 'Critical conflicts detected',
                    'conflicts': conflicts,
                    'assignment': None
                }

            # Create assignment
            session.add(assignment)
            session.flush()  # Get assignment ID

            # Log non-critical conflicts
            for conflict_data in conflicts:
                if conflict_data['severity'] != ConflictSeverity.CRITICAL.value:
                    conflict = ScheduleConflict(
                        conflict_type=conflict_data['type'],
                        severity=conflict_data['severity'],
                        assignment_1_id=assignment.id,
                        description=conflict_data['description'],
                        suggested_resolution=conflict_data.get('resolution'),
                        academic_year=self.academic_year
                    )
                    session.add(conflict)

            session.commit()

            # Update teacher workload
            self._update_teacher_workload(session, teacher_id)

            return {
                'status': 'success',
                'message': 'Schedule assignment created successfully',
                'assignment': {
                    'id': assignment.id,
                    'teacher_id': assignment.teacher_id,
                    'subject_id': assignment.subject_id,
                    'section_id': assignment.section_id,
                    'classroom_id': assignment.classroom_id,
                    'time_period_id': assignment.time_period_id,
                    'day_of_week': assignment.day_of_week.value,
                    'effective_date': assignment.effective_date.isoformat()
                },
                'conflicts': conflicts
            }

        except Exception as e:
            session.rollback()
            return {
                'status': 'error',
                'message': f'Failed to create assignment: {str(e)}',
                'assignment': None,
                'conflicts': []
            }
        finally:
            session.close()

    def _detect_assignment_conflicts(self, session, assignment: ScheduleAssignment) -> List[Dict]:
        """
        Detect conflicts for a schedule assignment

        Args:
            session: Database session
            assignment: Schedule assignment to check

        Returns:
            List of conflict dictionaries
        """
        conflicts = []

        # Check teacher double booking
        teacher_conflicts = self._check_teacher_conflicts(session, assignment)
        conflicts.extend(teacher_conflicts)

        # Check classroom conflicts
        classroom_conflicts = self._check_classroom_conflicts(session, assignment)
        conflicts.extend(classroom_conflicts)

        # Check section conflicts
        section_conflicts = self._check_section_conflicts(session, assignment)
        conflicts.extend(section_conflicts)

        # Check teacher-subject relationship
        subject_conflicts = self._check_teacher_subject_validity(session, assignment)
        conflicts.extend(subject_conflicts)

        # Check workload violations
        workload_conflicts = self._check_workload_violations(session, assignment)
        conflicts.extend(workload_conflicts)

        return conflicts

    def _check_teacher_conflicts(self, session, assignment: ScheduleAssignment) -> List[Dict]:
        """Check for teacher double booking conflicts"""
        conflicts = []

        # Find existing assignments for same teacher, day, and time period
        existing = session.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.teacher_id == assignment.teacher_id,
                ScheduleAssignment.day_of_week == assignment.day_of_week,
                ScheduleAssignment.time_period_id == assignment.time_period_id,
                ScheduleAssignment.academic_year == assignment.academic_year,
                ScheduleAssignment.is_active == True,
                ScheduleAssignment.id != getattr(assignment, 'id', 0)  # Exclude self if updating
            )
        ).first()

        if existing:
            conflicts.append({
                'type': ConflictType.TEACHER_DOUBLE_BOOKING.value,
                'severity': ConflictSeverity.CRITICAL.value,
                'description': f'Teacher is already assigned to another class at this time',
                'existing_assignment_id': existing.id,
                'resolution': 'Choose a different time period or teacher'
            })

        return conflicts

    def _check_classroom_conflicts(self, session, assignment: ScheduleAssignment) -> List[Dict]:
        """Check for classroom booking conflicts"""
        conflicts = []

        # Find existing assignments for same classroom, day, and time period
        existing = session.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.classroom_id == assignment.classroom_id,
                ScheduleAssignment.day_of_week == assignment.day_of_week,
                ScheduleAssignment.time_period_id == assignment.time_period_id,
                ScheduleAssignment.academic_year == assignment.academic_year,
                ScheduleAssignment.is_active == True,
                ScheduleAssignment.id != getattr(assignment, 'id', 0)
            )
        ).first()

        if existing:
            conflicts.append({
                'type': ConflictType.CLASSROOM_CONFLICT.value,
                'severity': ConflictSeverity.CRITICAL.value,
                'description': f'Classroom is already occupied at this time',
                'existing_assignment_id': existing.id,
                'resolution': 'Choose a different classroom or time period'
            })

        return conflicts

    def _check_section_conflicts(self, session, assignment: ScheduleAssignment) -> List[Dict]:
        """Check for section scheduling conflicts"""
        conflicts = []

        # Find existing assignments for same section, day, and time period
        existing = session.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.section_id == assignment.section_id,
                ScheduleAssignment.day_of_week == assignment.day_of_week,
                ScheduleAssignment.time_period_id == assignment.time_period_id,
                ScheduleAssignment.academic_year == assignment.academic_year,
                ScheduleAssignment.is_active == True,
                ScheduleAssignment.id != getattr(assignment, 'id', 0)
            )
        ).first()

        if existing:
            conflicts.append({
                'type': ConflictType.SECTION_OVERLAP.value,
                'severity': ConflictSeverity.CRITICAL.value,
                'description': f'Section already has a class scheduled at this time',
                'existing_assignment_id': existing.id,
                'resolution': 'Choose a different time period for this section'
            })

        return conflicts

    def _check_teacher_subject_validity(self, session, assignment: ScheduleAssignment) -> List[Dict]:
        """Check if teacher is qualified to teach the subject"""
        conflicts = []

        # Check if teacher has relationship with subject
        teacher_subject = session.query(TeacherSubject).filter(
            and_(
                TeacherSubject.teacher_id == assignment.teacher_id,
                TeacherSubject.subject_id == assignment.subject_id,
                TeacherSubject.academic_year == assignment.academic_year,
                TeacherSubject.is_active == True
            )
        ).first()

        if not teacher_subject:
            conflicts.append({
                'type': ConflictType.TEACHER_SUBJECT_MISMATCH.value,
                'severity': ConflictSeverity.WARNING.value,
                'description': f'Teacher is not assigned to teach this subject',
                'resolution': 'Verify teacher qualifications or assign subject to teacher first'
            })

        return conflicts

    def _check_workload_violations(self, session, assignment: ScheduleAssignment) -> List[Dict]:
        """Check for teacher workload violations"""
        conflicts = []

        # Get teacher's current workload
        teacher = session.query(Teacher).filter_by(id=assignment.teacher_id).first()
        if not teacher:
            return conflicts

        # Count current weekly hours for this teacher
        current_assignments = session.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.teacher_id == assignment.teacher_id,
                ScheduleAssignment.academic_year == assignment.academic_year,
                ScheduleAssignment.is_active == True
            )
        ).count()

        # Each assignment represents one period per week
        projected_hours = current_assignments + 1

        # Check against maximum allowed hours
        max_hours = teacher.max_weekly_hours or 40
        if projected_hours > max_hours:
            conflicts.append({
                'type': ConflictType.WORKLOAD_VIOLATION.value,
                'severity': ConflictSeverity.ERROR.value,
                'description': f'Assignment would exceed teacher maximum hours ({projected_hours} > {max_hours})',
                'resolution': f'Reduce teacher workload or increase maximum allowed hours'
            })

        return conflicts

    def _update_teacher_workload(self, session, teacher_id: int):
        """Update teacher workload calculations"""
        try:
            # Count total assignments for teacher
            total_assignments = session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.teacher_id == teacher_id,
                    ScheduleAssignment.academic_year == self.academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).count()

            # Update teacher's current weekly hours
            teacher = session.query(Teacher).filter_by(id=teacher_id).first()
            if teacher:
                teacher.current_weekly_hours = total_assignments

            # Update or create workload record
            workload = session.query(TeacherWorkload).filter(
                and_(
                    TeacherWorkload.teacher_id == teacher_id,
                    TeacherWorkload.academic_year == self.academic_year
                )
            ).first()

            if workload:
                workload.calculated_hours = total_assignments
                workload.validate_workload()
            else:
                workload = TeacherWorkload(
                    teacher_id=teacher_id,
                    academic_year=self.academic_year,
                    total_weekly_hours=total_assignments,
                    calculated_hours=total_assignments,
                    max_allowed_hours=teacher.max_weekly_hours or 40
                )
                workload.validate_workload()
                session.add(workload)

            session.commit()

        except Exception as e:
            session.rollback()
            print(f"Error updating teacher workload: {str(e)}")

    def get_schedule_for_section(self, section_id: int, week_start: datetime = None) -> Dict[str, any]:
        """
        Get complete schedule for a section

        Args:
            section_id: Section ID
            week_start: Start of week (optional)

        Returns:
            Schedule data organized by day and time period
        """
        session = self.SessionLocal()

        try:
            # Get all assignments for section
            assignments = session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.section_id == section_id,
                    ScheduleAssignment.academic_year == self.academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).all()

            # Organize by day and time period
            schedule = {}
            for day in DayOfWeek:
                schedule[day.value] = {}

            for assignment in assignments:
                day = assignment.day_of_week.value
                time_period = assignment.time_period

                schedule[day][time_period.period_name] = {
                    'assignment_id': assignment.id,
                    'subject': assignment.subject.subject_name,
                    'teacher': assignment.teacher.teacher_name,
                    'classroom': assignment.classroom.name,
                    'time': f"{time_period.start_time} - {time_period.end_time}",
                    'is_break': time_period.is_break
                }

            return {
                'status': 'success',
                'section_id': section_id,
                'academic_year': self.academic_year,
                'schedule': schedule
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to get section schedule: {str(e)}'
            }
        finally:
            session.close()

    def get_teacher_schedule(self, teacher_id: int) -> Dict[str, any]:
        """
        Get complete schedule for a teacher with workload information

        Args:
            teacher_id: Teacher ID

        Returns:
            Teacher schedule and workload data
        """
        session = self.SessionLocal()

        try:
            # Get teacher info
            teacher = session.query(Teacher).filter_by(id=teacher_id).first()
            if not teacher:
                return {
                    'status': 'error',
                    'message': 'Teacher not found'
                }

            # Get all assignments for teacher
            assignments = session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.teacher_id == teacher_id,
                    ScheduleAssignment.academic_year == self.academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).all()

            # Organize schedule
            schedule = {}
            for day in DayOfWeek:
                schedule[day.value] = {}

            subjects_taught = set()
            total_hours = 0

            for assignment in assignments:
                day = assignment.day_of_week.value
                time_period = assignment.time_period

                schedule[day][time_period.period_name] = {
                    'assignment_id': assignment.id,
                    'subject': assignment.subject.subject_name,
                    'section': assignment.section.name,
                    'classroom': assignment.classroom.name,
                    'time': f"{time_period.start_time} - {time_period.end_time}"
                }

                subjects_taught.add(assignment.subject.subject_name)
                total_hours += 1

            # Get workload information
            workload = session.query(TeacherWorkload).filter(
                and_(
                    TeacherWorkload.teacher_id == teacher_id,
                    TeacherWorkload.academic_year == self.academic_year
                )
            ).first()

            return {
                'status': 'success',
                'teacher': {
                    'id': teacher.id,
                    'name': teacher.teacher_name,
                    'specialization': teacher.area_specialization
                },
                'schedule': schedule,
                'workload': {
                    'current_hours': total_hours,
                    'max_hours': teacher.max_weekly_hours,
                    'subjects_taught': list(subjects_taught),
                    'is_valid': workload.is_valid if workload else True,
                    'overtime_hours': workload.overtime_hours if workload else 0
                },
                'academic_year': self.academic_year
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to get teacher schedule: {str(e)}'
            }
        finally:
            session.close()

    def detect_all_conflicts(self) -> Dict[str, any]:
        """
        Detect all scheduling conflicts in the current academic year

        Returns:
            Comprehensive conflict report
        """
        session = self.SessionLocal()

        try:
            conflicts = []

            # Get all active assignments
            assignments = session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.academic_year == self.academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).all()

            # Check each assignment for conflicts
            for assignment in assignments:
                assignment_conflicts = self._detect_assignment_conflicts(session, assignment)
                for conflict in assignment_conflicts:
                    conflict['assignment_id'] = assignment.id
                    conflicts.append(conflict)

            # Organize conflicts by type and severity
            conflict_summary = {}
            for conflict in conflicts:
                conflict_type = conflict['type']
                severity = conflict['severity']

                if conflict_type not in conflict_summary:
                    conflict_summary[conflict_type] = {}
                if severity not in conflict_summary[conflict_type]:
                    conflict_summary[conflict_type][severity] = 0

                conflict_summary[conflict_type][severity] += 1

            return {
                'status': 'success',
                'total_conflicts': len(conflicts),
                'conflicts': conflicts,
                'summary': conflict_summary,
                'academic_year': self.academic_year
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to detect conflicts: {str(e)}'
            }
        finally:
            session.close()

    def resolve_conflict(self, conflict_id: int, resolution_notes: str, resolved_by: str) -> Dict[str, any]:
        """
        Mark a conflict as resolved

        Args:
            conflict_id: Conflict ID
            resolution_notes: Notes about how conflict was resolved
            resolved_by: User who resolved the conflict

        Returns:
            Resolution result
        """
        session = self.SessionLocal()

        try:
            conflict = session.query(ScheduleConflict).filter_by(id=conflict_id).first()

            if not conflict:
                return {
                    'status': 'error',
                    'message': 'Conflict not found'
                }

            conflict.status = 'resolved'
            conflict.resolved_by = resolved_by
            conflict.resolved_at = datetime.now(timezone.utc)
            conflict.resolution_notes = resolution_notes

            session.commit()

            return {
                'status': 'success',
                'message': 'Conflict resolved successfully',
                'conflict_id': conflict_id
            }

        except Exception as e:
            session.rollback()
            return {
                'status': 'error',
                'message': f'Failed to resolve conflict: {str(e)}'
            }
        finally:
            session.close()

    def get_classroom_utilization(self) -> Dict[str, any]:
        """
        Get classroom utilization statistics

        Returns:
            Classroom usage analysis
        """
        session = self.SessionLocal()

        try:
            # Get all classrooms and their assignments
            from sqlalchemy import func

            utilization = session.query(
                Classroom.id,
                Classroom.name,
                Classroom.capacity,
                func.count(ScheduleAssignment.id).label('assignments_count')
            ).outerjoin(
                ScheduleAssignment,
                and_(
                    ScheduleAssignment.classroom_id == Classroom.id,
                    ScheduleAssignment.academic_year == self.academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).group_by(Classroom.id).all()

            # Calculate utilization percentages
            # Assuming 5 days × max periods per day as total possible slots
            max_periods_per_day = session.query(func.count(TimePeriod.id)).filter(
                TimePeriod.academic_year == self.academic_year
            ).scalar() or 8

            total_possible_slots = 5 * max_periods_per_day  # 5 days per week

            classroom_stats = []
            for classroom_id, name, capacity, assignments in utilization:
                utilization_pct = (assignments / total_possible_slots * 100) if total_possible_slots > 0 else 0

                classroom_stats.append({
                    'classroom_id': classroom_id,
                    'name': name,
                    'capacity': capacity,
                    'assignments_count': assignments,
                    'total_possible_slots': total_possible_slots,
                    'utilization_percentage': round(utilization_pct, 2)
                })

            return {
                'status': 'success',
                'classrooms': classroom_stats,
                'academic_year': self.academic_year
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to get classroom utilization: {str(e)}'
            }
        finally:
            session.close()