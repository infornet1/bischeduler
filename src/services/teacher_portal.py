"""
BiScheduler Teacher Portal Service Layer
Phase 4: Teacher Self-Service Portal (CRITICAL)

Handles teacher preferences, availability, schedule viewing, and change requests
with Venezuelan K12 compliance and preference scoring algorithms.

Key Features:
- Preference scoring algorithm (40% time, 30% day, 20% subject, 10% classroom)
- Teacher dashboard with personal schedule viewer
- Preference submission and management system
- Change request workflow
- Workload statistics and satisfaction metrics
"""

from datetime import datetime, timezone, time, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json

from ..models.tenant import (
    Teacher, TeacherPreference, TeacherAvailability, ScheduleChangeRequest,
    TeacherDashboardStats, ScheduleAssignment, TimePeriod, Subject, Classroom,
    Section, PreferenceType, PreferenceLevel, DayOfWeek
)


class TeacherPortalService:
    """
    Core service for teacher self-service portal functionality
    Implements Venezuelan K12 teacher preference and scheduling features
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.current_academic_year = "2025-2026"

    # ============================================================================
    # TEACHER PREFERENCE MANAGEMENT
    # ============================================================================

    def get_teacher_preferences(self, teacher_id: int) -> Dict:
        """Get all preferences for a teacher with categorization"""
        preferences = self.db.query(TeacherPreference).filter(
            and_(
                TeacherPreference.teacher_id == teacher_id,
                TeacherPreference.is_active == True,
                TeacherPreference.academic_year == self.current_academic_year
            )
        ).all()

        # Organize by preference type
        organized_prefs = {
            'time_slots': [],
            'days': [],
            'subjects': [],
            'classrooms': [],
            'sections': []
        }

        for pref in preferences:
            pref_data = {
                'id': pref.id,
                'level': pref.preference_level.value,
                'weight_score': pref.weight_score,
                'final_score': pref.final_score,
                'reason': pref.reason,
                'is_approved': pref.is_approved,
                'created_at': pref.created_at
            }

            if pref.preference_type == PreferenceType.TIME_SLOT and pref.time_period:
                pref_data['time_period'] = {
                    'id': pref.time_period.id,
                    'name': pref.time_period.period_name,
                    'start_time': pref.time_period.start_time.strftime('%H:%M'),
                    'end_time': pref.time_period.end_time.strftime('%H:%M')
                }
                organized_prefs['time_slots'].append(pref_data)

            elif pref.preference_type == PreferenceType.DAY_OF_WEEK:
                pref_data['day'] = pref.day_of_week.value
                organized_prefs['days'].append(pref_data)

            elif pref.preference_type == PreferenceType.SUBJECT and pref.subject:
                pref_data['subject'] = {
                    'id': pref.subject.id,
                    'name': pref.subject.subject_name,
                    'short_name': pref.subject.short_name
                }
                organized_prefs['subjects'].append(pref_data)

            elif pref.preference_type == PreferenceType.CLASSROOM and pref.classroom:
                pref_data['classroom'] = {
                    'id': pref.classroom.id,
                    'name': pref.classroom.name,
                    'capacity': pref.classroom.capacity,
                    'room_type': pref.classroom.room_type.value
                }
                organized_prefs['classrooms'].append(pref_data)

        return organized_prefs

    def save_teacher_preference(self, teacher_id: int, preference_data: Dict) -> Dict:
        """Save or update teacher preference with validation"""
        try:
            # Validate preference data
            if 'preference_type' not in preference_data or 'preference_level' not in preference_data:
                return {'success': False, 'error': 'Missing required fields'}

            pref_type = PreferenceType(preference_data['preference_type'])
            pref_level = PreferenceLevel(preference_data['preference_level'])

            # Check for existing preference of same type and target
            existing_pref = self._find_existing_preference(teacher_id, preference_data)

            if existing_pref:
                # Update existing preference
                existing_pref.preference_level = pref_level
                existing_pref.reason = preference_data.get('reason', '')
                existing_pref.updated_at = datetime.now(timezone.utc)
                existing_pref.is_approved = False  # Requires re-approval
                pref = existing_pref
            else:
                # Create new preference
                pref = TeacherPreference(
                    teacher_id=teacher_id,
                    preference_type=pref_type,
                    preference_level=pref_level,
                    reason=preference_data.get('reason', ''),
                    academic_year=self.current_academic_year
                )

                # Set target reference based on type
                if pref_type == PreferenceType.TIME_SLOT:
                    pref.time_period_id = preference_data.get('time_period_id')
                elif pref_type == PreferenceType.DAY_OF_WEEK:
                    pref.day_of_week = DayOfWeek(preference_data.get('day_of_week'))
                elif pref_type == PreferenceType.SUBJECT:
                    pref.subject_id = preference_data.get('subject_id')
                elif pref_type == PreferenceType.CLASSROOM:
                    pref.classroom_id = preference_data.get('classroom_id')

                self.db.add(pref)

            self.db.commit()

            return {
                'success': True,
                'preference_id': pref.id,
                'final_score': pref.final_score,
                'requires_approval': not pref.is_approved
            }

        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}

    def _find_existing_preference(self, teacher_id: int, pref_data: Dict) -> Optional[TeacherPreference]:
        """Find existing preference for same teacher, type, and target"""
        query = self.db.query(TeacherPreference).filter(
            and_(
                TeacherPreference.teacher_id == teacher_id,
                TeacherPreference.preference_type == PreferenceType(pref_data['preference_type']),
                TeacherPreference.is_active == True,
                TeacherPreference.academic_year == self.current_academic_year
            )
        )

        # Add specific target filter based on type
        pref_type = PreferenceType(pref_data['preference_type'])
        if pref_type == PreferenceType.TIME_SLOT:
            query = query.filter(TeacherPreference.time_period_id == pref_data.get('time_period_id'))
        elif pref_type == PreferenceType.DAY_OF_WEEK:
            query = query.filter(TeacherPreference.day_of_week == DayOfWeek(pref_data.get('day_of_week')))
        elif pref_type == PreferenceType.SUBJECT:
            query = query.filter(TeacherPreference.subject_id == pref_data.get('subject_id'))
        elif pref_type == PreferenceType.CLASSROOM:
            query = query.filter(TeacherPreference.classroom_id == pref_data.get('classroom_id'))

        return query.first()

    # ============================================================================
    # TEACHER SCHEDULE VIEWING
    # ============================================================================

    def get_teacher_schedule(self, teacher_id: int, week_offset: int = 0) -> Dict:
        """Get teacher's current schedule in Venezuelan format"""
        teacher = self.db.query(Teacher).get(teacher_id)
        if not teacher:
            return {'error': 'Teacher not found'}

        # Get all time periods for the day structure
        time_periods = self.db.query(TimePeriod).filter(
            and_(
                TimePeriod.academic_year == self.current_academic_year,
                TimePeriod.is_active == True
            )
        ).order_by(TimePeriod.display_order).all()

        # Get teacher's assignments
        assignments = self.db.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.teacher_id == teacher_id,
                ScheduleAssignment.academic_year == self.current_academic_year,
                ScheduleAssignment.is_active == True
            )
        ).all()

        # Build schedule grid (time periods x days)
        schedule_grid = {}
        days = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']

        for period in time_periods:
            schedule_grid[period.id] = {
                'period_info': {
                    'name': period.period_name,
                    'start_time': period.start_time.strftime('%H:%M'),
                    'end_time': period.end_time.strftime('%H:%M'),
                    'is_break': period.is_break,
                    'duration': period.duration_minutes
                },
                'assignments': {}
            }

            for day in days:
                schedule_grid[period.id]['assignments'][day] = None

        # Fill in assignments
        for assignment in assignments:
            period_id = assignment.time_period_id
            day = assignment.day_of_week.value

            if period_id in schedule_grid:
                schedule_grid[period_id]['assignments'][day] = {
                    'id': assignment.id,
                    'subject': assignment.subject.subject_name,
                    'subject_short': assignment.subject.short_name,
                    'section': assignment.section.name,
                    'classroom': assignment.classroom.name,
                    'classroom_type': assignment.classroom.room_type.value,
                    'assignment_type': assignment.assignment_type,
                    'is_locked': assignment.is_locked,
                    'conflict_status': assignment.conflict_status
                }

        return {
            'teacher': {
                'id': teacher.id,
                'name': teacher.teacher_name,
                'specialization': teacher.area_specialization
            },
            'schedule_grid': schedule_grid,
            'summary': self._calculate_schedule_summary(assignments),
            'week_offset': week_offset
        }

    def _calculate_schedule_summary(self, assignments: List[ScheduleAssignment]) -> Dict:
        """Calculate summary statistics for teacher's schedule"""
        total_hours = 0
        subjects = set()
        sections = set()
        classrooms = set()
        daily_hours = {day.value: 0 for day in DayOfWeek}

        for assignment in assignments:
            if not assignment.time_period.is_break:
                total_hours += assignment.time_period.duration_minutes / 60
                subjects.add(assignment.subject.subject_name)
                sections.add(assignment.section.name)
                classrooms.add(assignment.classroom.name)
                daily_hours[assignment.day_of_week.value] += assignment.time_period.duration_minutes / 60

        return {
            'total_weekly_hours': round(total_hours, 1),
            'total_subjects': len(subjects),
            'total_sections': len(sections),
            'total_classrooms': len(classrooms),
            'daily_hours': daily_hours,
            'subjects_list': list(subjects),
            'sections_list': list(sections)
        }

    # ============================================================================
    # TEACHER DASHBOARD STATISTICS
    # ============================================================================

    def get_teacher_dashboard_stats(self, teacher_id: int) -> Dict:
        """Get comprehensive dashboard statistics for teacher"""
        teacher = self.db.query(Teacher).get(teacher_id)
        if not teacher:
            return {'error': 'Teacher not found'}

        # Get or create dashboard stats record
        stats = self.db.query(TeacherDashboardStats).filter(
            and_(
                TeacherDashboardStats.teacher_id == teacher_id,
                TeacherDashboardStats.academic_year == self.current_academic_year
            )
        ).first()

        if not stats:
            stats = self._create_teacher_dashboard_stats(teacher_id)

        # Calculate current preference satisfaction
        preference_scores = self._calculate_preference_satisfaction(teacher_id)

        # Update stats with latest calculations
        stats.preference_satisfaction_score = preference_scores['overall']
        stats.time_preference_score = preference_scores['time']
        stats.day_preference_score = preference_scores['day']
        stats.subject_preference_score = preference_scores['subject']
        stats.classroom_preference_score = preference_scores['classroom']
        stats.last_calculated = datetime.now(timezone.utc)

        self.db.commit()

        return {
            'teacher_info': {
                'name': teacher.teacher_name,
                'specialization': teacher.area_specialization,
                'max_weekly_hours': teacher.max_weekly_hours
            },
            'workload': {
                'total_weekly_hours': stats.total_weekly_hours,
                'total_classes': stats.total_classes,
                'total_subjects': stats.total_subjects,
                'total_sections': stats.total_sections,
                'workload_balance_score': float(stats.workload_balance_score),
                'consecutive_classes_max': stats.consecutive_classes_max,
                'free_periods_per_week': stats.free_periods_per_week
            },
            'preferences': {
                'overall_satisfaction': float(stats.preference_satisfaction_score),
                'time_satisfaction': float(stats.time_preference_score),
                'day_satisfaction': float(stats.day_preference_score),
                'subject_satisfaction': float(stats.subject_preference_score),
                'classroom_satisfaction': float(stats.classroom_preference_score)
            },
            'change_requests': {
                'total': stats.total_change_requests,
                'approved': stats.approved_change_requests,
                'pending': stats.pending_change_requests,
                'approval_rate': round((stats.approved_change_requests / max(1, stats.total_change_requests)) * 100, 1)
            },
            'last_updated': stats.last_calculated.isoformat()
        }

    def _create_teacher_dashboard_stats(self, teacher_id: int) -> TeacherDashboardStats:
        """Create initial dashboard stats record for teacher"""
        stats = TeacherDashboardStats(
            teacher_id=teacher_id,
            academic_year=self.current_academic_year
        )
        self.db.add(stats)
        self.db.commit()
        return stats

    def _calculate_preference_satisfaction(self, teacher_id: int) -> Dict:
        """Calculate how well current schedule satisfies teacher preferences"""
        # Get teacher's preferences
        preferences = self.db.query(TeacherPreference).filter(
            and_(
                TeacherPreference.teacher_id == teacher_id,
                TeacherPreference.is_active == True,
                TeacherPreference.is_approved == True,
                TeacherPreference.academic_year == self.current_academic_year
            )
        ).all()

        # Get teacher's current assignments
        assignments = self.db.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.teacher_id == teacher_id,
                ScheduleAssignment.academic_year == self.current_academic_year,
                ScheduleAssignment.is_active == True
            )
        ).all()

        if not assignments:
            return {'overall': 0, 'time': 0, 'day': 0, 'subject': 0, 'classroom': 0}

        # Calculate satisfaction by preference type
        satisfaction_scores = {
            'time': self._calculate_time_satisfaction(preferences, assignments),
            'day': self._calculate_day_satisfaction(preferences, assignments),
            'subject': self._calculate_subject_satisfaction(preferences, assignments),
            'classroom': self._calculate_classroom_satisfaction(preferences, assignments)
        }

        # Calculate weighted overall satisfaction (40% time, 30% day, 20% subject, 10% classroom)
        overall = (
            satisfaction_scores['time'] * 0.40 +
            satisfaction_scores['day'] * 0.30 +
            satisfaction_scores['subject'] * 0.20 +
            satisfaction_scores['classroom'] * 0.10
        )

        return {
            'overall': round(overall, 2),
            'time': round(satisfaction_scores['time'], 2),
            'day': round(satisfaction_scores['day'], 2),
            'subject': round(satisfaction_scores['subject'], 2),
            'classroom': round(satisfaction_scores['classroom'], 2)
        }

    def _calculate_time_satisfaction(self, preferences: List[TeacherPreference], assignments: List[ScheduleAssignment]) -> float:
        """Calculate satisfaction score for time slot preferences"""
        time_prefs = [p for p in preferences if p.preference_type == PreferenceType.TIME_SLOT]
        if not time_prefs:
            return 50.0  # Neutral score when no preferences

        total_score = 0
        total_assignments = len(assignments)

        for assignment in assignments:
            period_id = assignment.time_period_id
            period_prefs = [p for p in time_prefs if p.time_period_id == period_id]

            if period_prefs:
                # Use the preference score (convert -10 to +10 range to 0-100)
                score = ((period_prefs[0].weight_score + 10) / 20) * 100
                total_score += score
            else:
                # Neutral score for periods with no preference
                total_score += 50

        return total_score / total_assignments if total_assignments > 0 else 50.0

    def _calculate_day_satisfaction(self, preferences: List[TeacherPreference], assignments: List[ScheduleAssignment]) -> float:
        """Calculate satisfaction score for day preferences"""
        day_prefs = [p for p in preferences if p.preference_type == PreferenceType.DAY_OF_WEEK]
        if not day_prefs:
            return 50.0

        total_score = 0
        total_assignments = len(assignments)

        for assignment in assignments:
            day = assignment.day_of_week
            day_prefs_for_day = [p for p in day_prefs if p.day_of_week == day]

            if day_prefs_for_day:
                score = ((day_prefs_for_day[0].weight_score + 10) / 20) * 100
                total_score += score
            else:
                total_score += 50

        return total_score / total_assignments if total_assignments > 0 else 50.0

    def _calculate_subject_satisfaction(self, preferences: List[TeacherPreference], assignments: List[ScheduleAssignment]) -> float:
        """Calculate satisfaction score for subject preferences"""
        subject_prefs = [p for p in preferences if p.preference_type == PreferenceType.SUBJECT]
        if not subject_prefs:
            return 50.0

        total_score = 0
        total_assignments = len(assignments)

        for assignment in assignments:
            subject_id = assignment.subject_id
            subject_prefs_for_subject = [p for p in subject_prefs if p.subject_id == subject_id]

            if subject_prefs_for_subject:
                score = ((subject_prefs_for_subject[0].weight_score + 10) / 20) * 100
                total_score += score
            else:
                total_score += 50

        return total_score / total_assignments if total_assignments > 0 else 50.0

    def _calculate_classroom_satisfaction(self, preferences: List[TeacherPreference], assignments: List[ScheduleAssignment]) -> float:
        """Calculate satisfaction score for classroom preferences"""
        classroom_prefs = [p for p in preferences if p.preference_type == PreferenceType.CLASSROOM]
        if not classroom_prefs:
            return 50.0

        total_score = 0
        total_assignments = len(assignments)

        for assignment in assignments:
            classroom_id = assignment.classroom_id
            classroom_prefs_for_room = [p for p in classroom_prefs if p.classroom_id == classroom_id]

            if classroom_prefs_for_room:
                score = ((classroom_prefs_for_room[0].weight_score + 10) / 20) * 100
                total_score += score
            else:
                total_score += 50

        return total_score / total_assignments if total_assignments > 0 else 50.0

    # ============================================================================
    # REFERENCE DATA FOR TEACHER PORTAL
    # ============================================================================

    def get_portal_reference_data(self) -> Dict:
        """Get all reference data needed for teacher portal forms"""
        time_periods = self.db.query(TimePeriod).filter(
            and_(
                TimePeriod.academic_year == self.current_academic_year,
                TimePeriod.is_active == True,
                TimePeriod.is_break == False
            )
        ).order_by(TimePeriod.display_order).all()

        subjects = self.db.query(Subject).filter(
            and_(
                Subject.academic_year == self.current_academic_year,
                Subject.is_active == True
            )
        ).order_by(Subject.subject_name).all()

        classrooms = self.db.query(Classroom).filter(
            Classroom.is_active == True
        ).order_by(Classroom.name).all()

        return {
            'time_periods': [
                {
                    'id': tp.id,
                    'name': tp.period_name,
                    'start_time': tp.start_time.strftime('%H:%M'),
                    'end_time': tp.end_time.strftime('%H:%M'),
                    'display': f"{tp.period_name} ({tp.start_time.strftime('%H:%M')}-{tp.end_time.strftime('%H:%M')})"
                }
                for tp in time_periods
            ],
            'days_of_week': [
                {'value': 'lunes', 'label': 'Lunes'},
                {'value': 'martes', 'label': 'Martes'},
                {'value': 'miercoles', 'label': 'Miércoles'},
                {'value': 'jueves', 'label': 'Jueves'},
                {'value': 'viernes', 'label': 'Viernes'}
            ],
            'subjects': [
                {
                    'id': s.id,
                    'name': s.subject_name,
                    'short_name': s.short_name,
                    'category': s.subject_category.value
                }
                for s in subjects
            ],
            'classrooms': [
                {
                    'id': c.id,
                    'name': c.name,
                    'capacity': c.capacity,
                    'type': c.room_type.value,
                    'display': f"{c.name} (Cap: {c.capacity})"
                }
                for c in classrooms
            ],
            'preference_levels': [
                {'value': 'avoid', 'label': 'Evitar', 'score': -10, 'color': 'danger'},
                {'value': 'dislike', 'label': 'No Prefiero', 'score': -5, 'color': 'warning'},
                {'value': 'neutral', 'label': 'Neutral', 'score': 0, 'color': 'secondary'},
                {'value': 'like', 'label': 'Me Gusta', 'score': 5, 'color': 'info'},
                {'value': 'prefer', 'label': 'Prefiero', 'score': 10, 'color': 'success'}
            ]
        }