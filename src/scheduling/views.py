"""
BiScheduler Schedule Management API Views
RESTful endpoints for Venezuelan K12 schedule management
Enhanced with conflict detection and workload validation
"""

from flask import Blueprint, request, jsonify, g
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from datetime import datetime, timezone
import json

from src.auth.decorators import (
    jwt_required, tenant_required, school_admin_required,
    teacher_or_admin_required, permissions_required, audit_action
)
from src.scheduling.services import ScheduleManager
from src.scheduling.export_import import VenezuelanScheduleExporter, VenezuelanScheduleImporter, create_schedule_template_excel
from src.models.tenant import DayOfWeek


# Create scheduling blueprint
scheduling_bp = Blueprint('scheduling', __name__, url_prefix='/api/schedule')


def get_schedule_manager(tenant_id: str) -> ScheduleManager:
    """Get ScheduleManager instance for tenant"""
    from flask import current_app

    # Get tenant database URL
    tenant_manager = current_app.tenant_manager
    tenant = tenant_manager.get_tenant_by_id(tenant_id)

    if not tenant:
        raise NotFound('Tenant not found')

    return ScheduleManager(tenant.database_url)


@scheduling_bp.route('/assignments', methods=['POST'])
@jwt_required
@tenant_required('tenant_id')
@permissions_required('manage_schedules')
@audit_action('create_schedule_assignment', 'schedule')
def create_assignment(tenant_id):
    """
    Create a new schedule assignment

    Request JSON:
        {
            "teacher_id": 1,
            "subject_id": 2,
            "section_id": 3,
            "classroom_id": 4,
            "time_period_id": 5,
            "day_of_week": "lunes",
            "validate_conflicts": true
        }

    Response:
        {
            "status": "success",
            "assignment": {...},
            "conflicts": []
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'JSON data required'}), 400

        # Validate required fields
        required_fields = [
            'teacher_id', 'subject_id', 'section_id',
            'classroom_id', 'time_period_id', 'day_of_week'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing field: {field}',
                    'message': f'{field} is required'
                }), 400

        # Validate day of week
        try:
            day_of_week = DayOfWeek(data['day_of_week'])
        except ValueError:
            return jsonify({
                'error': 'Invalid day_of_week',
                'message': f'Must be one of: {[day.value for day in DayOfWeek]}'
            }), 400

        # Get schedule manager
        schedule_manager = get_schedule_manager(tenant_id)

        # Create assignment
        result = schedule_manager.create_schedule_assignment(
            teacher_id=data['teacher_id'],
            subject_id=data['subject_id'],
            section_id=data['section_id'],
            classroom_id=data['classroom_id'],
            time_period_id=data['time_period_id'],
            day_of_week=day_of_week,
            created_by=g.current_user.get('email'),
            validate_conflicts=data.get('validate_conflicts', True)
        )

        if result['status'] == 'error':
            return jsonify(result), 400

        return jsonify(result), 201

    except Exception as e:
        return jsonify({
            'error': 'Assignment creation failed',
            'message': str(e)
        }), 500


@scheduling_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_assignment(tenant_id, assignment_id):
    """
    Get specific schedule assignment

    Response:
        {
            "assignment": {
                "id": 1,
                "teacher": {...},
                "subject": {...},
                "section": {...},
                "classroom": {...},
                "time_period": {...},
                "day_of_week": "lunes"
            }
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import ScheduleAssignment

            assignment = session.query(ScheduleAssignment).filter_by(
                id=assignment_id,
                academic_year=schedule_manager.academic_year
            ).first()

            if not assignment:
                return jsonify({
                    'error': 'Assignment not found',
                    'message': f'Assignment {assignment_id} does not exist'
                }), 404

            return jsonify({
                'assignment': {
                    'id': assignment.id,
                    'teacher': {
                        'id': assignment.teacher.id,
                        'name': assignment.teacher.teacher_name
                    },
                    'subject': {
                        'id': assignment.subject.id,
                        'name': assignment.subject.subject_name
                    },
                    'section': {
                        'id': assignment.section.id,
                        'name': assignment.section.name
                    },
                    'classroom': {
                        'id': assignment.classroom.id,
                        'name': assignment.classroom.name
                    },
                    'time_period': {
                        'id': assignment.time_period.id,
                        'name': assignment.time_period.period_name,
                        'start_time': assignment.time_period.start_time.strftime('%H:%M'),
                        'end_time': assignment.time_period.end_time.strftime('%H:%M')
                    },
                    'day_of_week': assignment.day_of_week.value,
                    'is_active': assignment.is_active,
                    'created_at': assignment.created_at.isoformat()
                }
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get assignment',
            'message': str(e)
        }), 500


@scheduling_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@jwt_required
@tenant_required('tenant_id')
@permissions_required('manage_schedules')
@audit_action('delete_schedule_assignment', 'schedule')
def delete_assignment(tenant_id, assignment_id):
    """
    Delete schedule assignment

    Response:
        {
            "status": "success",
            "message": "Assignment deleted successfully"
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import ScheduleAssignment

            assignment = session.query(ScheduleAssignment).filter_by(
                id=assignment_id,
                academic_year=schedule_manager.academic_year
            ).first()

            if not assignment:
                return jsonify({
                    'error': 'Assignment not found',
                    'message': f'Assignment {assignment_id} does not exist'
                }), 404

            # Soft delete by marking as inactive
            assignment.is_active = False
            assignment.updated_at = datetime.now(timezone.utc)

            session.commit()

            # Update teacher workload
            schedule_manager._update_teacher_workload(session, assignment.teacher_id)

            return jsonify({
                'status': 'success',
                'message': 'Assignment deleted successfully'
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to delete assignment',
            'message': str(e)
        }), 500


@scheduling_bp.route('/sections/<int:section_id>', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_section_schedule(tenant_id, section_id):
    """
    Get complete schedule for a section

    Query parameters:
        - week_start: Start date for the week (optional)

    Response:
        {
            "section_id": 1,
            "schedule": {
                "lunes": {
                    "P1": {
                        "subject": "MATEMÁTICAS",
                        "teacher": "MARIA NIETO",
                        "classroom": "Aula 1",
                        "time": "07:00 - 07:40"
                    }
                }
            }
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)

        # Get week start from query parameters
        week_start = request.args.get('week_start')
        if week_start:
            try:
                week_start = datetime.fromisoformat(week_start)
            except ValueError:
                return jsonify({
                    'error': 'Invalid week_start format',
                    'message': 'Use ISO format: YYYY-MM-DD'
                }), 400

        result = schedule_manager.get_schedule_for_section(section_id, week_start)

        if result['status'] == 'error':
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to get section schedule',
            'message': str(e)
        }), 500


