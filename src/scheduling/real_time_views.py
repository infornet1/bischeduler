"""
BiScheduler Real-Time Schedule Views
Live schedule updates and real-time conflict monitoring
Enhanced for Venezuelan K12 requirements
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import json

from src.auth.decorators import jwt_required, tenant_required, teacher_or_admin_required
from src.scheduling.services import ScheduleManager


# Create real-time views blueprint
realtime_bp = Blueprint('realtime', __name__, url_prefix='/api/schedule/realtime')


def get_schedule_manager(tenant_id: str) -> ScheduleManager:
    """Get ScheduleManager instance for tenant"""
    from flask import current_app

    tenant_manager = current_app.tenant_manager
    tenant = tenant_manager.get_tenant_by_id(tenant_id)

    if not tenant:
        raise ValueError('Tenant not found')

    return ScheduleManager(tenant.database_url)


@realtime_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_user_dashboard(tenant_id, user_id):
    """
    Get personalized real-time dashboard for user

    Response:
        {
            "user_type": "teacher",
            "current_class": {...},
            "next_class": {...},
            "today_schedule": [...],
            "conflicts": [...],
            "workload_status": {...}
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import ScheduleAssignment, Teacher, DayOfWeek
            from src.models.auth import User

            # Get user information
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'message': f'User {user_id} does not exist'
                }), 404

            dashboard_data = {
                'user_id': user_id,
                'user_role': user.role,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            # For teachers, get schedule and workload information
            if user.role == 'teacher':
                # Find teacher record
                teacher = session.query(Teacher).filter_by(
                    user_id=str(user_id),  # Assuming user_id is stored in teacher
                    academic_year=schedule_manager.academic_year
                ).first()

                if teacher:
                    dashboard_data.update(
                        get_teacher_dashboard_data(session, schedule_manager, teacher.id)
                    )
                else:
                    dashboard_data['message'] = 'Teacher profile not found'

            # For administrators, get general overview
            elif user.role in ['school_admin', 'academic_coordinator']:
                dashboard_data.update(
                    get_admin_dashboard_data(session, schedule_manager)
                )

            return jsonify(dashboard_data), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get dashboard',
            'message': str(e)
        }), 500


def get_teacher_dashboard_data(session, schedule_manager: ScheduleManager, teacher_id: int) -> Dict:
    """Get dashboard data specific to teachers"""
    from src.models.tenant import ScheduleAssignment, DayOfWeek
    import datetime as dt

    now = datetime.now()
    today = now.strftime('%A').lower()

    # Map English days to Spanish
    day_mapping = {
        'monday': 'lunes',
        'tuesday': 'martes',
        'wednesday': 'miercoles',
        'thursday': 'jueves',
        'friday': 'viernes'
    }

    today_spanish = day_mapping.get(today)

    teacher_data = {
        'user_type': 'teacher',
        'current_class': None,
        'next_class': None,
        'today_schedule': [],
        'conflicts': [],
        'workload_status': {}
    }

    if today_spanish:
        try:
            day_enum = DayOfWeek(today_spanish)

            # Get today's schedule for teacher
            today_assignments = session.query(ScheduleAssignment).filter_by(
                teacher_id=teacher_id,
                day_of_week=day_enum,
                academic_year=schedule_manager.academic_year,
                is_active=True
            ).order_by(ScheduleAssignment.time_period_id).all()

            current_time = now.time()
            current_class = None
            next_class = None

            for assignment in today_assignments:
                class_info = {
                    'assignment_id': assignment.id,
                    'subject': assignment.subject.subject_name,
                    'section': assignment.section.name,
                    'classroom': assignment.classroom.name,
                    'start_time': assignment.time_period.start_time.strftime('%H:%M'),
                    'end_time': assignment.time_period.end_time.strftime('%H:%M'),
                    'is_current': False,
                    'is_next': False
                }

                # Check if this is current or next class
                if (assignment.time_period.start_time <= current_time <= assignment.time_period.end_time):
                    current_class = class_info.copy()
                    current_class['is_current'] = True
                elif assignment.time_period.start_time > current_time and not next_class:
                    next_class = class_info.copy()
                    next_class['is_next'] = True

                teacher_data['today_schedule'].append(class_info)

            teacher_data['current_class'] = current_class
            teacher_data['next_class'] = next_class

            # Get teacher conflicts
            teacher_conflicts = []
            for assignment in today_assignments:
                conflicts = schedule_manager._detect_assignment_conflicts(session, assignment)
                for conflict in conflicts:
                    conflict['assignment_id'] = assignment.id
                    teacher_conflicts.append(conflict)

            teacher_data['conflicts'] = teacher_conflicts

        except ValueError:
            # Today is not a weekday
            teacher_data['message'] = 'No classes scheduled for today'

    # Get workload status
    teacher_result = schedule_manager.get_teacher_schedule(teacher_id)
    if teacher_result['status'] == 'success':
        teacher_data['workload_status'] = teacher_result['workload']

    return teacher_data


