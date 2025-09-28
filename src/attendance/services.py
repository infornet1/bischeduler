"""
Venezuelan Absence Monitoring Services
Phase 11: Core attendance functionality and government compliance
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from calendar import monthrange

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from src.models.tenant import (
    Student, DailyAttendance, MonthlyAttendanceSummary,
    AttendanceAlert, Section, Teacher
)


class AttendanceService:
    """
    Core attendance tracking and management service
    Phase 11.1: Daily attendance functionality
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def mark_attendance(self, student_id: int, attendance_date: date,
                       present: bool, teacher_id: int, **kwargs) -> DailyAttendance:
        """
        Mark attendance for a student on a specific date

        Args:
            student_id: Student ID
            attendance_date: Date of attendance
            present: Whether student was present
            teacher_id: Teacher marking attendance
            **kwargs: Additional attendance details (excused, late_arrival, etc.)

        Returns:
            DailyAttendance record
        """
        # Check if attendance already exists for this date
        existing = self.db.query(DailyAttendance).filter(
            and_(
                DailyAttendance.student_id == student_id,
                func.date(DailyAttendance.date) == attendance_date
            )
        ).first()

        if existing:
            # Update existing record
            existing.present = present
            existing.excused = kwargs.get('excused', False)
            existing.late_arrival = kwargs.get('late_arrival', False)
            existing.early_departure = kwargs.get('early_departure', False)
            existing.absence_reason = kwargs.get('absence_reason')
            existing.notes = kwargs.get('notes')
            existing.recorded_by = teacher_id
            existing.recorded_at = datetime.now()

            self.db.commit()
            return existing
        else:
            # Create new record
            student = self.db.query(Student).get(student_id)
            attendance = DailyAttendance(
                student_id=student_id,
                date=datetime.combine(attendance_date, datetime.min.time()),
                present=present,
                excused=kwargs.get('excused', False),
                late_arrival=kwargs.get('late_arrival', False),
                early_departure=kwargs.get('early_departure', False),
                absence_reason=kwargs.get('absence_reason'),
                notes=kwargs.get('notes'),
                recorded_by=teacher_id,
                academic_year=student.academic_year
            )

            self.db.add(attendance)
            self.db.commit()
            return attendance

    def mark_section_attendance(self, section_id: int, attendance_date: date,
                               attendance_data: Dict[int, Dict], teacher_id: int) -> List[DailyAttendance]:
        """
        Mark attendance for all students in a section

        Args:
            section_id: Section ID
            attendance_date: Date of attendance
            attendance_data: Dict mapping student_id to attendance details
            teacher_id: Teacher marking attendance

        Returns:
            List of DailyAttendance records
        """
        results = []

        # Get all students in section
        students = self.db.query(Student).filter_by(
            section_id=section_id, is_active=True
        ).all()

        for student in students:
            student_attendance = attendance_data.get(student.id, {'present': False})

            attendance = self.mark_attendance(
                student_id=student.id,
                attendance_date=attendance_date,
                teacher_id=teacher_id,
                **student_attendance
            )
            results.append(attendance)

        return results

    def get_student_attendance(self, student_id: int, start_date: date,
                              end_date: date) -> List[DailyAttendance]:
        """Get attendance records for a student in date range"""
        return self.db.query(DailyAttendance).filter(
            and_(
                DailyAttendance.student_id == student_id,
                func.date(DailyAttendance.date) >= start_date,
                func.date(DailyAttendance.date) <= end_date
            )
        ).order_by(DailyAttendance.date).all()

    def get_section_attendance(self, section_id: int, attendance_date: date) -> Dict:
        """Get attendance for all students in a section on specific date"""
        students = self.db.query(Student).filter_by(
            section_id=section_id, is_active=True
        ).all()

        result = {}
        for student in students:
            attendance = self.db.query(DailyAttendance).filter(
                and_(
                    DailyAttendance.student_id == student.id,
                    func.date(DailyAttendance.date) == attendance_date
                )
            ).first()

            result[student.id] = {
                'student': student,
                'attendance': attendance
            }

        return result

    def calculate_attendance_percentage(self, student_id: int, start_date: date,
                                      end_date: date) -> Tuple[float, int, int]:
        """
        Calculate attendance percentage for a student in date range

        Returns:
            Tuple of (percentage, present_days, total_days)
        """
        records = self.get_student_attendance(student_id, start_date, end_date)

        if not records:
            return 0.0, 0, 0

        total_days = len(records)
        present_days = sum(1 for r in records if r.present)

        percentage = (present_days / total_days) * 100 if total_days > 0 else 0.0

        return percentage, present_days, total_days

    def check_chronic_absenteeism(self, student_id: int, days_back: int = 30) -> Optional[AttendanceAlert]:
        """
        Check for chronic absenteeism patterns and create alerts

        Args:
            student_id: Student to check
            days_back: Number of days to look back

        Returns:
            AttendanceAlert if pattern detected, None otherwise
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

        percentage, present_days, total_days = self.calculate_attendance_percentage(
            student_id, start_date, end_date
        )

        # Venezuelan standard: <80% attendance is concerning, <70% is critical
        if total_days >= 10:  # Only check if sufficient data
            if percentage < 70:
                severity = 'critical'
                alert_type = 'chronic_absence_critical'
            elif percentage < 80:
                severity = 'high'
                alert_type = 'chronic_absence_warning'
            else:
                return None

            # Check if alert already exists and is active
            existing_alert = self.db.query(AttendanceAlert).filter(
                and_(
                    AttendanceAlert.student_id == student_id,
                    AttendanceAlert.alert_type.like('chronic_absence%'),
                    AttendanceAlert.is_active == True
                )
            ).first()

            if existing_alert:
                # Update existing alert
                existing_alert.absence_percentage = Decimal(str(round(percentage, 2)))
                existing_alert.severity = severity
                existing_alert.period_days = total_days
                existing_alert.absence_count = total_days - present_days
                self.db.commit()
                return existing_alert
            else:
                # Create new alert
                alert = AttendanceAlert(
                    student_id=student_id,
                    alert_type=alert_type,
                    severity=severity,
                    message=f"Student has {percentage:.1f}% attendance rate over last {days_back} days",
                    absence_count=total_days - present_days,
                    absence_percentage=Decimal(str(round(percentage, 2))),
                    period_days=total_days
                )

                self.db.add(alert)
                self.db.commit()
                return alert

        return None


class MonthlyReportService:
    """
    Venezuelan government compliance reporting service
    Phase 11.2: Monthly statistical calculations and Matrícula export
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def calculate_monthly_summary(self, month: int, year: int,
                                 academic_year: str) -> List[MonthlyAttendanceSummary]:
        """
        Calculate monthly attendance summary by grade level
        Following Venezuelan Matrícula format requirements

        Args:
            month: Month number (1-12)
            year: Year
            academic_year: Academic year string

        Returns:
            List of MonthlyAttendanceSummary records
        """
        # Get working days in month (excluding weekends)
        working_days = self._calculate_working_days(month, year)

        # Get all grade levels with active students
        grade_levels = self.db.query(Student.grade_level).filter(
            and_(
                Student.academic_year == academic_year,
                Student.is_active == True
            )
        ).distinct().all()

        summaries = []

        for (grade_level,) in grade_levels:
            summary = self._calculate_grade_summary(
                grade_level, month, year, academic_year, working_days
            )
            if summary:
                summaries.append(summary)

        return summaries

    def _calculate_grade_summary(self, grade_level: int, month: int, year: int,
                                academic_year: str, working_days: int) -> Optional[MonthlyAttendanceSummary]:
        """Calculate summary for specific grade level"""

        # Get students by gender for this grade
        students_query = self.db.query(Student).filter(
            and_(
                Student.grade_level == grade_level,
                Student.academic_year == academic_year,
                Student.is_active == True
            )
        )

        male_students = students_query.filter(Student.gender == 'M').count()
        female_students = students_query.filter(Student.gender == 'F').count()
        total_students = male_students + female_students

        if total_students == 0:
            return None

        # Get sections count for this grade
        section_count = self.db.query(Section.id).join(Student).filter(
            and_(
                Student.grade_level == grade_level,
                Student.academic_year == academic_year,
                Student.is_active == True
            )
        ).distinct().count()

        # Calculate attendance for the month
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        # Get all attendance records for students in this grade for the month
        attendance_query = self.db.query(DailyAttendance).join(Student).filter(
            and_(
                Student.grade_level == grade_level,
                Student.academic_year == academic_year,
                func.date(DailyAttendance.date) >= start_date,
                func.date(DailyAttendance.date) <= end_date,
                DailyAttendance.present == True
            )
        )

        attendance_sum = attendance_query.count()

        # Calculate averages
        max_possible_attendance = total_students * working_days
        average_attendance = Decimal(str(attendance_sum / working_days)) if working_days > 0 else Decimal('0')
        attendance_percentage = Decimal(str((attendance_sum / max_possible_attendance) * 100)) if max_possible_attendance > 0 else Decimal('0')

        # Check if summary already exists
        existing = self.db.query(MonthlyAttendanceSummary).filter(
            and_(
                MonthlyAttendanceSummary.grade_level == grade_level,
                MonthlyAttendanceSummary.month == month,
                MonthlyAttendanceSummary.year == year,
                MonthlyAttendanceSummary.academic_year == academic_year
            )
        ).first()

        if existing:
            # Update existing summary
            existing.section_count = section_count
            existing.male_students = male_students
            existing.female_students = female_students
            existing.total_students = total_students
            existing.working_days = working_days
            existing.attendance_sum = attendance_sum
            existing.average_attendance = average_attendance
            existing.attendance_percentage = attendance_percentage
            existing.calculated_at = datetime.now()
            existing.calculated_by = 'system_auto'

            self.db.commit()
            return existing
        else:
            # Create new summary
            summary = MonthlyAttendanceSummary(
                grade_level=grade_level,
                section_count=section_count,
                male_students=male_students,
                female_students=female_students,
                total_students=total_students,
                working_days=working_days,
                attendance_sum=attendance_sum,
                average_attendance=average_attendance,
                attendance_percentage=attendance_percentage,
                month=month,
                year=year,
                academic_year=academic_year,
                calculated_by='system_auto'
            )

            self.db.add(summary)
            self.db.commit()
            return summary

    def _calculate_working_days(self, month: int, year: int) -> int:
        """Calculate working days in month (Monday-Friday)"""
        _, last_day = monthrange(year, month)
        working_days = 0

        for day in range(1, last_day + 1):
            weekday = date(year, month, day).weekday()
            if weekday < 5:  # Monday=0, Friday=4
                working_days += 1

        return working_days

    def get_monthly_summaries(self, month: int, year: int,
                             academic_year: str) -> List[MonthlyAttendanceSummary]:
        """Get all monthly summaries for a specific month/year"""
        return self.db.query(MonthlyAttendanceSummary).filter(
            and_(
                MonthlyAttendanceSummary.month == month,
                MonthlyAttendanceSummary.year == year,
                MonthlyAttendanceSummary.academic_year == academic_year
            )
        ).order_by(MonthlyAttendanceSummary.grade_level).all()

    def export_matricula_format(self, month: int, year: int,
                               academic_year: str) -> Dict:
        """
        Export data in Venezuelan Matrícula format
        Phase 11.2: Government compliance export

        Returns:
            Dict with data formatted for Excel export matching government template
        """
        summaries = self.get_monthly_summaries(month, year, academic_year)

        # Build data in exact government format
        export_data = {
            'headers': [
                'GRADO',  # J
                'CANTIDAD DE SECCIONES',  # K
                'V',  # L - Varones (Male)
                'H',  # M - Hembras (Female)
                'TOTAL',  # N
                'DÍAS HABILES',  # O
                'SUMATORIA DE LA ASISTENCIA',  # P
                'PROMEDIO DE ASISTENCIA',  # Q
                'PORCENTAJE DE ASISTENCIA'  # R
            ],
            'data': [],
            'metadata': {
                'month': month,
                'year': year,
                'academic_year': academic_year,
                'generated_at': datetime.now(),
                'total_students': sum(s.total_students for s in summaries),
                'average_attendance': sum(s.attendance_percentage for s in summaries) / len(summaries) if summaries else 0
            }
        }

        for summary in summaries:
            row = [
                f"{summary.grade_level}° año",  # GRADO
                summary.section_count,  # CANTIDAD DE SECCIONES
                summary.male_students,  # V - Varones
                summary.female_students,  # H - Hembras
                summary.total_students,  # TOTAL
                summary.working_days,  # DÍAS HABILES
                summary.attendance_sum,  # SUMATORIA DE LA ASISTENCIA
                float(summary.average_attendance),  # PROMEDIO DE ASISTENCIA
                float(summary.attendance_percentage)  # PORCENTAJE DE ASISTENCIA
            ]
            export_data['data'].append(row)

        return export_data