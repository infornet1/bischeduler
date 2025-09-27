"""
BiScheduler Exam Scheduling Service
Phase 6: Exam Scheduling with Venezuelan K12 Compliance

Constraint engine for exam scheduling with conflict detection,
supervisor assignment, and Venezuelan exam types.
"""

from datetime import datetime, timezone, time, timedelta, date
from typing import List, Dict, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, distinct
import json
from collections import defaultdict

from ..models.tenant import (
    Exam, ExamSupervisor, ExamConflict, StudentExamSchedule, ExamCalendarEvent,
    Teacher, Subject, Classroom, Section, TimePeriod,
    ExamType, ExamStatus, SupervisorRole
)


class ExamConstraintEngine:
    """
    Venezuelan K12 Exam Scheduling Constraint Engine
    Handles conflict detection, supervisor assignment, and room capacity
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.current_academic_year = "2025-2026"

    # ============================================================================
    # CONSTRAINT VALIDATION
    # ============================================================================

    def validate_exam_scheduling(self, exam_data: Dict) -> Dict:
        """
        Comprehensive exam scheduling validation
        Returns validation results with conflicts and suggestions
        """
        conflicts = []
        warnings = []
        suggestions = []

        # Basic data validation
        if not self._validate_basic_exam_data(exam_data):
            return {'valid': False, 'error': 'Invalid exam data provided'}

        exam_date = datetime.fromisoformat(exam_data['exam_date'])
        start_time = datetime.strptime(exam_data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(exam_data['end_time'], '%H:%M').time()

        # 1. Student conflict detection
        student_conflicts = self._check_student_conflicts(
            exam_data['section_id'], exam_date, start_time, end_time
        )
        conflicts.extend(student_conflicts)

        # 2. Classroom availability
        classroom_conflicts = self._check_classroom_conflicts(
            exam_data['classroom_id'], exam_date, start_time, end_time
        )
        conflicts.extend(classroom_conflicts)

        # 3. Supervisor availability
        supervisor_conflicts = self._check_supervisor_availability(
            exam_data.get('supervisor_ids', []), exam_date, start_time, end_time
        )
        conflicts.extend(supervisor_conflicts)

        # 4. Weekly limits validation
        weekly_limit_warnings = self._check_weekly_exam_limits(
            exam_data['section_id'], exam_date
        )
        warnings.extend(weekly_limit_warnings)

        # 5. Preparation time validation
        preparation_warnings = self._check_preparation_time(
            exam_data['section_id'], exam_data['subject_id'], exam_date
        )
        warnings.extend(preparation_warnings)

        # 6. Room capacity validation
        capacity_warnings = self._check_room_capacity(
            exam_data['classroom_id'], exam_data['section_id']
        )
        warnings.extend(capacity_warnings)

        # Generate suggestions for improvement
        if conflicts or warnings:
            suggestions = self._generate_scheduling_suggestions(
                exam_data, conflicts, warnings
            )

        return {
            'valid': len(conflicts) == 0,
            'conflicts': conflicts,
            'warnings': warnings,
            'suggestions': suggestions,
            'conflict_count': len(conflicts),
            'warning_count': len(warnings)
        }

    def _validate_basic_exam_data(self, exam_data: Dict) -> bool:
        """Validate basic exam data structure"""
        required_fields = [
            'exam_name', 'exam_type', 'subject_id', 'section_id',
            'exam_date', 'start_time', 'end_time', 'classroom_id'
        ]
        return all(field in exam_data for field in required_fields)

    def _check_student_conflicts(self, section_id: int, exam_date: datetime,
                               start_time: time, end_time: time) -> List[Dict]:
        """Check for student scheduling conflicts"""
        conflicts = []

        # Get existing exams for the same section on the same date
        existing_exams = self.db.query(Exam).filter(
            and_(
                Exam.section_id == section_id,
                func.date(Exam.exam_date) == exam_date.date(),
                Exam.status.in_([ExamStatus.SCHEDULED, ExamStatus.CONFIRMED]),
                Exam.academic_year == self.current_academic_year
            )
        ).all()

        for existing_exam in existing_exams:
            # Check time overlap
            if self._time_periods_overlap(
                start_time, end_time,
                existing_exam.start_time, existing_exam.end_time
            ):
                conflicts.append({
                    'type': 'student_time_conflict',
                    'severity': 'error',
                    'description': f'Students have overlapping exam: {existing_exam.exam_name}',
                    'conflicting_exam_id': existing_exam.id,
                    'conflicting_exam_name': existing_exam.exam_name,
                    'conflicting_time': f'{existing_exam.start_time}-{existing_exam.end_time}'
                })

        # Check daily exam limits (max 2 exams per day per student)
        daily_exam_count = len(existing_exams)
        if daily_exam_count >= 2:
            conflicts.append({
                'type': 'daily_exam_limit',
                'severity': 'error',
                'description': f'Students already have {daily_exam_count} exams on this date',
                'limit': 2,
                'current_count': daily_exam_count
            })

        return conflicts

    def _check_classroom_conflicts(self, classroom_id: int, exam_date: datetime,
                                 start_time: time, end_time: time) -> List[Dict]:
        """Check for classroom scheduling conflicts"""
        conflicts = []

        # Get existing exams in the same classroom
        existing_exams = self.db.query(Exam).filter(
            and_(
                Exam.classroom_id == classroom_id,
                func.date(Exam.exam_date) == exam_date.date(),
                Exam.status.in_([ExamStatus.SCHEDULED, ExamStatus.CONFIRMED]),
                Exam.academic_year == self.current_academic_year
            )
        ).all()

        for existing_exam in existing_exams:
            if self._time_periods_overlap(
                start_time, end_time,
                existing_exam.start_time, existing_exam.end_time
            ):
                conflicts.append({
                    'type': 'classroom_conflict',
                    'severity': 'error',
                    'description': f'Classroom occupied by: {existing_exam.exam_name}',
                    'conflicting_exam_id': existing_exam.id,
                    'conflicting_exam_name': existing_exam.exam_name,
                    'classroom_name': existing_exam.classroom.name
                })

        return conflicts

    def _check_supervisor_availability(self, supervisor_ids: List[int],
                                     exam_date: datetime, start_time: time,
                                     end_time: time) -> List[Dict]:
        """Check supervisor availability conflicts"""
        conflicts = []

        for supervisor_id in supervisor_ids:
            # Get existing supervision assignments
            existing_assignments = self.db.query(ExamSupervisor).join(Exam).filter(
                and_(
                    ExamSupervisor.teacher_id == supervisor_id,
                    func.date(Exam.exam_date) == exam_date.date(),
                    Exam.status.in_([ExamStatus.SCHEDULED, ExamStatus.CONFIRMED]),
                    ExamSupervisor.is_confirmed == True,
                    Exam.academic_year == self.current_academic_year
                )
            ).all()

            for assignment in existing_assignments:
                exam = assignment.exam
                if self._time_periods_overlap(
                    start_time, end_time,
                    exam.start_time, exam.end_time
                ):
                    conflicts.append({
                        'type': 'supervisor_conflict',
                        'severity': 'error',
                        'description': f'Supervisor {assignment.teacher.teacher_name} is assigned to: {exam.exam_name}',
                        'supervisor_id': supervisor_id,
                        'supervisor_name': assignment.teacher.teacher_name,
                        'conflicting_exam_id': exam.id,
                        'conflicting_exam_name': exam.exam_name
                    })

        return conflicts

    def _check_weekly_exam_limits(self, section_id: int, exam_date: datetime) -> List[Dict]:
        """Check weekly exam limits for students"""
        warnings = []

        # Get start and end of the week
        week_start = exam_date - timedelta(days=exam_date.weekday())
        week_end = week_start + timedelta(days=6)

        # Count exams for this section in the week
        weekly_exams = self.db.query(Exam).filter(
            and_(
                Exam.section_id == section_id,
                Exam.exam_date >= week_start,
                Exam.exam_date <= week_end,
                Exam.status.in_([ExamStatus.SCHEDULED, ExamStatus.CONFIRMED]),
                Exam.academic_year == self.current_academic_year
            )
        ).count()

        # Venezuelan K12 recommendation: max 5 exams per week
        if weekly_exams >= 5:
            warnings.append({
                'type': 'weekly_exam_limit',
                'severity': 'warning',
                'description': f'Students already have {weekly_exams} exams this week',
                'recommended_limit': 5,
                'current_count': weekly_exams
            })

        return warnings

    def _check_preparation_time(self, section_id: int, subject_id: int,
                              exam_date: datetime) -> List[Dict]:
        """Check minimum preparation time between exams"""
        warnings = []

        # Find recent exams for the same subject
        recent_exams = self.db.query(Exam).filter(
            and_(
                Exam.section_id == section_id,
                Exam.subject_id == subject_id,
                Exam.exam_date < exam_date,
                Exam.exam_date >= exam_date - timedelta(days=14),  # Last 2 weeks
                Exam.status.in_([ExamStatus.SCHEDULED, ExamStatus.CONFIRMED, ExamStatus.COMPLETED]),
                Exam.academic_year == self.current_academic_year
            )
        ).order_by(desc(Exam.exam_date)).first()

        if recent_exams:
            days_between = (exam_date.date() - recent_exams.exam_date.date()).days
            if days_between < 7:  # Minimum 1 week between subject exams
                warnings.append({
                    'type': 'insufficient_preparation_time',
                    'severity': 'warning',
                    'description': f'Only {days_between} days since last {recent_exams.subject.subject_name} exam',
                    'recommended_minimum': 7,
                    'actual_days': days_between,
                    'previous_exam': recent_exams.exam_name
                })

        return warnings

    def _check_room_capacity(self, classroom_id: int, section_id: int) -> List[Dict]:
        """Check if classroom capacity meets section enrollment"""
        warnings = []

        classroom = self.db.query(Classroom).get(classroom_id)
        section = self.db.query(Section).get(section_id)

        if classroom and section:
            if section.current_students > classroom.capacity:
                warnings.append({
                    'type': 'capacity_exceeded',
                    'severity': 'warning',
                    'description': f'Classroom capacity ({classroom.capacity}) < students ({section.current_students})',
                    'classroom_capacity': classroom.capacity,
                    'student_count': section.current_students,
                    'overflow_count': section.current_students - classroom.capacity
                })

        return warnings

    def _time_periods_overlap(self, start1: time, end1: time, start2: time, end2: time) -> bool:
        """Check if two time periods overlap"""
        return start1 < end2 and start2 < end1

    def _generate_scheduling_suggestions(self, exam_data: Dict,
                                       conflicts: List[Dict],
                                       warnings: List[Dict]) -> List[Dict]:
        """Generate suggestions to resolve conflicts"""
        suggestions = []

        # Suggest alternative time slots
        if any(c['type'] in ['student_time_conflict', 'classroom_conflict'] for c in conflicts):
            alternative_slots = self._find_alternative_time_slots(
                exam_data['section_id'],
                datetime.fromisoformat(exam_data['exam_date']),
                int(exam_data.get('duration_minutes', 120))
            )

            if alternative_slots:
                suggestions.append({
                    'type': 'alternative_times',
                    'description': 'Consider these alternative time slots',
                    'alternatives': alternative_slots[:3]  # Top 3 suggestions
                })

        # Suggest alternative classrooms
        if any(c['type'] == 'classroom_conflict' for c in conflicts):
            alternative_rooms = self._find_alternative_classrooms(
                exam_data['classroom_id'],
                datetime.fromisoformat(exam_data['exam_date']),
                datetime.strptime(exam_data['start_time'], '%H:%M').time(),
                datetime.strptime(exam_data['end_time'], '%H:%M').time()
            )

            if alternative_rooms:
                suggestions.append({
                    'type': 'alternative_classrooms',
                    'description': 'Available alternative classrooms',
                    'alternatives': alternative_rooms[:3]
                })

        # Suggest different dates for weekly limit issues
        if any(w['type'] == 'weekly_exam_limit' for w in warnings):
            suggestions.append({
                'type': 'reschedule_week',
                'description': 'Consider scheduling in a different week with fewer exams',
                'recommendation': 'Move to following week or reduce weekly exam load'
            })

        return suggestions

    def _find_alternative_time_slots(self, section_id: int, exam_date: datetime,
                                   duration_minutes: int) -> List[Dict]:
        """Find available alternative time slots"""
        alternatives = []

        # Venezuelan K12 typical exam hours: 7:00-12:00, 13:00-17:00
        time_slots = [
            (time(7, 0), time(9, 0)),    # Morning slot 1
            (time(9, 0), time(11, 0)),   # Morning slot 2
            (time(11, 0), time(12, 0)),  # Late morning
            (time(13, 0), time(15, 0)),  # Afternoon slot 1
            (time(15, 0), time(17, 0))   # Afternoon slot 2
        ]

        for start_time, end_time in time_slots:
            # Check if this slot is available
            conflicts = self._check_student_conflicts(section_id, exam_date, start_time, end_time)
            if not conflicts:
                alternatives.append({
                    'start_time': start_time.strftime('%H:%M'),
                    'end_time': end_time.strftime('%H:%M'),
                    'duration': f'{(datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).seconds // 60} minutes'
                })

        return alternatives

    def _find_alternative_classrooms(self, original_classroom_id: int,
                                   exam_date: datetime, start_time: time,
                                   end_time: time) -> List[Dict]:
        """Find available alternative classrooms"""
        alternatives = []

        # Get all classrooms except the conflicted one
        available_classrooms = self.db.query(Classroom).filter(
            and_(
                Classroom.id != original_classroom_id,
                Classroom.is_active == True
            )
        ).all()

        for classroom in available_classrooms:
            # Check if classroom is available
            conflicts = self._check_classroom_conflicts(
                classroom.id, exam_date, start_time, end_time
            )

            if not conflicts:
                alternatives.append({
                    'classroom_id': classroom.id,
                    'classroom_name': classroom.name,
                    'capacity': classroom.capacity,
                    'room_type': classroom.room_type.value
                })

        return alternatives

    # ============================================================================
    # SUPERVISOR ASSIGNMENT
    # ============================================================================

    def assign_exam_supervisors(self, exam_id: int, supervisor_preferences: Dict = None) -> Dict:
        """
        Automatically assign supervisors to an exam
        Considers availability, expertise, and workload balance
        """
        exam = self.db.query(Exam).get(exam_id)
        if not exam:
            return {'success': False, 'error': 'Exam not found'}

        # Determine supervisor requirements
        required_supervisors = self._calculate_supervisor_requirements(exam)

        # Find available supervisors
        available_supervisors = self._find_available_supervisors(
            exam.exam_date, exam.start_time, exam.end_time
        )

        # Score and rank supervisors
        ranked_supervisors = self._rank_supervisors_for_exam(
            exam, available_supervisors, supervisor_preferences
        )

        # Assign supervisors based on ranking
        assignments = []
        for i, supervisor_data in enumerate(ranked_supervisors[:required_supervisors]):
            role = SupervisorRole.PRIMARY if i == 0 else SupervisorRole.SECONDARY

            assignment = ExamSupervisor(
                exam_id=exam_id,
                teacher_id=supervisor_data['teacher_id'],
                supervisor_role=role,
                arrival_time=self._calculate_arrival_time(exam.start_time),
                departure_time=self._calculate_departure_time(exam.end_time),
                responsibilities=self._get_supervisor_responsibilities(role, exam),
                has_subject_expertise=supervisor_data['subject_expertise'],
                assigned_by='system_auto',
                supervision_hours=self._calculate_supervision_hours(exam)
            )

            self.db.add(assignment)
            assignments.append({
                'teacher_id': supervisor_data['teacher_id'],
                'teacher_name': supervisor_data['teacher_name'],
                'role': role.value,
                'score': supervisor_data['score']
            })

        try:
            self.db.commit()
            return {
                'success': True,
                'assignments': assignments,
                'total_assigned': len(assignments),
                'required': required_supervisors
            }
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}

    def _calculate_supervisor_requirements(self, exam: Exam) -> int:
        """Calculate number of supervisors needed based on exam size and type"""
        base_supervisors = 1

        # Additional supervisor for large exams
        if exam.enrolled_students > 30:
            base_supervisors += 1

        # Additional supervisor for final exams
        if exam.exam_type == ExamType.FINAL:
            base_supervisors += 1

        return min(base_supervisors, 3)  # Max 3 supervisors

    def _find_available_supervisors(self, exam_date: datetime,
                                  start_time: time, end_time: time) -> List[Dict]:
        """Find teachers available for supervision"""
        # Get all active teachers
        all_teachers = self.db.query(Teacher).filter(
            and_(
                Teacher.is_active == True,
                Teacher.academic_year == self.current_academic_year
            )
        ).all()

        available_supervisors = []

        for teacher in all_teachers:
            # Check if teacher is already assigned to supervise another exam
            existing_supervision = self.db.query(ExamSupervisor).join(Exam).filter(
                and_(
                    ExamSupervisor.teacher_id == teacher.id,
                    func.date(Exam.exam_date) == exam_date.date(),
                    ExamSupervisor.is_confirmed == True,
                    or_(
                        and_(Exam.start_time <= start_time, Exam.end_time > start_time),
                        and_(Exam.start_time < end_time, Exam.end_time >= end_time),
                        and_(Exam.start_time >= start_time, Exam.end_time <= end_time)
                    )
                )
            ).first()

            if not existing_supervision:
                available_supervisors.append({
                    'teacher_id': teacher.id,
                    'teacher_name': teacher.teacher_name,
                    'specialization': teacher.area_specialization,
                    'experience_years': teacher.years_experience or 0
                })

        return available_supervisors

    def _rank_supervisors_for_exam(self, exam: Exam, available_supervisors: List[Dict],
                                 preferences: Dict = None) -> List[Dict]:
        """Rank supervisors based on suitability for the exam"""
        scored_supervisors = []

        for supervisor in available_supervisors:
            score = 0

            # Base score
            score += 10

            # Experience bonus
            score += min(supervisor['experience_years'] * 2, 20)

            # Subject expertise bonus
            subject_expertise = self._check_subject_expertise(
                supervisor['teacher_id'], exam.subject_id
            )
            if subject_expertise:
                score += 30

            # Workload balance (prefer teachers with lighter supervision load)
            supervision_load = self._get_supervisor_workload(
                supervisor['teacher_id'], exam.exam_date
            )
            score -= supervision_load * 5  # Penalty for high workload

            # Specialization match
            if exam.subject.subject_category.value in supervisor['specialization'].lower():
                score += 15

            scored_supervisors.append({
                **supervisor,
                'score': score,
                'subject_expertise': subject_expertise
            })

        # Sort by score (highest first)
        return sorted(scored_supervisors, key=lambda x: x['score'], reverse=True)

    def _check_subject_expertise(self, teacher_id: int, subject_id: int) -> bool:
        """Check if teacher has expertise in the subject"""
        # This would check teacher_subjects relationship
        # For now, simplified check
        return True  # Assume all teachers can supervise

    def _get_supervisor_workload(self, teacher_id: int, exam_date: datetime) -> int:
        """Get supervisor's current workload for the week"""
        week_start = exam_date - timedelta(days=exam_date.weekday())
        week_end = week_start + timedelta(days=6)

        workload = self.db.query(ExamSupervisor).join(Exam).filter(
            and_(
                ExamSupervisor.teacher_id == teacher_id,
                Exam.exam_date >= week_start,
                Exam.exam_date <= week_end,
                ExamSupervisor.is_confirmed == True
            )
        ).count()

        return workload

    def _calculate_arrival_time(self, exam_start: time) -> time:
        """Calculate supervisor arrival time (30 minutes early)"""
        exam_datetime = datetime.combine(date.today(), exam_start)
        arrival_datetime = exam_datetime - timedelta(minutes=30)
        return arrival_datetime.time()

    def _calculate_departure_time(self, exam_end: time) -> time:
        """Calculate supervisor departure time (30 minutes after)"""
        exam_datetime = datetime.combine(date.today(), exam_end)
        departure_datetime = exam_datetime + timedelta(minutes=30)
        return departure_datetime.time()

    def _get_supervisor_responsibilities(self, role: SupervisorRole, exam: Exam) -> str:
        """Get role-specific responsibilities"""
        if role == SupervisorRole.PRIMARY:
            return "Supervisor principal: distribución de examen, control de tiempo, recogida de exámenes"
        else:
            return "Supervisor auxiliar: vigilancia, asistencia a estudiantes, apoyo al supervisor principal"

    def _calculate_supervision_hours(self, exam: Exam) -> float:
        """Calculate total supervision hours including prep and cleanup"""
        exam_duration = exam.duration_minutes / 60
        prep_cleanup = 1.0  # 1 hour for prep and cleanup
        return exam_duration + prep_cleanup