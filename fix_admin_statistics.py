#!/usr/bin/env python3
"""
Fix the broken api_admin_statistics function
"""

# Read the file
with open('src/attendance/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the broken function
broken_function = """@attendance_bp.route('/api/admin/statistics')
def api_admin_statistics():
    \"\"\"
    Get overall attendance statistics for administrator dashboard
    Phase 11.1: Administrative statistics API
    \"\"\"
    # Ensure tenant context
    if not ensure_tenant_context():
        # Get current month stats
        current_date = date.today()
        start_date = current_date.replace(day=1)

        # Total active students
        total_students = db.session.query(Student).filter_by(
            is_active=True
        ).count()

        # Total attendance records this month
        attendance_count = db.session.query(DailyAttendance).filter(
            DailyAttendance.attendance_date >= start_date
        ).count()

        # Present count this month
        present_count = db.session.query(DailyAttendance).filter(
            and_(
                DailyAttendance.attendance_date >= start_date,
                DailyAttendance.present == True
            'overall_attendance': overall_attendance,
            'critical_alerts': critical_alerts,
            'monthly_reports': monthly_reports
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500"""

fixed_function = """@attendance_bp.route('/api/admin/statistics')
def api_admin_statistics():
    \"\"\"
    Get overall attendance statistics for administrator dashboard
    Phase 11.1: Administrative statistics API
    \"\"\"
    # Ensure tenant context
    if not ensure_tenant_context():
        return jsonify({
            'error': 'Tenant not found',
            'message': 'UEIPAB tenant not configured in database'
        }), 400
    
    try:
        # Get current month stats
        current_date = date.today()
        start_date = current_date.replace(day=1)

        # Total active students
        total_students = db.session.query(Student).filter_by(
            is_active=True
        ).count()

        # Total attendance records this month
        attendance_count = db.session.query(DailyAttendance).filter(
            DailyAttendance.attendance_date >= start_date
        ).count()

        # Present count this month
        present_count = db.session.query(DailyAttendance).filter(
            and_(
                DailyAttendance.attendance_date >= start_date,
                DailyAttendance.present == True
            )
        ).count()

        # Calculate overall attendance percentage
        overall_attendance = (present_count / attendance_count * 100) if attendance_count > 0 else 0

        # Count critical alerts (simplified for now)
        critical_alerts = 0

        # Monthly reports count
        monthly_reports = db.session.query(MonthlyAttendanceSummary).filter_by(
            academic_year='2025-2026'
        ).count()

        return jsonify({
            'total_students': total_students,
            'overall_attendance': round(overall_attendance, 1),
            'critical_alerts': critical_alerts,
            'monthly_reports': monthly_reports
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500"""

content = content.replace(broken_function, fixed_function)

# Write back
with open('src/attendance/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed api_admin_statistics function!")
