"""
Venezuelan Absence Monitoring Views
Phase 11: Teacher and administrator interfaces for attendance tracking
"""

from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from sqlalchemy import and_, func, desc

from src.core.app import db
from src.models.tenant import Student, DailyAttendance, MonthlyAttendanceSummary, Section, Teacher
from src.attendance.services import AttendanceService, MonthlyReportService
from src.tenants.middleware import require_tenant, get_current_tenant


# Create blueprint
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
def index():
    """Main attendance dashboard"""
    from flask import g, request
    from src.tenants.manager import TenantManager

    # Manual tenant resolution for attendance system
    if not hasattr(g, 'current_tenant') or not g.current_tenant:
        tenant_manager = TenantManager('mysql+pymysql://root:Temporal2024!@localhost/bischeduler_master')
        tenant = tenant_manager.get_tenant_by_domain(request.host)

        if tenant:
            g.current_tenant = tenant
        else:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'This endpoint requires tenant identification',
                'debug': f'Host: {request.host}'
            }), 400

    return render_template('attendance/dashboard.html')


@attendance_bp.route('/force')
def force_tenant():
    """Force set tenant and test dashboard"""
    from flask import g
    from src.tenants.manager import TenantManager

    # Manually set tenant context
    tenant_manager = TenantManager('mysql+pymysql://root:Temporal2024!@localhost/bischeduler_master')
    tenant = tenant_manager.get_tenant_by_domain('dev.ueipab.edu.ve')

    if tenant:
        g.current_tenant = tenant
        return render_template('attendance/dashboard.html')
    else:
        return jsonify({'error': 'Could not resolve tenant'});


@attendance_bp.route('/mark/<int:section_id>')
@require_tenant
def mark_attendance_form(section_id):
    """
    Display attendance marking form for a section
    Phase 11.1: Teacher daily attendance interface
    """
    # Get section with students
    section = db.session.query(Section).get(section_id)
    if not section:
        flash('Sección no encontrada', 'error')
        return redirect(url_for('attendance.index'))

    # Get students in section
    students = db.session.query(Student).filter_by(
        section_id=section_id, is_active=True
    ).order_by(Student.last_name, Student.first_name).all()

    # Get today's date or requested date
    attendance_date = request.args.get('date')
    if attendance_date:
        try:
            attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            attendance_date = date.today()
    else:
        attendance_date = date.today()

    # Get existing attendance for this date
    attendance_service = AttendanceService(db.session)
    existing_attendance = attendance_service.get_section_attendance(section_id, attendance_date)

    return render_template('attendance/mark_attendance.html',
                         section=section,
                         students=students,
                         attendance_date=attendance_date,
                         existing_attendance=existing_attendance)


@attendance_bp.route('/mark/<int:section_id>', methods=['POST'])
@require_tenant
def submit_attendance(section_id):
    """
    Submit attendance for a section
    Phase 11.1: Process teacher attendance marking
    """
    try:
        # Get form data
        attendance_date = datetime.strptime(request.form['attendance_date'], '%Y-%m-%d').date()
        teacher_id = 1  # TODO: Get from session/auth

        # Process attendance data
        attendance_data = {}
        for key, value in request.form.items():
            if key.startswith('student_'):
                student_id = int(key.split('_')[1])
                field = key.split('_')[2] if len(key.split('_')) > 2 else 'present'

                if student_id not in attendance_data:
                    attendance_data[student_id] = {}

                if field == 'present':
                    attendance_data[student_id]['present'] = value == 'on'
                elif field == 'excused':
                    attendance_data[student_id]['excused'] = value == 'on'
                elif field == 'late':
                    attendance_data[student_id]['late_arrival'] = value == 'on'
                elif field == 'reason':
                    attendance_data[student_id]['absence_reason'] = value
                elif field == 'notes':
                    attendance_data[student_id]['notes'] = value

        # Mark attendance
        attendance_service = AttendanceService(db.session)
        results = attendance_service.mark_section_attendance(
            section_id, attendance_date, attendance_data, teacher_id
        )

        flash(f'Asistencia registrada para {len(results)} estudiantes', 'success')
        return redirect(url_for('attendance.mark_attendance_form', section_id=section_id))

    except Exception as e:
        flash(f'Error al registrar asistencia: {str(e)}', 'error')
        return redirect(url_for('attendance.mark_attendance_form', section_id=section_id))


