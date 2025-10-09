"""
Fix Academic Year References
Elimina todas las referencias a academic_year que no existe en la base de datos
"""

def fix_services():
    """Fix services.py"""
    with open('src/attendance/services.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open('src/attendance/services.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Fix calculate_monthly_summary signature
    content = content.replace(
        'def calculate_monthly_summary(self, month: int, year: int,\n                                 academic_year: str) -> List[MonthlyAttendanceSummary]:',
        'def calculate_monthly_summary(self, month: int, year: int) -> List[MonthlyAttendanceSummary]:'
    )
    
    # Fix docstring
    content = content.replace(
        '            academic_year: Academic year string\n\n',
        '\n'
    )
    
    # Fix Student query
    content = content.replace(
        '        grade_levels = self.db.query(Student.grade_level).filter(\n            and_(\n                Student.academic_year == academic_year,\n                Student.is_active == True\n            )\n        ).distinct().all()',
        '        grade_levels = self.db.query(Student.grade_level).filter(\n            Student.is_active == True\n        ).distinct().all()'
    )
    
    # Fix _calculate_grade_summary call
    content = content.replace(
        '                grade_level, month, year, academic_year, working_days',
        '                grade_level, month, year, working_days'
    )
    
    # Fix _calculate_grade_summary signature
    content = content.replace(
        'def _calculate_grade_summary(self, grade_level: int, month: int, year: int,\n                                academic_year: str, working_days: int) -> Optional[MonthlyAttendanceSummary]:',
        'def _calculate_grade_summary(self, grade_level: int, month: int, year: int,\n                                working_days: int) -> Optional[MonthlyAttendanceSummary]:'
    )
    
    # Fix students query in _calculate_grade_summary
    content = content.replace(
        '        students_query = self.db.query(Student).filter(\n            and_(\n                Student.grade_level == grade_level,\n                Student.academic_year == academic_year,\n                Student.is_active == True\n            )\n        )',
        '        students_query = self.db.query(Student).filter(\n            and_(\n                Student.grade_level == grade_level,\n                Student.is_active == True\n            )\n        )'
    )
    
    # Fix section count query
    content = content.replace(
        '        section_count = self.db.query(Section.id).join(Student).filter(\n            and_(\n                Student.grade_level == grade_level,\n                Student.academic_year == academic_year,\n                Student.is_active == True\n            )\n        ).distinct().count()',
        '        section_count = self.db.query(Section.id).join(Student).filter(\n            and_(\n                Student.grade_level == grade_level,\n                Student.is_active == True\n            )\n        ).distinct().count()'
    )
    
    # Fix attendance query
    content = content.replace(
        '        attendance_query = self.db.query(DailyAttendance).join(Student).filter(\n            and_(\n                Student.grade_level == grade_level,\n                Student.academic_year == academic_year,\n                func.date(DailyAttendance.attendance_date) >= start_date,\n                func.date(DailyAttendance.attendance_date) <= end_date,\n                DailyAttendance.present == True\n            )\n        )',
        '        attendance_query = self.db.query(DailyAttendance).join(Student).filter(\n            and_(\n                Student.grade_level == grade_level,\n                func.date(DailyAttendance.attendance_date) >= start_date,\n                func.date(DailyAttendance.attendance_date) <= end_date,\n                DailyAttendance.present == True\n            )\n        )'
    )
    
    # Fix existing summary query
    content = content.replace(
        '        existing = self.db.query(MonthlyAttendanceSummary).filter(\n            and_(\n                MonthlyAttendanceSummary.grade_level == grade_level,\n                MonthlyAttendanceSummary.month == month,\n                MonthlyAttendanceSummary.year == year,\n                MonthlyAttendanceSummary.academic_year == academic_year\n            )\n        ).first()',
        '        existing = self.db.query(MonthlyAttendanceSummary).filter(\n            and_(\n                MonthlyAttendanceSummary.grade_level == grade_level,\n                MonthlyAttendanceSummary.month == month,\n                MonthlyAttendanceSummary.year == year\n            )\n        ).first()'
    )
    
    # Fix new summary creation
    content = content.replace(
        '                month=month,\n                year=year,\n                academic_year=academic_year,\n                calculated_by=',
        '                month=month,\n                year=year,\n                calculated_by='
    )
    
    # Fix get_monthly_summaries signature
    content = content.replace(
        'def get_monthly_summaries(self, month: int, year: int,\n                             academic_year: str) -> List[MonthlyAttendanceSummary]:',
        'def get_monthly_summaries(self, month: int, year: int) -> List[MonthlyAttendanceSummary]:'
    )
    
    # Fix get_monthly_summaries query
    content = content.replace(
        '        return self.db.query(MonthlyAttendanceSummary).filter(\n            and_(\n                MonthlyAttendanceSummary.month == month,\n                MonthlyAttendanceSummary.year == year,\n                MonthlyAttendanceSummary.academic_year == academic_year\n            )\n        ).order_by(MonthlyAttendanceSummary.grade_level).all()',
        '        return self.db.query(MonthlyAttendanceSummary).filter(\n            and_(\n                MonthlyAttendanceSummary.month == month,\n                MonthlyAttendanceSummary.year == year\n            )\n        ).order_by(MonthlyAttendanceSummary.grade_level).all()'
    )
    
    # Fix export_matricula_format signature
    content = content.replace(
        'def export_matricula_format(self, month: int, year: int,\n                               academic_year: str) -> Dict:',
        'def export_matricula_format(self, month: int, year: int) -> Dict:'
    )
    
    # Fix export call
    content = content.replace(
        'summaries = self.get_monthly_summaries(month, year, academic_year)',
        'summaries = self.get_monthly_summaries(month, year)'
    )
    
    # Fix metadata
    content = content.replace(
        "                'month': month,\n                'year': year,\n                'academic_year': academic_year,\n                'generated_at':",
        "                'month': month,\n                'year': year,\n                'generated_at':"
    )
    
    with open('src/attendance/services.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ services.py fixed')

def fix_views():
    """Fix views.py"""
    with open('src/attendance/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open('src/attendance/views.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Fix reports_dashboard
    content = content.replace(
        "    summaries = report_service.get_monthly_summaries(month, year, '2025-2026')",
        "    summaries = report_service.get_monthly_summaries(month, year)"
    )
    
    # Fix api_calculate_monthly
    content = content.replace(
        "        summaries = report_service.calculate_monthly_summary(month, year, academic_year)",
        "        summaries = report_service.calculate_monthly_summary(month, year)"
    )
    
    # Fix export_matricula
    content = content.replace(
        "        summaries = report_service.calculate_monthly_summary(month, year, academic_year)",
        "        summaries = report_service.calculate_monthly_summary(month, year)"
    )
    
    content = content.replace(
        "        export_data = report_service.export_matricula_format(month, year, academic_year)",
        "        export_data = report_service.export_matricula_format(month, year)"
    )
    
    with open('src/attendance/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ views.py fixed')

if __name__ == '__main__':
    print('=' * 70)
    print('🔧 Fixing Academic Year References')
    print('=' * 70)
    print()
    
    fix_services()
    fix_views()
    
    print()
    print('=' * 70)
    print('✅ ALL FIXES COMPLETED')
    print('   Reinicia el servidor para aplicar los cambios')
    print('=' * 70)