@scheduling_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_teacher_schedule(tenant_id, teacher_id):
    """
    Get complete schedule for a teacher with workload information

    Response:
        {
            "teacher": {
                "id": 1,
                "name": "MARIA NIETO",
                "specialization": "bachillerato"
            },
            "schedule": {
                "lunes": {
                    "P1": {
                        "subject": "MATEMÁTICAS",
                        "section": "1er año A",
                        "classroom": "Aula 1",
                        "time": "07:00 - 07:40"
                    }
                }
            },
            "workload": {
                "current_hours": 22,
                "max_hours": 40,
                "subjects_taught": ["MATEMÁTICAS"],
                "is_valid": true,
                "overtime_hours": 0
            }
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        result = schedule_manager.get_teacher_schedule(teacher_id)

        if result['status'] == 'error':
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to get teacher schedule',
            'message': str(e)
        }), 500


@scheduling_bp.route('/conflicts', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@permissions_required('view_reports')
def get_conflicts(tenant_id):
    """
    Get all scheduling conflicts

    Response:
        {
            "total_conflicts": 5,
            "conflicts": [
                {
                    "type": "teacher_double_booking",
                    "severity": "critical",
                    "description": "Teacher is already assigned...",
                    "assignment_id": 123
                }
            ],
            "summary": {
                "teacher_double_booking": {
                    "critical": 2,
                    "warning": 1
                }
            }
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        result = schedule_manager.detect_all_conflicts()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to get conflicts',
            'message': str(e)
        }), 500