@attendance_bp.route('/student/<int:student_id>')
@require_tenant
def student_attendance(student_id):
    """
    View individual student attendance history
    Phase 11.1: Student attendance details
    """
    student = db.session.query(Student).get(student_id)
    if not student:
        flash('Estudiante no encontrado', 'error')
        return redirect(url_for('attendance.index'))

    # Get date range (default to current month)
    end_date = date.today()
    start_date = end_date.replace(day=1)

    # Get attendance records
    attendance_service = AttendanceService(db.session)
    records = attendance_service.get_student_attendance(student_id, start_date, end_date)

    # Calculate statistics
    percentage, present_days, total_days = attendance_service.calculate_attendance_percentage(
        student_id, start_date, end_date
    )

    return render_template('attendance/student_detail.html',
                         student=student,
                         records=records,
                         start_date=start_date,
                         end_date=end_date,
                         attendance_percentage=percentage,
                         present_days=present_days,
                         total_days=total_days)


@attendance_bp.route('/reports')
@require_tenant
def reports_dashboard():
    """
    Attendance reports dashboard
    Phase 11.1: Basic reporting interface
    """
    # Get current month data
    current_date = date.today()
    month = current_date.month
    year = current_date.year

    # Get monthly summaries
    report_service = MonthlyReportService(db.session)
    summaries = report_service.get_monthly_summaries(month, year, '2025-2026')

    return render_template('attendance/reports.html',
                         summaries=summaries,
                         month=month,
                         year=year)


@attendance_bp.route('/api/sections')
def api_sections():
    """
    API endpoint to get sections for attendance marking
    Phase 11.1: AJAX support for attendance interface
    """
    from flask import g, request
    from src.tenants.manager import TenantManager

    # Manual tenant resolution for API
    if not hasattr(g, 'current_tenant') or not g.current_tenant:
        tenant_manager = TenantManager('mysql+pymysql://root:Temporal2024!@localhost/bischeduler_master')
        tenant = tenant_manager.get_tenant_by_domain(request.host)

        if tenant:
            g.current_tenant = tenant
        else:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'This endpoint requires tenant identification',
                'debug': f'Host: {request.host}'
            }), 400

    try:
        # For now, return mock data since we don't have real sections yet
        mock_sections = [
            {
                'id': 1,
                'name': '1er Grado A',
                'grade_level': 1,
                'student_count': 25
            },
            {
                'id': 2,
                'name': '1er Grado B',
                'grade_level': 1,
                'student_count': 23
            },
            {
                'id': 3,
                'name': '2do Grado A',
                'grade_level': 2,
                'student_count': 27
            },
            {
                'id': 4,
                'name': '3er Grado A',
                'grade_level': 3,
                'student_count': 24
            },
            {
                'id': 5,
                'name': '4to Grado A',
                'grade_level': 4,
                'student_count': 26
            },
            {
                'id': 6,
                'name': '5to Grado A',
                'grade_level': 5,
                'student_count': 22
            },
            {
                'id': 7,
                'name': '6to Grado A',
                'grade_level': 6,
                'student_count': 28
            }
        ]

        return jsonify(mock_sections)

    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@attendance_bp.route('/api/attendance/summary/<int:section_id>')
def api_attendance_summary(section_id):
    """
    Get attendance summary for a section
    Phase 11.1: Real-time attendance statistics
    """
    from flask import g, request
    from src.tenants.manager import TenantManager

    # Manual tenant resolution for API
    if not hasattr(g, 'current_tenant') or not g.current_tenant:
        tenant_manager = TenantManager('mysql+pymysql://root:Temporal2024!@localhost/bischeduler_master')
        tenant = tenant_manager.get_tenant_by_domain(request.host)

        if tenant:
            g.current_tenant = tenant
        else:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'This endpoint requires tenant identification',
                'debug': f'Host: {request.host}'
            }), 400

    try:
        # Return mock data for demonstration
        mock_students = [
            {
                'student_id': 1,
                'student_name': 'María García',
                'attendance_percentage': 92.5,
                'present_days': 37,
                'total_days': 40,
                'status': 'excellent'
            },
            {
                'student_id': 2,
                'student_name': 'Carlos Rodríguez',
                'attendance_percentage': 85.0,
                'present_days': 34,
                'total_days': 40,
                'status': 'good'
            },
            {
                'student_id': 3,
                'student_name': 'Ana Pérez',
                'attendance_percentage': 75.0,
                'present_days': 30,
                'total_days': 40,
                'status': 'concerning'
            },
            {
                'student_id': 4,
                'student_name': 'José López',
                'attendance_percentage': 62.5,
                'present_days': 25,
                'total_days': 40,
                'status': 'critical'
            }
        ]

        section_average = sum(s['attendance_percentage'] for s in mock_students) / len(mock_students)

        return jsonify({
            'section_id': section_id,
            'date_range': {
                'start': (date.today() - timedelta(days=30)).isoformat(),
                'end': date.today().isoformat()
            },
            'students': mock_students,
            'section_average': round(section_average, 1)
        })

    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500