def get_admin_dashboard_data(session, schedule_manager: ScheduleManager) -> Dict:
    """Get dashboard data for administrators"""
    from src.models.tenant import ScheduleAssignment, ScheduleConflict, Teacher, Section

    admin_data = {
        'user_type': 'admin',
        'platform_overview': {},
        'critical_conflicts': [],
        'teacher_alerts': [],
        'schedule_completion': {}
    }

    try:
        # Platform overview
        total_assignments = session.query(ScheduleAssignment).filter_by(
            academic_year=schedule_manager.academic_year,
            is_active=True
        ).count()

        total_conflicts = session.query(ScheduleConflict).filter_by(
            academic_year=schedule_manager.academic_year,
            status='active'
        ).count()

        critical_conflicts = session.query(ScheduleConflict).filter_by(
            academic_year=schedule_manager.academic_year,
            severity='critical',
            status='active'
        ).count()

        admin_data['platform_overview'] = {
            'total_assignments': total_assignments,
            'total_conflicts': total_conflicts,
            'critical_conflicts': critical_conflicts,
            'conflict_rate': round((total_conflicts / total_assignments * 100) if total_assignments > 0 else 0, 2)
        }

        # Recent critical conflicts
        recent_conflicts = session.query(ScheduleConflict).filter_by(
            academic_year=schedule_manager.academic_year,
            severity='critical',
            status='active'
        ).order_by(ScheduleConflict.detected_at.desc()).limit(5).all()

        admin_data['critical_conflicts'] = [{
            'id': conflict.id,
            'type': conflict.conflict_type,
            'description': conflict.description,
            'detected_at': conflict.detected_at.isoformat()
        } for conflict in recent_conflicts]

        # Teacher workload alerts
        overloaded_teachers = session.query(Teacher).filter(
            Teacher.current_weekly_hours > Teacher.max_weekly_hours,
            Teacher.academic_year == schedule_manager.academic_year,
            Teacher.is_active == True
        ).limit(5).all()

        admin_data['teacher_alerts'] = [{
            'teacher_id': teacher.id,
            'teacher_name': teacher.teacher_name,
            'current_hours': teacher.current_weekly_hours,
            'max_hours': teacher.max_weekly_hours,
            'excess_hours': teacher.current_weekly_hours - teacher.max_weekly_hours
        } for teacher in overloaded_teachers]

        # Schedule completion by section
        sections = session.query(Section).filter_by(
            academic_year=schedule_manager.academic_year,
            is_active=True
        ).all()

        completion_data = []
        for section in sections:
            section_assignments = session.query(ScheduleAssignment).filter_by(
                section_id=section.id,
                academic_year=schedule_manager.academic_year,
                is_active=True
            ).count()

            # Estimate expected assignments (5 days × 8 periods = 40 slots)
            expected_assignments = 40
            completion_pct = min(100, round((section_assignments / expected_assignments * 100), 1))

            completion_data.append({
                'section_id': section.id,
                'section_name': section.name,
                'assignments_count': section_assignments,
                'completion_percentage': completion_pct
            })

        admin_data['schedule_completion'] = completion_data

    except Exception as e:
        admin_data['error'] = f"Error getting admin data: {str(e)}"

    return admin_data