@scheduling_bp.route('/conflicts/<int:conflict_id>/resolve', methods=['POST'])
@jwt_required
@tenant_required('tenant_id')
@permissions_required('manage_schedules')
@audit_action('resolve_schedule_conflict', 'schedule')
def resolve_conflict(tenant_id, conflict_id):
    """
    Resolve a scheduling conflict

    Request JSON:
        {
            "resolution_notes": "Moved teacher to different time slot"
        }

    Response:
        {
            "status": "success",
            "message": "Conflict resolved successfully"
        }
    """
    try:
        data = request.get_json()

        if not data or 'resolution_notes' not in data:
            return jsonify({
                'error': 'Resolution notes required',
                'message': 'resolution_notes field is required'
            }), 400

        schedule_manager = get_schedule_manager(tenant_id)
        result = schedule_manager.resolve_conflict(
            conflict_id=conflict_id,
            resolution_notes=data['resolution_notes'],
            resolved_by=g.current_user.get('email')
        )

        if result['status'] == 'error':
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to resolve conflict',
            'message': str(e)
        }), 500


@scheduling_bp.route('/classrooms/utilization', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@permissions_required('view_reports')
def get_classroom_utilization(tenant_id):
    """
    Get classroom utilization statistics

    Response:
        {
            "classrooms": [
                {
                    "classroom_id": 1,
                    "name": "Aula 1",
                    "capacity": 35,
                    "assignments_count": 25,
                    "total_possible_slots": 40,
                    "utilization_percentage": 62.5
                }
            ]
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        result = schedule_manager.get_classroom_utilization()

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to get classroom utilization',
            'message': str(e)
        }), 500


@scheduling_bp.route('/workload/summary', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@permissions_required('view_reports')
def get_workload_summary(tenant_id):
    """
    Get teacher workload summary for all teachers

    Response:
        {
            "teachers": [
                {
                    "teacher_id": 1,
                    "name": "MARIA NIETO",
                    "current_hours": 22,
                    "max_hours": 40,
                    "utilization_percentage": 55.0,
                    "is_overloaded": false,
                    "subjects_count": 1
                }
            ],
            "summary": {
                "total_teachers": 15,
                "overloaded_teachers": 2,
                "underutilized_teachers": 5,
                "average_utilization": 68.5
            }
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import Teacher, TeacherWorkload
            from sqlalchemy import func

            # Get all teachers with their workload data
            teachers_data = session.query(
                Teacher.id,
                Teacher.teacher_name,
                Teacher.max_weekly_hours,
                Teacher.current_weekly_hours,
                func.count(TeacherWorkload.id).label('has_workload')
            ).outerjoin(
                TeacherWorkload,
                Teacher.id == TeacherWorkload.teacher_id
            ).filter(
                Teacher.academic_year == schedule_manager.academic_year
            ).group_by(Teacher.id).all()

            teachers = []
            total_utilization = 0
            overloaded_count = 0
            underutilized_count = 0

            for teacher_id, name, max_hours, current_hours, has_workload in teachers_data:
                max_hours = max_hours or 40
                current_hours = current_hours or 0
                utilization_pct = (current_hours / max_hours * 100) if max_hours > 0 else 0

                is_overloaded = current_hours > max_hours
                is_underutilized = utilization_pct < 50

                if is_overloaded:
                    overloaded_count += 1
                if is_underutilized:
                    underutilized_count += 1

                # Count distinct subjects for this teacher
                from src.models.tenant import ScheduleAssignment
                subjects_count = session.query(
                    func.count(func.distinct(ScheduleAssignment.subject_id))
                ).filter(
                    ScheduleAssignment.teacher_id == teacher_id,
                    ScheduleAssignment.academic_year == schedule_manager.academic_year,
                    ScheduleAssignment.is_active == True
                ).scalar() or 0

                teachers.append({
                    'teacher_id': teacher_id,
                    'name': name,
                    'current_hours': current_hours,
                    'max_hours': max_hours,
                    'utilization_percentage': round(utilization_pct, 1),
                    'is_overloaded': is_overloaded,
                    'is_underutilized': is_underutilized,
                    'subjects_count': subjects_count
                })

                total_utilization += utilization_pct

            avg_utilization = total_utilization / len(teachers) if teachers else 0

            return jsonify({
                'teachers': teachers,
                'summary': {
                    'total_teachers': len(teachers),
                    'overloaded_teachers': overloaded_count,
                    'underutilized_teachers': underutilized_count,
                    'average_utilization': round(avg_utilization, 1)
                },
                'academic_year': schedule_manager.academic_year
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get workload summary',
            'message': str(e)
        }), 500


@scheduling_bp.route('/bulk-assign', methods=['POST'])
@jwt_required
@tenant_required('tenant_id')
@school_admin_required
@audit_action('bulk_schedule_assignment', 'schedule')
def bulk_assign(tenant_id):
    """
    Create multiple schedule assignments in bulk

    Request JSON:
        {
            "assignments": [
                {
                    "teacher_id": 1,
                    "subject_id": 2,
                    "section_id": 3,
                    "classroom_id": 4,
                    "time_period_id": 5,
                    "day_of_week": "lunes"
                }
            ],
            "validate_conflicts": true,
            "stop_on_conflict": false
        }

    Response:
        {
            "status": "success",
            "created_assignments": 5,
            "failed_assignments": 1,
            "conflicts": [...]
        }
    """
    try:
        data = request.get_json()

        if not data or 'assignments' not in data:
            return jsonify({
                'error': 'Assignments required',
                'message': 'assignments field is required'
            }), 400

        assignments = data['assignments']
        validate_conflicts = data.get('validate_conflicts', True)
        stop_on_conflict = data.get('stop_on_conflict', False)

        schedule_manager = get_schedule_manager(tenant_id)

        created_assignments = []
        failed_assignments = []
        all_conflicts = []

        for i, assignment_data in enumerate(assignments):
            try:
                # Validate day of week
                day_of_week = DayOfWeek(assignment_data['day_of_week'])

                result = schedule_manager.create_schedule_assignment(
                    teacher_id=assignment_data['teacher_id'],
                    subject_id=assignment_data['subject_id'],
                    section_id=assignment_data['section_id'],
                    classroom_id=assignment_data['classroom_id'],
                    time_period_id=assignment_data['time_period_id'],
                    day_of_week=day_of_week,
                    created_by=g.current_user.get('email'),
                    validate_conflicts=validate_conflicts
                )

                if result['status'] == 'success':
                    created_assignments.append({
                        'index': i,
                        'assignment_id': result['assignment']['id']
                    })
                    if result['conflicts']:
                        all_conflicts.extend(result['conflicts'])
                else:
                    failed_assignments.append({
                        'index': i,
                        'error': result['message'],
                        'conflicts': result.get('conflicts', [])
                    })

                    if stop_on_conflict and result.get('conflicts'):
                        break

            except Exception as e:
                failed_assignments.append({
                    'index': i,
                    'error': str(e)
                })

        return jsonify({
            'status': 'success' if created_assignments else 'error',
            'created_assignments': len(created_assignments),
            'failed_assignments': len(failed_assignments),
            'assignments_created': created_assignments,
            'assignments_failed': failed_assignments,
            'conflicts': all_conflicts
        }), 200 if created_assignments else 400

    except Exception as e:
        return jsonify({
            'error': 'Bulk assignment failed',
            'message': str(e)
        }), 500


@scheduling_bp.route('/export/section/<int:section_id>/excel', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def export_section_schedule_excel(tenant_id, section_id):
    """
    Export section schedule as Venezuelan standard Excel format

    Response:
        Excel file download
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        exporter = VenezuelanScheduleExporter(schedule_manager)

        excel_data = exporter.export_student_schedule_excel(section_id)

        # Get section name for filename
        session = schedule_manager.SessionLocal()
        try:
            from src.models.tenant import Section
            section = session.query(Section).filter_by(id=section_id).first()
            section_name = section.name if section else f"Seccion_{section_id}"
        finally:
            session.close()

        filename = f"Horario_{section_name}_{schedule_manager.academic_year}.xlsx"

        response = jsonify({'message': 'Excel export not implemented in demo'})
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response, 200

    except Exception as e:
        return jsonify({
            'error': 'Export failed',
            'message': str(e)
        }), 500


@scheduling_bp.route('/export/teachers/workload/excel', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@permissions_required('view_reports')
def export_teacher_workload_excel(tenant_id):
    """
    Export teacher workload report as Venezuelan CARGA HORARIA Excel format

    Response:
        Excel file download
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        exporter = VenezuelanScheduleExporter(schedule_manager)

        excel_data = exporter.export_teacher_workload_excel()

        filename = f"Carga_Horaria_{schedule_manager.academic_year}.xlsx"

        response = jsonify({'message': 'Workload export not implemented in demo'})
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response, 200

    except Exception as e:
        return jsonify({
            'error': 'Export failed',
            'message': str(e)
        }), 500


@scheduling_bp.route('/export/section/<int:section_id>/csv', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def export_section_schedule_csv(tenant_id, section_id):
    """
    Export section schedule as CSV

    Response:
        CSV file download
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        exporter = VenezuelanScheduleExporter(schedule_manager)

        csv_data = exporter.export_schedule_csv(section_id)

        # Get section name for filename
        session = schedule_manager.SessionLocal()
        try:
            from src.models.tenant import Section
            section = session.query(Section).filter_by(id=section_id).first()
            section_name = section.name if section else f"Seccion_{section_id}"
        finally:
            session.close()

        filename = f"Horario_{section_name}_{schedule_manager.academic_year}.csv"

        return jsonify({
            'status': 'success',
            'csv_data': csv_data,
            'filename': filename
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'CSV export failed',
            'message': str(e)
        }), 500


@scheduling_bp.route('/import/csv', methods=['POST'])
@jwt_required
@tenant_required('tenant_id')
@school_admin_required
@audit_action('import_schedule_csv', 'schedule')
def import_schedule_csv(tenant_id):
    """
    Import schedule from CSV

    Request JSON:
        {
            "csv_content": "section_id,section_name,day_of_week,..."
        }

    Response:
        {
            "status": "success",
            "imported_assignments": 25,
            "failed_assignments": 2,
            "errors": ["Row 3: Teacher not found"]
        }
    """
    try:
        data = request.get_json()

        if not data or 'csv_content' not in data:
            return jsonify({
                'error': 'CSV content required',
                'message': 'csv_content field is required'
            }), 400

        schedule_manager = get_schedule_manager(tenant_id)
        importer = VenezuelanScheduleImporter(schedule_manager)

        result = importer.import_from_csv(
            csv_content=data['csv_content'],
            created_by=g.current_user.get('email')
        )

        if result['status'] == 'error':
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Import failed',
            'message': str(e)
        }), 500


@scheduling_bp.route('/template/excel', methods=['GET'])
@jwt_required
@teacher_or_admin_required
def get_schedule_template():
    """
    Get empty Venezuelan schedule template for manual data entry

    Response:
        Excel template file
    """
    try:
        excel_data = create_schedule_template_excel()

        filename = "Plantilla_Horario_BiScheduler.xlsx"

        return jsonify({
            'status': 'success',
            'message': 'Template generated',
            'filename': filename
        }), 200

    except Exception as e:
        return jsonify({
            'error': 'Template generation failed',
            'message': str(e)
        }), 500


@scheduling_bp.route('/sections/<int:section_id>/conflicts', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_section_conflicts(tenant_id, section_id):
    """
    Get conflicts specific to a section

    Response:
        {
            "section_id": 1,
            "conflicts": [
                {
                    "type": "classroom_conflict",
                    "severity": "critical",
                    "description": "...",
                    "assignment_id": 123
                }
            ]
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import ScheduleAssignment

            # Get all assignments for section
            assignments = session.query(ScheduleAssignment).filter_by(
                section_id=section_id,
                academic_year=schedule_manager.academic_year,
                is_active=True
            ).all()

            section_conflicts = []
            for assignment in assignments:
                conflicts = schedule_manager._detect_assignment_conflicts(session, assignment)
                for conflict in conflicts:
                    conflict['assignment_id'] = assignment.id
                    section_conflicts.append(conflict)

            return jsonify({
                'section_id': section_id,
                'conflicts': section_conflicts,
                'total_conflicts': len(section_conflicts)
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get section conflicts',
            'message': str(e)
        }), 500


@scheduling_bp.route('/teachers/<int:teacher_id>/conflicts', methods=['GET'])
@jwt_required
@tenant_required('tenant_id')
@teacher_or_admin_required
def get_teacher_conflicts(tenant_id, teacher_id):
    """
    Get conflicts specific to a teacher

    Response:
        {
            "teacher_id": 1,
            "conflicts": [...],
            "workload_status": {
                "current_hours": 25,
                "max_hours": 40,
                "is_overloaded": false
            }
        }
    """
    try:
        schedule_manager = get_schedule_manager(tenant_id)
        session = schedule_manager.SessionLocal()

        try:
            from src.models.tenant import ScheduleAssignment, Teacher

            # Get teacher info
            teacher = session.query(Teacher).filter_by(id=teacher_id).first()
            if not teacher:
                return jsonify({
                    'error': 'Teacher not found',
                    'message': f'Teacher {teacher_id} does not exist'
                }), 404

            # Get all assignments for teacher
            assignments = session.query(ScheduleAssignment).filter_by(
                teacher_id=teacher_id,
                academic_year=schedule_manager.academic_year,
                is_active=True
            ).all()

            teacher_conflicts = []
            for assignment in assignments:
                conflicts = schedule_manager._detect_assignment_conflicts(session, assignment)
                for conflict in conflicts:
                    conflict['assignment_id'] = assignment.id
                    teacher_conflicts.append(conflict)

            return jsonify({
                'teacher_id': teacher_id,
                'teacher_name': teacher.teacher_name,
                'conflicts': teacher_conflicts,
                'total_conflicts': len(teacher_conflicts),
                'workload_status': {
                    'current_hours': teacher.current_weekly_hours or 0,
                    'max_hours': teacher.max_weekly_hours or 40,
                    'is_overloaded': (teacher.current_weekly_hours or 0) > (teacher.max_weekly_hours or 40)
                }
            }), 200

        finally:
            session.close()

    except Exception as e:
        return jsonify({
            'error': 'Failed to get teacher conflicts',
            'message': str(e)
        }), 500


@scheduling_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad request',
        'message': 'Invalid request data'
    }), 400


@scheduling_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'Resource not found'
    }), 404


@scheduling_bp.errorhandler(403)
def forbidden(error):
    """Handle forbidden errors"""
    return jsonify({
        'error': 'Forbidden',
        'message': 'Insufficient privileges'
    }), 403


@scheduling_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500