@attendance_bp.route('/api/monthly/calculate', methods=['POST'])
@require_tenant
def api_calculate_monthly():
    """
    Calculate monthly attendance summaries
    Phase 11.2: Government compliance calculations
    """
    try:
        data = request.get_json()
        month = data.get('month', date.today().month)
        year = data.get('year', date.today().year)
        academic_year = data.get('academic_year', '2025-2026')

        report_service = MonthlyReportService(db.session)
        summaries = report_service.calculate_monthly_summary(month, year, academic_year)

        return jsonify({
            'success': True,
            'message': f'Calculado {len(summaries)} resúmenes mensuales',
            'summaries': [{
                'grade_level': s.grade_level,
                'total_students': s.total_students,
                'attendance_percentage': float(s.attendance_percentage)
            } for s in summaries]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@attendance_bp.route('/admin')
@require_tenant
def admin_dashboard():
    """
    Administrator attendance dashboard
    Phase 11.1: Administrative oversight interface
    """
    return render_template('attendance/admin_dashboard.html')


@attendance_bp.route('/api/admin/statistics')
@require_tenant
def api_admin_statistics():
    """
    Get overall attendance statistics for administrator dashboard
    Phase 11.1: Administrative statistics API
    """
    try:
        # Get current month stats
        current_date = date.today()
        start_date = current_date.replace(day=1)

        # Total active students
        total_students = db.session.query(Student).filter_by(
            academic_year='2025-2026', is_active=True
        ).count()

        # Overall attendance percentage
        attendance_service = AttendanceService(db.session)

        # Calculate average attendance across all students
        students = db.session.query(Student).filter_by(
            academic_year='2025-2026', is_active=True
        ).all()

        total_percentage = 0
        student_count = 0
        critical_alerts = 0

        for student in students:
            percentage, _, _ = attendance_service.calculate_attendance_percentage(
                student.id, start_date, current_date
            )
            total_percentage += percentage
            student_count += 1

            if percentage < 70:  # Critical threshold
                critical_alerts += 1

        overall_attendance = total_percentage / student_count if student_count > 0 else 0

        # Monthly reports count
        monthly_reports = db.session.query(MonthlyAttendanceSummary).filter_by(
            academic_year='2025-2026'
        ).count()

        return jsonify({
            'total_students': total_students,
            'overall_attendance': overall_attendance,
            'critical_alerts': critical_alerts,
            'monthly_reports': monthly_reports
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@attendance_bp.route('/api/admin/grade-summary')
@require_tenant
def api_admin_grade_summary():
    """
    Get attendance summary by grade level for administrator dashboard
    Phase 11.1: Grade-level administrative statistics
    """
    try:
        current_date = date.today()
        start_date = current_date.replace(day=1)

        # Get all grade levels
        grade_levels = db.session.query(Student.grade_level).filter_by(
            academic_year='2025-2026', is_active=True
        ).distinct().all()

        attendance_service = AttendanceService(db.session)
        grade_summaries = []

        for (grade_level,) in grade_levels:
            # Get students in this grade
            students = db.session.query(Student).filter_by(
                grade_level=grade_level, academic_year='2025-2026', is_active=True
            ).all()

            # Count by gender
            male_students = sum(1 for s in students if s.gender == 'M')
            female_students = sum(1 for s in students if s.gender == 'F')

            # Calculate attendance for this grade
            total_percentage = 0
            for student in students:
                percentage, _, _ = attendance_service.calculate_attendance_percentage(
                    student.id, start_date, current_date
                )
                total_percentage += percentage

            grade_attendance = total_percentage / len(students) if students else 0

            # Get sections count for this grade
            sections_count = db.session.query(Section).filter_by(
                grade_level=grade_level, academic_year='2025-2026', is_active=True
            ).count()

            # Calculate working days (approximate)
            working_days = (current_date - start_date).days
            if working_days > 0:
                # Remove weekends approximately
                working_days = int(working_days * 5/7)

            grade_summaries.append({
                'grade_level': grade_level,
                'sections_count': sections_count,
                'male_students': male_students,
                'female_students': female_students,
                'total_students': len(students),
                'working_days': working_days,
                'average_attendance': grade_attendance,
                'attendance_percentage': grade_attendance
            })

        # Sort by grade level
        grade_summaries.sort(key=lambda x: x['grade_level'])

        return jsonify(grade_summaries)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@attendance_bp.route('/api/admin/critical-alerts')
@require_tenant
def api_admin_critical_alerts():
    """
    Get critical attendance alerts for administrator dashboard
    Phase 11.1: Critical attendance monitoring
    """
    try:
        current_date = date.today()
        start_date = current_date.replace(day=1)

        # Get all students
        students = db.session.query(Student).filter_by(
            academic_year='2025-2026', is_active=True
        ).all()

        attendance_service = AttendanceService(db.session)
        critical_alerts = []

        for student in students:
            percentage, present_days, total_days = attendance_service.calculate_attendance_percentage(
                student.id, start_date, current_date
            )

            # Critical threshold: below 70%
            if percentage < 70 and total_days > 0:
                # Get section info
                section = db.session.query(Section).get(student.section_id)

                critical_alerts.append({
                    'student_id': student.id,
                    'student_name': student.full_name,
                    'section_name': section.name if section else 'Sin sección',
                    'grade_level': student.grade_level,
                    'attendance_percentage': percentage,
                    'present_days': present_days,
                    'absent_days': total_days - present_days,
                    'total_days': total_days
                })

        # Sort by attendance percentage (worst first)
        critical_alerts.sort(key=lambda x: x['attendance_percentage'])

        # Limit to top 10 most critical
        return jsonify(critical_alerts[:10])

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@attendance_bp.route('/api/admin/chart-data')
@require_tenant
def api_admin_chart_data():
    """
    Get chart data for administrator dashboard
    Phase 11.1: Visual analytics for administrators
    """
    try:
        current_date = date.today()
        start_date = current_date.replace(day=1)

        # Grade attendance data
        grade_levels = db.session.query(Student.grade_level).filter_by(
            academic_year='2025-2026', is_active=True
        ).distinct().all()

        attendance_service = AttendanceService(db.session)
        grade_data = []

        total_male = 0
        total_female = 0

        for (grade_level,) in grade_levels:
            students = db.session.query(Student).filter_by(
                grade_level=grade_level, academic_year='2025-2026', is_active=True
            ).all()

            # Gender count
            male_count = sum(1 for s in students if s.gender == 'M')
            female_count = sum(1 for s in students if s.gender == 'F')
            total_male += male_count
            total_female += female_count

            # Attendance calculation
            total_percentage = 0
            for student in students:
                percentage, _, _ = attendance_service.calculate_attendance_percentage(
                    student.id, start_date, current_date
                )
                total_percentage += percentage

            grade_attendance = total_percentage / len(students) if students else 0

            grade_data.append({
                'grade': grade_level,
                'attendance': round(grade_attendance, 1)
            })

        grade_data.sort(key=lambda x: x['grade'])

        # Weekly trend data (mock for now - would need more complex calculation)
        weekly_trend = [
            {'week': 'Sem 1', 'attendance': 87.5},
            {'week': 'Sem 2', 'attendance': 89.2},
            {'week': 'Sem 3', 'attendance': 85.8},
            {'week': 'Sem 4', 'attendance': 88.1}
        ]

        return jsonify({
            'grade_data': grade_data,
            'gender_data': {
                'male': total_male,
                'female': total_female
            },
            'weekly_trend': weekly_trend
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@attendance_bp.route('/test')
def test_attendance():
    """Test endpoint to verify attendance system works without tenant context"""
    from flask import request
    return jsonify({
        'message': 'Venezuelan Attendance System is working!',
        'system': 'BiScheduler Phase 11 - Absence Monitoring',
        'status': 'active',
        'request_url': request.url,
        'request_path': request.path,
        'request_host': request.host,
        'features': [
            'Daily attendance tracking',
            'Monthly statistical calculations',
            'Venezuelan Matrícula format export',
            'Gender-segregated reporting',
            'Administrative dashboard',
            'Critical absence alerts'
        ]
    })


@attendance_bp.route('/demo')
def demo_dashboard():
    """Demo attendance dashboard without tenant requirement - for testing templates"""
    return render_template('attendance/dashboard.html')


@attendance_bp.route('/debug')
def debug_tenant():
    """Debug tenant resolution"""
    from flask import request, g
    debug_info = {
        'request_host': getattr(request, 'host', 'No host'),
        'request_path': getattr(request, 'path', 'No path'),
        'request_url': getattr(request, 'url', 'No URL'),
        'has_current_tenant': hasattr(g, 'current_tenant'),
        'current_tenant': str(getattr(g, 'current_tenant', 'None')),
        'request_headers': dict(request.headers),
    }
    return jsonify(debug_info)


@attendance_bp.route('/export/matricula/<int:month>/<int:year>')
@require_tenant
def export_matricula(month, year):
    """
    Export attendance data in Venezuelan Matrícula format
    Phase 11.2: Government compliance export
    """
    try:
        academic_year = '2025-2026'
        report_service = MonthlyReportService(db.session)

        # Calculate summaries if they don't exist
        summaries = report_service.calculate_monthly_summary(month, year, academic_year)

        # Export in government format
        export_data = report_service.export_matricula_format(month, year, academic_year)

        return jsonify({
            'success': True,
            'data': export_data,
            'filename': f'matricula_asistencia_{month:02d}_{year}.xlsx'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500