@realtime_bp.route('/conflicts/live', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_live_conflicts(tenant_id):
    """
    Get real-time conflict updates

    Query parameters:
        - since: ISO timestamp for incremental updates
        - severity: Filter by conflict severity

    Response:
        {
            "conflicts": [...],
            "last_updated": "2025-01-01T00:00:00Z",
            "total_count": 5
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import ScheduleConflict

            # Get query parameters
            since = request.args.get('since')
            severity_filter = request.args.get('severity')

            query = session.query(ScheduleConflict).filter_by(
                academic_year=schedule_manager.academic_year,
                status='active'
            )

            # Apply filters
            if since:
                try:
                    since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                    query = query.filter(ScheduleConflict.detected_at > since_dt)
                except ValueError:
                    return jsonify({
                        'error': 'Invalid since timestamp',
                        'message': 'Use ISO format: YYYY-MM-DDTHH:MM:SSZ'
                    }), 400

            if severity_filter:
                query = query.filter(ScheduleConflict.severity == severity_filter)

            conflicts = query.order_by(ScheduleConflict.detected_at.desc()).all()

            conflict_data = []
            for conflict in conflicts:
                conflict_data.append({
                    'id': conflict.id,
                    'type': conflict.conflict_type,
                    'severity': conflict.severity,
                    'description': conflict.description,
                    'assignment_1_id': conflict.assignment_1_id,
                    'assignment_2_id': conflict.assignment_2_id,
                    'suggested_resolution': conflict.suggested_resolution,
                    'detected_at': conflict.detected_at.isoformat(),
                    'auto_resolvable': conflict.auto_resolvable
                })

            return jsonify({
                'conflicts': conflict_data,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_count': len(conflict_data),
                'filters_applied': {
                    'since': since,
                    'severity': severity_filter
                }
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get live conflicts',
            'message': str(e)
        }), 500


@realtime_bp.route('/workload/alerts', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_workload_alerts(tenant_id):
    """
    Get real-time teacher workload alerts

    Response:
        {
            "alerts": [
                {
                    "teacher_id": 1,
                    "teacher_name": "MARIA NIETO",
                    "alert_type": "overloaded",
                    "current_hours": 45,
                    "max_hours": 40,
                    "severity": "critical"
                }
            ]
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import Teacher, TeacherWorkload

            # Get teachers with workload issues
            teachers = session.query(Teacher).filter_by(
                academic_year=schedule_manager.academic_year,
                is_active=True
            ).all()

            alerts = []
            for teacher in teachers:
                current_hours = teacher.current_weekly_hours or 0
                max_hours = teacher.max_weekly_hours or 40

                # Check for overload
                if current_hours > max_hours:
                    alerts.append({
                        'teacher_id': teacher.id,
                        'teacher_name': teacher.teacher_name,
                        'alert_type': 'overloaded',
                        'current_hours': current_hours,
                        'max_hours': max_hours,
                        'excess_hours': current_hours - max_hours,
                        'severity': 'critical' if current_hours > max_hours * 1.2 else 'warning'
                    })

                # Check for underutilization
                elif current_hours < max_hours * 0.5:
                    alerts.append({
                        'teacher_id': teacher.id,
                        'teacher_name': teacher.teacher_name,
                        'alert_type': 'underutilized',
                        'current_hours': current_hours,
                        'max_hours': max_hours,
                        'utilization_percentage': round((current_hours / max_hours * 100), 1),
                        'severity': 'info'
                    })

            return jsonify({
                'alerts': alerts,
                'total_alerts': len(alerts),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get workload alerts',
            'message': str(e)
        }), 500


@realtime_bp.route('/schedule/changes', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_recent_changes(tenant_id):
    """
    Get recent schedule changes for real-time updates

    Query parameters:
        - since: ISO timestamp for incremental updates
        - limit: Maximum number of changes to return (default: 50)

    Response:
        {
            "changes": [
                {
                    "assignment_id": 123,
                    "change_type": "created",
                    "teacher_name": "MARIA NIETO",
                    "subject_name": "MATEMÁTICAS",
                    "section_name": "1er año A",
                    "changed_at": "2025-01-01T00:00:00Z"
                }
            ]
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import ScheduleAssignment

            # Get query parameters
            since = request.args.get('since')
            limit = int(request.args.get('limit', 50))

            query = session.query(ScheduleAssignment).filter_by(
                academic_year=schedule_manager.academic_year
            )

            # Apply since filter
            if since:
                try:
                    since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                    query = query.filter(ScheduleAssignment.created_at > since_dt)
                except ValueError:
                    return jsonify({
                        'error': 'Invalid since timestamp',
                        'message': 'Use ISO format: YYYY-MM-DDTHH:MM:SSZ'
                    }), 400

            assignments = query.order_by(
                ScheduleAssignment.created_at.desc()
            ).limit(limit).all()

            changes = []
            for assignment in assignments:
                change_type = 'deleted' if not assignment.is_active else 'created'

                changes.append({
                    'assignment_id': assignment.id,
                    'change_type': change_type,
                    'teacher_name': assignment.teacher.teacher_name,
                    'subject_name': assignment.subject.subject_name,
                    'section_name': assignment.section.name,
                    'classroom_name': assignment.classroom.name,
                    'day_of_week': assignment.day_of_week.value,
                    'time_period': assignment.time_period.period_name,
                    'changed_at': assignment.created_at.isoformat(),
                    'changed_by': assignment.created_by
                })

            return jsonify({
                'changes': changes,
                'total_changes': len(changes),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'since': since,
                'limit': limit
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get recent changes',
            'message': str(e)
        }), 500