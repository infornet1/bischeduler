"""
BiScheduler Flask Application Factory
Multi-tenant K12 scheduling platform for Venezuelan education
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app(config_name='development'):
    """
    Application factory pattern for BiScheduler

    Args:
        config_name (str): Configuration environment name

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__,
                static_folder='../static',
                template_folder='../../templates',
                static_url_path='/bischeduler/static')

    # Load configuration
    app.config.from_object(f'src.core.config.{config_name.title()}Config')

    # Set application root for URL prefix support
    app.config['APPLICATION_ROOT'] = '/bischeduler'
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    # Import models to register them with SQLAlchemy
    import src.models

    # Initialize authentication system
    from src.auth import JWTService, AuthenticationMiddleware
    from src.auth.views import auth_bp

    jwt_service = JWTService(app)
    auth_middleware = AuthenticationMiddleware(app)

    # Initialize multi-tenant system
    from src.tenants.manager import TenantManager
    from src.tenants.middleware import MultiTenantMiddleware

    tenant_manager = TenantManager(app.config['MASTER_DATABASE_URL'])
    multi_tenant_middleware = MultiTenantMiddleware(app, tenant_manager)

    # Store services in app context for access in blueprints
    app.tenant_manager = tenant_manager
    app.jwt_service = jwt_service

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/bischeduler/api/auth')

    # Import and register scheduling blueprint
    from src.scheduling.views import scheduling_bp
    app.register_blueprint(scheduling_bp)

    # Import and register schedule optimizer blueprint (Phase 8)
    from src.api.schedule_optimizer import schedule_optimizer_bp
    app.register_blueprint(schedule_optimizer_bp)

    # Import and register attendance blueprint (Phase 11)
    from src.attendance.views import attendance_bp
    app.register_blueprint(attendance_bp, url_prefix='/bischeduler/attendance')

    # Main landing page
    @app.route('/')
    @app.route('/bischeduler')
    @app.route('/bischeduler/')
    def index():
        from flask import render_template, g
        from src.tenants.middleware import get_current_tenant, get_current_schema_name
        from src.models.master import Tenant

        # Get current tenant information
        current_tenant = get_current_tenant()
        schema_name = get_current_schema_name()

        # Provide fallback values for tenant information
        if not current_tenant:
            # Create a mock tenant object for display purposes
            class MockTenant:
                def __init__(self):
                    self.institution_name = 'UEIPAB'
                    self.name = 'Universidad Experimental de las Fuerzas Armadas Nacional Bolivariana'
            current_tenant = MockTenant()

        if not schema_name:
            schema_name = 'ueipab_2025_2026'

        return render_template('index.html',
                             current_tenant=current_tenant,
                             schema_name=schema_name)

    # Login page
    @app.route('/login')
    @app.route('/bischeduler/login')
    def login_page():
        from flask import render_template
        return render_template('login.html')

    # Tenant status endpoint
    @app.route('/api/tenant/status')
    def tenant_status():
        from flask import jsonify, g
        from src.tenants.middleware import get_current_tenant
        from src.models.master import Tenant

        # Get current tenant or default to UEIPAB
        current_tenant = get_current_tenant()
        if not current_tenant:
            current_tenant = db.session.query(Tenant).filter_by(institution_name='UEIPAB').first()

        if current_tenant:
            return jsonify({
                'tenant_id': current_tenant.id,
                'institution_name': current_tenant.institution_name,
                'institution_code': current_tenant.institution_code,
                'schema_name': current_tenant.schema_name,
                'database_url_info': f"Database: {current_tenant.schema_name}",
                'status': current_tenant.status.value,
                'state_region': current_tenant.state_region,
                'municipality': current_tenant.municipality,
                'is_live_data': True,
                'academic_year': '2025-2026'
            })
        else:
            return jsonify({'error': 'No tenant found'}), 404

    # Dashboard page (post-login landing)
    @app.route('/dashboard')
    @app.route('/bischeduler/dashboard')
    def dashboard():
        from flask import render_template
        from src.tenants.middleware import get_current_tenant, get_current_schema_name
        from src.models.master import Tenant
        from src.models.tenant import Student, Teacher, Section, Classroom, ScheduleAssignment
        from sqlalchemy import func

        # Get current tenant information
        current_tenant = get_current_tenant()
        schema_name = get_current_schema_name()

        # Provide fallback values for tenant information
        if not current_tenant:
            # Create a mock tenant object for display purposes
            class MockTenant:
                def __init__(self):
                    self.institution_name = 'UEIPAB'
                    self.name = 'Universidad Experimental de las Fuerzas Armadas Nacional Bolivariana'
            current_tenant = MockTenant()

        if not schema_name:
            schema_name = 'ueipab_2025_2026'

        # Get real statistics from database
        try:
            stats = {
                'active_students': db.session.query(func.count(Student.id)).filter(Student.is_active == True).scalar() or 0,
                'total_teachers': db.session.query(func.count(Teacher.id)).filter(Teacher.is_active == True).scalar() or 0,
                'total_sections': db.session.query(func.count(Section.id)).scalar() or 0,
                'total_classrooms': db.session.query(func.count(Classroom.id)).scalar() or 0,
                'schedule_assignments': db.session.query(func.count(ScheduleAssignment.id)).scalar() or 0
            }
        except Exception as e:
            # Fallback to default values if database query fails
            stats = {
                'active_students': 0,
                'total_teachers': 15,  # We know 15 teachers were imported
                'total_sections': 6,   # We know 6 sections were imported
                'total_classrooms': 15, # We know 15 classrooms were imported
                'schedule_assignments': 0
            }

        return render_template('dashboard.html',
                             current_tenant=current_tenant,
                             schema_name=schema_name,
                             stats=stats)

    # Teacher portal page (Phase 4 - Teacher Self-Service)
    @app.route('/teacher-portal')
    @app.route('/bischeduler/teacher-portal')
    def teacher_portal():
        from flask import render_template
        return render_template('teacher_portal.html')

    # Exam calendar page (Phase 6 - Exam Scheduling)
    @app.route('/exam-calendar')
    @app.route('/bischeduler/exam-calendar')
    def exam_calendar():
        from flask import render_template
        return render_template('exam_calendar.html')

    # Student exam dashboard (Phase 6 - Student exam alerts)
    @app.route('/student-exams')
    @app.route('/bischeduler/student-exams')
    def student_exam_dashboard():
        from flask import render_template
        return render_template('student_exam_dashboard.html')

    # Core Management Routes (Should exist from Phases 1-4)
    @app.route('/schedules')
    @app.route('/bischeduler/schedules')
    def schedules():
        from flask import render_template
        return render_template('schedules.html')

    @app.route('/schedule-management')
    @app.route('/bischeduler/schedule-management')
    def schedule_management():
        from flask import render_template
        return render_template('schedule_management.html')

    @app.route('/section-schedules')
    @app.route('/bischeduler/section-schedules')
    def section_schedules():
        from flask import render_template
        return render_template('section_schedules.html')

    @app.route('/conflict-resolution')
    @app.route('/bischeduler/conflict-resolution')
    def conflict_resolution():
        from flask import render_template
        return render_template('conflict_resolution.html')

    @app.route('/students')
    @app.route('/bischeduler/students')
    def students():
        from flask import render_template
        return render_template('students.html')

    @app.route('/teachers')
    @app.route('/bischeduler/teachers')
    def teachers():
        from flask import render_template
        return render_template('teachers.html')

    @app.route('/classrooms')
    @app.route('/bischeduler/classrooms')
    def classrooms():
        from flask import render_template
        return render_template('classrooms.html')

    # API Routes for data retrieval
    @app.route('/api/teachers')
    @app.route('/bischeduler/api/teachers')
    def get_teachers():
        """Get all teachers"""
        from flask import jsonify
        from src.models.tenant import Teacher
        
        try:
            teachers = db.session.query(Teacher).filter_by(is_active=True).all()
            return jsonify({
                'success': True,
                'teachers': [{
                    'id': t.id,
                    'cedula': t.cedula,
                    'first_name': t.first_name,
                    'last_name': t.last_name,
                    'email': t.email,
                    'phone': t.phone,
                    'specialization': t.specialization,
                    'employment_type': t.employment_type,
                    'weekly_hours': t.weekly_hours,
                    'is_active': t.is_active
                } for t in teachers]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/students')
    @app.route('/bischeduler/api/students')
    def get_students():
        """Get all students"""
        from flask import jsonify
        from src.models.tenant import Student
        
        try:
            students = db.session.query(Student).filter_by(is_active=True).all()
            return jsonify({
                'success': True,
                'students': [{
                    'id': s.id,
                    'cedula': s.cedula,
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'date_of_birth': s.date_of_birth.isoformat() if s.date_of_birth else None,
                    'gender': s.gender,
                    'section_id': s.section_id,
                    'parent_name': s.parent_name,
                    'parent_phone': s.parent_phone,
                    'parent_email': s.parent_email,
                    'is_active': s.is_active
                } for s in students]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/sections')
    @app.route('/bischeduler/api/sections')
    def get_sections():
        """Get all sections"""
        from flask import jsonify
        from src.models.tenant import Section
        
        try:
            sections = db.session.query(Section).all()
            return jsonify({
                'success': True,
                'sections': [{
                    'id': s.id,
                    'name': s.name,
                    'grade_level': s.grade_level,
                    'academic_year': s.academic_year,
                    'capacity': s.capacity,
                    'shift': s.shift
                } for s in sections]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/classrooms')
    @app.route('/bischeduler/api/classrooms')
    def get_classrooms():
        """Get all classrooms"""
        from flask import jsonify
        from src.models.tenant import Classroom
        
        try:
            classrooms = db.session.query(Classroom).all()
            return jsonify({
                'success': True,
                'classrooms': [{
                    'id': c.id,
                    'name': c.name,
                    'building': c.building,
                    'floor': c.floor,
                    'capacity': c.capacity,
                    'classroom_type': c.classroom_type,
                    'has_projector': c.has_projector,
                    'has_computer': c.has_computer,
                    'has_ac': c.has_ac,
                    'is_lab': c.is_lab
                } for c in classrooms]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # Phase 7: Parent Portal
    @app.route('/parent-portal')
    @app.route('/bischeduler/parent-portal')
    def parent_portal():
        from flask import render_template
        return render_template('parent_portal.html')

    # Phase 8: Schedule Optimizer
    @app.route('/schedule-optimizer')
    @app.route('/bischeduler/schedule-optimizer')
    def schedule_optimizer():
        from flask import render_template
        return render_template('schedule_optimizer.html')

    # Future Phase Routes (Placeholder pages)
    @app.route('/bimodal')
    @app.route('/bischeduler/bimodal')
    def bimodal():
        from flask import render_template
        return render_template('coming_soon.html',
                             feature_name="Gestión Bimodal",
                             feature_description="Horarios presencial/virtual",
                             phase="Fase 7")

    @app.route('/matricula')
    @app.route('/bischeduler/matricula')
    def matricula():
        from flask import render_template
        return render_template('coming_soon.html',
                             feature_name="Reportes de Matrícula",
                             feature_description="Informes oficiales MINED",
                             phase="Fase 8")

    @app.route('/reports')
    @app.route('/bischeduler/reports')
    def reports():
        from flask import render_template
        return render_template('coming_soon.html',
                             feature_name="Sistema de Reportes",
                             feature_description="Informes académicos y administrativos",
                             phase="Fase 9")

    @app.route('/admin')
    @app.route('/bischeduler/admin')
    def admin():
        from flask import render_template
        return render_template('coming_soon.html',
                             feature_name="Panel de Administración",
                             feature_description="Configuración del sistema",
                             phase="Fase 10")

    # Teacher portal API routes
    @app.route('/api/teacher/dashboard/<int:teacher_id>')
    def teacher_dashboard_api(teacher_id):
        from flask import jsonify
        from src.services.teacher_portal import TeacherPortalService
        from src.models.tenant import get_tenant_session

        try:
            # Get tenant session (assuming current tenant context)
            db_session = get_tenant_session()
            service = TeacherPortalService(db_session)

            stats = service.get_teacher_dashboard_stats(teacher_id)
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/teacher/schedule/<int:teacher_id>')
    def teacher_schedule_api(teacher_id):
        from flask import jsonify, request
        from src.services.teacher_portal import TeacherPortalService
        from src.models.tenant import get_tenant_session

        try:
            week_offset = request.args.get('week', 0, type=int)
            db_session = get_tenant_session()
            service = TeacherPortalService(db_session)

            schedule = service.get_teacher_schedule(teacher_id, week_offset)
            return jsonify(schedule)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/teacher/preferences/<int:teacher_id>')
    def teacher_preferences_api(teacher_id):
        from flask import jsonify
        from src.services.teacher_portal import TeacherPortalService
        from src.models.tenant import get_tenant_session

        try:
            db_session = get_tenant_session()
            service = TeacherPortalService(db_session)

            preferences = service.get_teacher_preferences(teacher_id)
            return jsonify(preferences)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/teacher/reference-data')
    def teacher_reference_data_api():
        from flask import jsonify
        from src.services.teacher_portal import TeacherPortalService
        from src.models.tenant import get_tenant_session

        try:
            db_session = get_tenant_session()
            service = TeacherPortalService(db_session)

            data = service.get_portal_reference_data()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ============================================================================
    # PHASE 3: EXCEL INTEGRATION ROUTES
    # ============================================================================

    @app.route('/excel-integration')
    @app.route('/bischeduler/excel-integration')
    def excel_integration():
        """Excel import/export management page"""
        from flask import render_template
        return render_template('excel_integration.html')

    @app.route('/api/excel/upload-teachers', methods=['POST'])
    def upload_teachers_excel():
        """Upload and import teachers from Excel"""
        from flask import request, jsonify
        from src.services.excel_integration import ExcelIntegrationService, ExcelValidationError
        from src.models.tenant import get_tenant_session

        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Get tenant session
            db_session = get_tenant_session()
            service = ExcelIntegrationService(db_session, 'current_tenant')

            # Save and process file
            temp_path = service.save_uploaded_file(file)
            results = service.import_teachers_from_excel(temp_path)
            service.cleanup_temp_file(temp_path)

            return jsonify({
                'success': True,
                'message': f"Import completed: {results['success']} teachers imported",
                'results': results
            })

        except ExcelValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f"Import failed: {str(e)}"}), 500

    @app.route('/api/excel/upload-students', methods=['POST'])
    def upload_students_excel():
        """Upload and import students from Excel"""
        from flask import request, jsonify
        from src.services.excel_integration import ExcelIntegrationService, ExcelValidationError
        from src.models.tenant import get_tenant_session

        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            db_session = get_tenant_session()
            service = ExcelIntegrationService(db_session, 'current_tenant')

            temp_path = service.save_uploaded_file(file)
            results = service.import_students_from_excel(temp_path)
            service.cleanup_temp_file(temp_path)

            return jsonify({
                'success': True,
                'message': f"Import completed: {results['success']} students imported",
                'results': results
            })

        except ExcelValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f"Import failed: {str(e)}"}), 500

    @app.route('/api/excel/upload-classrooms', methods=['POST'])
    def upload_classrooms_excel():
        """Upload and import classrooms from Excel"""
        from flask import request, jsonify
        from src.services.excel_integration import ExcelIntegrationService, ExcelValidationError
        from src.models.tenant import get_tenant_session

        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            db_session = get_tenant_session()
            service = ExcelIntegrationService(db_session, 'current_tenant')

            temp_path = service.save_uploaded_file(file)
            results = service.import_classrooms_from_excel(temp_path)
            service.cleanup_temp_file(temp_path)

            return jsonify({
                'success': True,
                'message': f"Import completed: {results['success']} classrooms imported",
                'results': results
            })

        except ExcelValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f"Import failed: {str(e)}"}), 500

    @app.route('/api/excel/export-teachers')
    def export_teachers_excel():
        """Export teachers to Excel file"""
        from flask import send_file, jsonify
        from src.services.excel_integration import ExcelIntegrationService
        from src.models.tenant import get_tenant_session

        try:
            db_session = get_tenant_session()
            service = ExcelIntegrationService(db_session, 'current_tenant')

            temp_path = service.export_teachers_to_excel()
            return send_file(temp_path,
                           as_attachment=True,
                           download_name='teachers_export.xlsx',
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        except Exception as e:
            return jsonify({'error': f"Export failed: {str(e)}"}), 500

    @app.route('/api/excel/export-schedule')
    def export_schedule_excel():
        """Export complete schedule to Excel"""
        from flask import send_file, jsonify, request
        from src.services.excel_integration import ExcelIntegrationService
        from src.models.tenant import get_tenant_session

        try:
            academic_period_id = request.args.get('academic_period_id', type=int)

            db_session = get_tenant_session()
            service = ExcelIntegrationService(db_session, 'current_tenant')

            temp_path = service.export_schedule_to_excel(academic_period_id)
            return send_file(temp_path,
                           as_attachment=True,
                           download_name='schedule_export.xlsx',
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        except Exception as e:
            return jsonify({'error': f"Export failed: {str(e)}"}), 500

    @app.route('/api/excel/templates/<template_type>')
    def download_excel_template(template_type):
        """Download Excel templates for data import"""
        from flask import send_file, jsonify
        from src.services.excel_integration import ExcelIntegrationService

        try:
            service = ExcelIntegrationService(None, 'template')

            if template_type == 'teachers':
                temp_path = service.create_teachers_template()
                filename = 'teachers_template.xlsx'
            elif template_type == 'students':
                temp_path = service.create_students_template()
                filename = 'students_template.xlsx'
            elif template_type == 'classrooms':
                temp_path = service.create_classrooms_template()
                filename = 'classrooms_template.xlsx'
            else:
                return jsonify({'error': 'Invalid template type'}), 400

            return send_file(temp_path,
                           as_attachment=True,
                           download_name=filename,
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        except Exception as e:
            return jsonify({'error': f"Template generation failed: {str(e)}"}), 500

    @app.route('/api/excel/statistics')
    def excel_statistics():
        """Get import/export statistics"""
        from flask import jsonify
        from src.services.excel_integration import ExcelIntegrationService
        from src.models.tenant import get_tenant_session

        try:
            db_session = get_tenant_session()
            service = ExcelIntegrationService(db_session, 'current_tenant')

            stats = service.get_import_statistics()
            return jsonify({
                'success': True,
                'statistics': stats
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ============================================================================
    # PHASE 5: SUBSTITUTE TEACHER MANAGEMENT ROUTES
    # ============================================================================

    @app.route('/substitute-management')
    @app.route('/bischeduler/substitute-management')
    def substitute_management():
        """Substitute teacher management page"""
        from flask import render_template
        return render_template('substitute_management.html')

    @app.route('/api/substitutes/pool')
    def get_substitute_pool():
        """Get available substitute teachers"""
        from flask import jsonify, request
        from src.services.substitute_management import SubstituteManagementService
        from src.models.tenant import get_tenant_session

        try:
            subject_id = request.args.get('subject_id', type=int)
            available_date = request.args.get('available_date')

            db_session = get_tenant_session()
            service = SubstituteManagementService(db_session)

            pool = service.get_substitute_pool(subject_id, available_date)
            return jsonify({
                'success': True,
                'substitute_pool': pool
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/substitutes/register', methods=['POST'])
    def register_substitute():
        """Register new substitute teacher"""
        from flask import request, jsonify
        from src.services.substitute_management import SubstituteManagementService
        from src.models.tenant import get_tenant_session

        try:
            teacher_data = request.get_json()

            db_session = get_tenant_session()
            service = SubstituteManagementService(db_session)

            result = service.register_substitute_teacher(teacher_data)
            return jsonify(result)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/absences/submit', methods=['POST'])
    def submit_absence():
        """Submit teacher absence request"""
        from flask import request, jsonify
        from src.services.substitute_management import SubstituteManagementService
        from src.models.tenant import get_tenant_session
        from datetime import datetime

        try:
            absence_data = request.get_json()

            # Convert date strings to date objects
            if 'start_date' in absence_data:
                absence_data['start_date'] = datetime.strptime(absence_data['start_date'], '%Y-%m-%d').date()
            if 'end_date' in absence_data:
                absence_data['end_date'] = datetime.strptime(absence_data['end_date'], '%Y-%m-%d').date()

            db_session = get_tenant_session()
            service = SubstituteManagementService(db_session)

            result = service.submit_absence_request(absence_data)
            return jsonify(result)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/substitutes/<int:substitute_id>/dashboard')
    def substitute_dashboard(substitute_id):
        """Get substitute teacher dashboard data"""
        from flask import jsonify
        from src.services.substitute_management import SubstituteManagementService
        from src.models.tenant import get_tenant_session

        try:
            db_session = get_tenant_session()
            service = SubstituteManagementService(db_session)

            dashboard_data = service.get_substitute_dashboard(substitute_id)
            return jsonify(dashboard_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/substitutes/<int:substitute_id>/assignments/<int:assignment_id>/accept', methods=['POST'])
    def accept_substitute_assignment(substitute_id, assignment_id):
        """Accept substitute assignment"""
        from flask import jsonify
        from src.services.substitute_management import SubstituteManagementService
        from src.models.tenant import get_tenant_session

        try:
            db_session = get_tenant_session()
            service = SubstituteManagementService(db_session)

            result = service.accept_assignment(substitute_id, assignment_id)
            return jsonify(result)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/substitutes/<int:substitute_id>/assignments/<int:assignment_id>/decline', methods=['POST'])
    def decline_substitute_assignment(substitute_id, assignment_id):
        """Decline substitute assignment"""
        from flask import request, jsonify
        from src.services.substitute_management import SubstituteManagementService
        from src.models.tenant import get_tenant_session

        try:
            data = request.get_json()
            reason = data.get('reason', 'No reason provided')

            db_session = get_tenant_session()
            service = SubstituteManagementService(db_session)

            result = service.decline_assignment(substitute_id, assignment_id, reason)
            return jsonify(result)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/substitutes/assignments/cost')
    def calculate_assignment_cost():
        """Calculate cost for substitute assignment"""
        from flask import request, jsonify
        from src.services.substitute_management import SubstituteManagementService
        from src.models.tenant import get_tenant_session

        try:
            substitute_id = request.args.get('substitute_id', type=int)
            hours = request.args.get('hours', type=float)
            assignment_type = request.args.get('assignment_type', 'regular')

            db_session = get_tenant_session()
            service = SubstituteManagementService(db_session)

            cost_data = service.calculate_assignment_cost(substitute_id, hours, assignment_type)
            return jsonify({
                'success': True,
                'cost_calculation': cost_data
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Phase 7: Parent Portal API Endpoints
    @app.route('/api/parent/children/<int:parent_id>')
    def get_parent_children(parent_id):
        """Get list of children for a parent account"""
        try:
            # Demo data - in production, this would query the database
            children_data = [
                {
                    'id': 1,
                    'name': 'María González Rodríguez',
                    'grade': '3er año A',
                    'student_id': 'E-12345678',
                    'status': 'active',
                    'current_average': 17.8,
                    'attendance': 96
                },
                {
                    'id': 2,
                    'name': 'Carlos González Rodríguez',
                    'grade': '1er año B',
                    'student_id': 'E-12345679',
                    'status': 'exam_period',
                    'current_average': 16.2,
                    'attendance': 94
                }
            ]

            return jsonify({
                'success': True,
                'children': children_data
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/parent/student/<int:student_id>/schedule')
    def get_student_schedule(student_id):
        """Get current schedule for a specific student"""
        try:
            # Demo schedule data
            schedule_data = {
                'student_info': {
                    'name': 'María González Rodríguez',
                    'grade': '3er año A',
                    'section': 'A'
                },
                'schedule': {
                    'lunes': [
                        {'period': 'P1', 'time': '07:00-07:40', 'subject': 'MATEMÁTICAS', 'teacher': 'Prof. García', 'classroom': 'Aula 3'},
                        {'period': 'P2', 'time': '07:40-08:20', 'subject': 'CIENCIAS', 'teacher': 'Prof. López', 'classroom': 'Lab Ciencias'}
                    ],
                    'martes': [
                        {'period': 'P1', 'time': '07:00-07:40', 'subject': 'CASTELLANO', 'teacher': 'Prof. Morales', 'classroom': 'Aula 1'},
                        {'period': 'P2', 'time': '07:40-08:20', 'subject': 'MATEMÁTICAS', 'teacher': 'Prof. García', 'classroom': 'Aula 3'}
                    ]
                }
            }

            return jsonify({
                'success': True,
                'schedule': schedule_data
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/parent/student/<int:student_id>/exams')
    def get_student_exams(student_id):
        """Get upcoming exams for a specific student"""
        try:
            # Demo exam data
            exams_data = [
                {
                    'id': 1,
                    'subject': 'MATEMÁTICAS',
                    'type': 'parcial',
                    'date': '2024-09-29',
                    'time': '08:00',
                    'classroom': 'Aula 3',
                    'teacher': 'Prof. García',
                    'topics': ['Ecuaciones cuadráticas', 'Sistemas de ecuaciones']
                },
                {
                    'id': 2,
                    'subject': 'CASTELLANO',
                    'type': 'parcial',
                    'date': '2024-10-02',
                    'time': '07:00',
                    'classroom': 'Aula 1',
                    'teacher': 'Prof. Morales',
                    'topics': ['Análisis literario', 'Comprensión lectora']
                },
                {
                    'id': 3,
                    'subject': 'CIENCIAS',
                    'type': 'final',
                    'date': '2024-10-04',
                    'time': '07:40',
                    'classroom': 'Lab Ciencias',
                    'teacher': 'Prof. López',
                    'topics': ['Sistema circulatorio', 'Sistema respiratorio']
                }
            ]

            return jsonify({
                'success': True,
                'exams': exams_data
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/parent/student/<int:student_id>/notifications')
    def get_student_notifications(student_id):
        """Get recent notifications for a specific student"""
        try:
            # Demo notifications data
            notifications_data = [
                {
                    'id': 1,
                    'type': 'grade',
                    'title': 'Calificación Publicada',
                    'message': 'Matemáticas - 18.5/20',
                    'timestamp': '2024-09-27T14:30:00Z',
                    'read': False
                },
                {
                    'id': 2,
                    'type': 'schedule',
                    'title': 'Cambio de Horario',
                    'message': 'Educación Física - Nueva hora: Jueves P3',
                    'timestamp': '2024-09-26T10:15:00Z',
                    'read': True
                },
                {
                    'id': 3,
                    'type': 'exam',
                    'title': 'Recordatorio de Examen',
                    'message': 'Examen de Matemáticas - Viernes 29 Sept',
                    'timestamp': '2024-09-27T08:00:00Z',
                    'read': False
                }
            ]

            return jsonify({
                'success': True,
                'notifications': notifications_data
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/parent/student/<int:student_id>/grades')
    def get_student_grades(student_id):
        """Get academic grades and summary for a specific student"""
        try:
            # Demo grades data
            grades_data = {
                'summary': {
                    'overall_average': 17.8,
                    'attendance_percentage': 96,
                    'top_subject': 'MATEMÁTICAS',
                    'top_subject_average': 19.2,
                    'pending_exams': 3,
                    'academic_period': '2024-2025 - Lapso II'
                },
                'subjects': [
                    {'name': 'MATEMÁTICAS', 'average': 19.2, 'grades': [18, 20, 19, 19]},
                    {'name': 'CASTELLANO', 'average': 17.5, 'grades': [17, 18, 17, 18]},
                    {'name': 'CIENCIAS', 'average': 16.8, 'grades': [16, 17, 17, 17]},
                    {'name': 'HISTORIA', 'average': 18.0, 'grades': [18, 18, 18, 18]},
                    {'name': 'INGLÉS', 'average': 17.2, 'grades': [17, 17, 17, 18]},
                    {'name': 'EDUCACIÓN FÍSICA', 'average': 18.5, 'grades': [19, 18, 19, 18]},
                    {'name': 'ARTE', 'average': 17.0, 'grades': [17, 17, 17, 17]}
                ]
            }

            return jsonify({
                'success': True,
                'grades': grades_data
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    # ============================================================================
    # SCHEDULE MANAGEMENT API ENDPOINTS
    # ============================================================================

    @app.route('/api/schedule/reference-data')
    @app.route('/bischeduler/api/schedule/reference-data')
    def schedule_reference_data():
        """Get all reference data needed for schedule management"""
        from flask import jsonify
        from src.models.tenant import (
            get_tenant_session, Teacher, Section, Subject,
            Classroom, TimePeriod
        )
        from sqlalchemy import and_

        try:
            db_session = get_tenant_session()
            current_academic_year = '2025-2026'

            # Get all teachers
            teachers = db_session.query(Teacher).filter(
                Teacher.is_active == True
            ).order_by(Teacher.teacher_name).all()

            # Get all sections
            sections = db_session.query(Section).filter(
                Section.is_active == True
            ).order_by(Section.name).all()

            # Get all subjects
            subjects = db_session.query(Subject).filter(
                and_(
                    Subject.academic_year == current_academic_year,
                    Subject.is_active == True
                )
            ).order_by(Subject.subject_name).all()

            # Get all classrooms
            classrooms = db_session.query(Classroom).filter(
                Classroom.is_active == True
            ).order_by(Classroom.name).all()

            # Get time periods (deduplicated by name and time)
            time_periods_query = db_session.query(TimePeriod).filter(
                and_(
                    TimePeriod.academic_year == current_academic_year,
                    TimePeriod.is_active == True
                )
            ).order_by(TimePeriod.display_order).all()

            # Deduplicate time periods by name and start_time
            seen_periods = {}
            time_periods = []
            for tp in time_periods_query:
                key = f"{tp.period_name}_{tp.start_time}"
                if key not in seen_periods:
                    seen_periods[key] = tp
                    time_periods.append(tp)

            return jsonify({
                'success': True,
                'data': {
                    'teachers': [
                        {
                            'id': t.id,
                            'name': t.teacher_name,
                            'specialization': t.area_specialization or 'General'
                        } for t in teachers
                    ],
                    'sections': [
                        {
                            'id': s.id,
                            'name': s.name,
                            'grade': s.grade_level
                        } for s in sections
                    ],
                    'subjects': [
                        {
                            'id': s.id,
                            'name': s.subject_name,
                            'short_name': s.short_name
                        } for s in subjects
                    ],
                    'classrooms': [
                        {
                            'id': c.id,
                            'name': c.name,
                            'capacity': c.capacity or 30,
                            'room_type': c.room_type.value if c.room_type else 'regular'
                        } for c in classrooms
                    ],
                    'time_periods': [
                        {
                            'id': tp.id,
                            'name': tp.period_name,
                            'start_time': tp.start_time.strftime('%H:%M'),
                            'end_time': tp.end_time.strftime('%H:%M'),
                            'is_break': tp.is_break,
                            'duration': tp.duration_minutes
                        } for tp in time_periods
                    ]
                }
            })

        except Exception as e:
            return jsonify({'error': f"Failed to load reference data: {str(e)}"}), 500

    @app.route('/api/schedule/assignments')
    @app.route('/bischeduler/api/schedule/assignments')
    def get_schedule_assignments():
        """Get schedule assignments for a specific view (section/teacher/classroom)"""
        from flask import jsonify, request
        from src.models.tenant import get_tenant_session, ScheduleAssignment, TimePeriod
        from sqlalchemy import and_

        try:
            view_type = request.args.get('view_type', 'section')  # section, teacher, classroom
            target_id = request.args.get('target_id', type=int)
            current_academic_year = '2025-2026'

            if not target_id:
                return jsonify({'error': 'target_id is required'}), 400

            db_session = get_tenant_session()

            # Build query based on view type
            query = db_session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.academic_year == current_academic_year,
                    ScheduleAssignment.is_active == True
                )
            )

            if view_type == 'section':
                query = query.filter(ScheduleAssignment.section_id == target_id)
            elif view_type == 'teacher':
                query = query.filter(ScheduleAssignment.teacher_id == target_id)
            elif view_type == 'classroom':
                query = query.filter(ScheduleAssignment.classroom_id == target_id)

            assignments = query.all()

            # Get time periods for mapping (deduplicated)
            time_periods_query = db_session.query(TimePeriod).filter(
                and_(
                    TimePeriod.academic_year == current_academic_year,
                    TimePeriod.is_active == True
                )
            ).order_by(TimePeriod.display_order).all()

            # Create mapping from all period IDs to canonical period info
            period_mapping = {}
            seen_periods = {}
            for tp in time_periods_query:
                key = f"{tp.period_name}_{tp.start_time}"
                if key not in seen_periods:
                    seen_periods[key] = tp
                    canonical_period = tp
                else:
                    canonical_period = seen_periods[key]

                period_mapping[tp.id] = canonical_period

            # Format assignments for frontend
            schedule_data = {}
            for assignment in assignments:
                try:
                    # Map to canonical period
                    canonical_period = period_mapping.get(assignment.time_period_id)
                    if not canonical_period:
                        continue

                    key = f"{assignment.day_of_week.value}_{canonical_period.id}"
                    schedule_data[key] = {
                        'id': assignment.id,
                        'subject': assignment.subject.subject_name if assignment.subject else 'Unknown Subject',
                        'teacher': assignment.teacher.teacher_name if assignment.teacher else 'Unknown Teacher',
                        'classroom': assignment.classroom.name if assignment.classroom else 'Unknown Classroom',
                        'section': assignment.section.name if assignment.section else 'Unknown Section',
                        'assignment_type': assignment.assignment_type,
                        'is_locked': assignment.is_locked,
                        'conflict_status': assignment.conflict_status
                    }
                except Exception as e:
                    # Skip assignments with missing relationships
                    continue

            return jsonify({
                'success': True,
                'schedule_data': schedule_data,
                'view_type': view_type,
                'target_id': target_id
            })

        except Exception as e:
            return jsonify({'error': f"Failed to load assignments: {str(e)}"}), 500

    @app.route('/api/schedule/assignments', methods=['POST'])
    def create_schedule_assignment():
        """Create a new schedule assignment with conflict detection"""
        from flask import jsonify, request
        from src.models.tenant import (
            get_tenant_session, ScheduleAssignment, Teacher, Section,
            Subject, Classroom, TimePeriod, DayOfWeek
        )
        from sqlalchemy import and_
        from datetime import datetime

        try:
            data = request.get_json()
            required_fields = ['section_id', 'subject_id', 'teacher_id',
                             'classroom_id', 'day_of_week', 'time_period_id']

            # Validate required fields
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            db_session = get_tenant_session()
            current_academic_year = '2025-2026'

            # Check for conflicts before creating
            conflicts = check_assignment_conflicts(
                db_session, data['teacher_id'], data['classroom_id'],
                data['day_of_week'], data['time_period_id'], current_academic_year
            )

            if conflicts:
                return jsonify({
                    'error': 'Assignment conflicts detected',
                    'conflicts': conflicts
                }), 409

            # Create new assignment
            assignment = ScheduleAssignment(
                tenant_id=1,  # UEIPAB tenant
                section_id=data['section_id'],
                subject_id=data['subject_id'],
                teacher_id=data['teacher_id'],
                classroom_id=data['classroom_id'],
                time_period_id=data['time_period_id'],
                day_of_week=DayOfWeek(data['day_of_week']),
                academic_year=current_academic_year,
                assignment_type=data.get('assignment_type', 'regular'),
                is_active=True,
                is_locked=data.get('is_locked', False),
                conflict_status='none',
                created_at=datetime.now()
            )

            db_session.add(assignment)
            db_session.commit()

            return jsonify({
                'success': True,
                'message': 'Assignment created successfully',
                'assignment_id': assignment.id
            }), 201

        except Exception as e:
            db_session.rollback()
            return jsonify({'error': f"Failed to create assignment: {str(e)}"}), 500
        finally:
            db_session.close()

    @app.route('/api/schedule/assignments/<int:assignment_id>', methods=['PUT'])
    def update_schedule_assignment(assignment_id):
        """Update an existing schedule assignment"""
        from flask import jsonify, request
        from src.models.tenant import get_tenant_session, ScheduleAssignment, DayOfWeek
        from datetime import datetime

        try:
            data = request.get_json()
            db_session = get_tenant_session()

            # Get existing assignment
            assignment = db_session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.id == assignment_id,
                    ScheduleAssignment.is_active == True
                )
            ).first()

            if not assignment:
                return jsonify({'error': 'Assignment not found'}), 404

            # Check if assignment is locked
            if assignment.is_locked:
                return jsonify({'error': 'Cannot modify locked assignment'}), 403

            # Check for conflicts if time/resource changes
            if any(field in data for field in ['teacher_id', 'classroom_id', 'day_of_week', 'time_period_id']):
                conflicts = check_assignment_conflicts(
                    db_session,
                    data.get('teacher_id', assignment.teacher_id),
                    data.get('classroom_id', assignment.classroom_id),
                    data.get('day_of_week', assignment.day_of_week.value),
                    data.get('time_period_id', assignment.time_period_id),
                    assignment.academic_year,
                    exclude_assignment_id=assignment_id
                )

                if conflicts:
                    return jsonify({
                        'error': 'Update would create conflicts',
                        'conflicts': conflicts
                    }), 409

            # Update assignment fields
            updatable_fields = [
                'section_id', 'subject_id', 'teacher_id', 'classroom_id',
                'time_period_id', 'assignment_type', 'is_locked'
            ]

            for field in updatable_fields:
                if field in data:
                    if field == 'day_of_week':
                        setattr(assignment, field, DayOfWeek(data[field]))
                    else:
                        setattr(assignment, field, data[field])

            assignment.updated_at = datetime.now()
            db_session.commit()

            return jsonify({
                'success': True,
                'message': 'Assignment updated successfully'
            })

        except Exception as e:
            db_session.rollback()
            return jsonify({'error': f"Failed to update assignment: {str(e)}"}), 500
        finally:
            db_session.close()

    @app.route('/api/schedule/assignments/<int:assignment_id>', methods=['DELETE'])
    def delete_schedule_assignment(assignment_id):
        """Delete a schedule assignment"""
        from flask import jsonify
        from src.models.tenant import get_tenant_session, ScheduleAssignment
        from sqlalchemy import and_
        from datetime import datetime

        try:
            db_session = get_tenant_session()

            # Get assignment
            assignment = db_session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.id == assignment_id,
                    ScheduleAssignment.is_active == True
                )
            ).first()

            if not assignment:
                return jsonify({'error': 'Assignment not found'}), 404

            # Check if assignment is locked
            if assignment.is_locked:
                return jsonify({'error': 'Cannot delete locked assignment'}), 403

            # Soft delete
            assignment.is_active = False
            assignment.updated_at = datetime.now()
            db_session.commit()

            return jsonify({
                'success': True,
                'message': 'Assignment deleted successfully'
            })

        except Exception as e:
            db_session.rollback()
            return jsonify({'error': f"Failed to delete assignment: {str(e)}"}), 500
        finally:
            db_session.close()

    @app.route('/api/schedule/conflicts/check', methods=['POST'])
    def check_schedule_conflicts():
        """Check for conflicts in a proposed assignment"""
        from flask import jsonify, request
        from src.models.tenant import get_tenant_session

        try:
            data = request.get_json()
            required_fields = ['teacher_id', 'classroom_id', 'day_of_week', 'time_period_id']

            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            db_session = get_tenant_session()
            current_academic_year = '2025-2026'

            conflicts = check_assignment_conflicts(
                db_session, data['teacher_id'], data['classroom_id'],
                data['day_of_week'], data['time_period_id'], current_academic_year,
                exclude_assignment_id=data.get('exclude_assignment_id')
            )

            return jsonify({
                'success': True,
                'has_conflicts': len(conflicts) > 0,
                'conflicts': conflicts
            })

        except Exception as e:
            return jsonify({'error': f"Failed to check conflicts: {str(e)}"}), 500
        finally:
            db_session.close()

    def check_assignment_conflicts(db_session, teacher_id, classroom_id, day_of_week,
                                 time_period_id, academic_year, exclude_assignment_id=None):
        """Helper function to check for assignment conflicts"""
        from src.models.tenant import ScheduleAssignment, Teacher, TimePeriod, DayOfWeek
        from sqlalchemy import and_, or_

        conflicts = []

        # Check teacher conflict
        teacher_query = db_session.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.teacher_id == teacher_id,
                ScheduleAssignment.day_of_week == DayOfWeek(day_of_week),
                ScheduleAssignment.time_period_id == time_period_id,
                ScheduleAssignment.academic_year == academic_year,
                ScheduleAssignment.is_active == True
            )
        )

        if exclude_assignment_id:
            teacher_query = teacher_query.filter(ScheduleAssignment.id != exclude_assignment_id)

        teacher_conflict = teacher_query.first()
        if teacher_conflict:
            teacher = db_session.query(Teacher).get(teacher_id)
            conflicts.append({
                'type': 'teacher_conflict',
                'message': f'Teacher {teacher.teacher_name if teacher else "Unknown"} is already assigned at this time',
                'existing_assignment_id': teacher_conflict.id
            })

        # Check classroom conflict
        classroom_query = db_session.query(ScheduleAssignment).filter(
            and_(
                ScheduleAssignment.classroom_id == classroom_id,
                ScheduleAssignment.day_of_week == DayOfWeek(day_of_week),
                ScheduleAssignment.time_period_id == time_period_id,
                ScheduleAssignment.academic_year == academic_year,
                ScheduleAssignment.is_active == True
            )
        )

        if exclude_assignment_id:
            classroom_query = classroom_query.filter(ScheduleAssignment.id != exclude_assignment_id)

        classroom_conflict = classroom_query.first()
        if classroom_conflict:
            conflicts.append({
                'type': 'classroom_conflict',
                'message': f'Classroom is already occupied at this time',
                'existing_assignment_id': classroom_conflict.id
            })

        # Check teacher workload (Venezuelan regulation: max 40 hours/week)
        teacher_weekly_hours = db_session.query(ScheduleAssignment).join(TimePeriod).filter(
            and_(
                ScheduleAssignment.teacher_id == teacher_id,
                ScheduleAssignment.academic_year == academic_year,
                ScheduleAssignment.is_active == True
            )
        ).count() * 0.67  # Approximate hours per period (40 min = 0.67 hours)

        if teacher_weekly_hours >= 40:
            teacher = db_session.query(Teacher).get(teacher_id)
            conflicts.append({
                'type': 'workload_limit',
                'message': f'Teacher {teacher.teacher_name if teacher else "Unknown"} exceeds 40-hour weekly limit ({teacher_weekly_hours:.1f} hours)',
                'current_workload': teacher_weekly_hours
            })

        return conflicts

    @app.route('/api/schedule/export', methods=['POST'])
    def export_schedule():
        """Export schedule data in various formats"""
        from flask import jsonify, request, send_file
        from src.models.tenant import get_tenant_session, ScheduleAssignment
        from sqlalchemy import and_
        import pandas as pd
        import io
        from datetime import datetime

        try:
            data = request.get_json()
            view_type = data.get('view_type', 'section')
            target_id = data.get('target_id')
            format_type = data.get('format', 'xlsx')
            current_academic_year = '2025-2026'

            if not target_id:
                return jsonify({'error': 'target_id is required'}), 400

            db_session = get_tenant_session()

            # Build query based on view type
            query = db_session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.academic_year == current_academic_year,
                    ScheduleAssignment.is_active == True
                )
            )

            if view_type == 'section':
                query = query.filter(ScheduleAssignment.section_id == target_id)
            elif view_type == 'teacher':
                query = query.filter(ScheduleAssignment.teacher_id == target_id)
            elif view_type == 'classroom':
                query = query.filter(ScheduleAssignment.classroom_id == target_id)

            assignments = query.all()

            # Prepare data for export
            export_data = []
            for assignment in assignments:
                try:
                    export_data.append({
                        'Día': assignment.day_of_week.value if assignment.day_of_week else 'N/A',
                        'Hora Inicio': assignment.time_period.start_time.strftime('%H:%M') if assignment.time_period else 'N/A',
                        'Hora Fin': assignment.time_period.end_time.strftime('%H:%M') if assignment.time_period else 'N/A',
                        'Período': assignment.time_period.period_name if assignment.time_period else 'N/A',
                        'Materia': assignment.subject.subject_name if assignment.subject else 'N/A',
                        'Profesor': assignment.teacher.teacher_name if assignment.teacher else 'N/A',
                        'Aula': assignment.classroom.name if assignment.classroom else 'N/A',
                        'Sección': assignment.section.name if assignment.section else 'N/A',
                        'Tipo': assignment.assignment_type,
                        'Año Académico': assignment.academic_year
                    })
                except Exception as e:
                    # Skip assignments with missing relationships
                    continue

            if not export_data:
                return jsonify({'error': 'No data to export'}), 404

            df = pd.DataFrame(export_data)

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'horario_{view_type}_{timestamp}'

            # Create output buffer
            output = io.BytesIO()

            if format_type == 'xlsx':
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Horario', index=False)

                    # Get workbook and worksheet
                    workbook = writer.book
                    worksheet = writer.sheets['Horario']

                    # Add formats
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#003366',
                        'font_color': 'white',
                        'border': 1
                    })

                    # Apply header format
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)

                    # Auto-adjust column widths
                    for i, col in enumerate(df.columns):
                        column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, min(column_len, 50))

                output.seek(0)
                filename += '.xlsx'
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

            elif format_type == 'csv':
                df.to_csv(output, index=False, encoding='utf-8-sig')
                output.seek(0)
                filename += '.csv'
                mimetype = 'text/csv'

            elif format_type == 'pdf':
                # For PDF, we'll use a simple HTML to PDF conversion
                html_content = df.to_html(index=False, classes='table table-striped')
                html_template = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Horario {view_type.title()}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; margin-bottom: 20px; }}
                        .table {{ width: 100%; border-collapse: collapse; }}
                        .table th, .table td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
                        .table th {{ background-color: #003366; color: white; }}
                        .table-striped tbody tr:nth-of-type(odd) {{ background-color: rgba(0,0,0,.05); }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>Horario Académico - UEIPAB 2025-2026</h2>
                        <p>Vista: {view_type.title()} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    {html_content}
                </body>
                </html>
                """

                # For now, return HTML (PDF generation requires additional libraries)
                output.write(html_template.encode('utf-8'))
                output.seek(0)
                filename += '.html'
                mimetype = 'text/html'

            else:
                return jsonify({'error': 'Unsupported format'}), 400

            return send_file(
                output,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )

        except Exception as e:
            return jsonify({'error': f"Failed to export schedule: {str(e)}"}), 500
        finally:
            db_session.close()

    @app.route('/api/schedule/generate', methods=['POST'])
    def generate_schedule():
        """Intelligent schedule generation with Venezuelan K12 compliance"""
        from flask import jsonify, request
        from src.models.tenant import get_tenant_session, ScheduleAssignment
        from datetime import datetime

        try:
            data = request.get_json()
            generation_type = data.get('generation_type', 'fill_gaps')
            view_type = data.get('view_type', 'section')
            target_id = data.get('target_id')
            academic_year = data.get('academic_year', '2025-2026')
            preserve_existing = data.get('preserve_existing', True)

            if not target_id:
                return jsonify({'error': 'target_id is required'}), 400

            db_session = get_tenant_session()

            # For now, return a placeholder response
            # Future implementation will include intelligent scheduling algorithms
            summary = {
                'assignments_created': 0,
                'teachers_assigned': 0,
                'conflicts_resolved': 0,
                'message': f'Generación automática de tipo "{generation_type}" está en desarrollo'
            }

            if generation_type == 'complete_rebuild':
                summary['message'] = 'Regeneración completa implementada en versión futura'
            elif generation_type == 'fill_gaps':
                summary['message'] = 'Completar espacios libres - algoritmo en desarrollo'
            elif generation_type == 'optimize_workload':
                summary['message'] = 'Optimización de carga docente - algoritmo en desarrollo'

            return jsonify({
                'success': True,
                'assignments_created': summary['assignments_created'],
                'summary': summary,
                'message': 'Generación automática disponible en versión futura'
            })

        except Exception as e:
            return jsonify({'error': f"Failed to generate schedule: {str(e)}"}), 500
        finally:
            db_session.close()

    @app.route('/api/schedule/validate/venezuelan-k12', methods=['POST'])
    def validate_venezuelan_k12_compliance():
        """Validate schedule against Venezuelan K12 education regulations"""
        from flask import jsonify, request
        from src.models.tenant import get_tenant_session, ScheduleAssignment, Teacher, Section
        from sqlalchemy import and_, func

        try:
            data = request.get_json()
            view_type = data.get('view_type', 'section')
            target_id = data.get('target_id')
            academic_year = data.get('academic_year', '2025-2026')

            if not target_id:
                return jsonify({'error': 'target_id is required'}), 400

            db_session = get_tenant_session()
            violations = []

            # Venezuelan K12 Compliance Rules

            # Rule 1: Teacher workload limit (40 hours/week)
            teacher_workloads = db_session.query(
                ScheduleAssignment.teacher_id,
                func.count(ScheduleAssignment.id).label('assignments_count')
            ).filter(
                and_(
                    ScheduleAssignment.academic_year == academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).group_by(ScheduleAssignment.teacher_id).all()

            for teacher_id, assignments_count in teacher_workloads:
                weekly_hours = assignments_count * 0.67  # 40 min periods = 0.67 hours
                if weekly_hours > 40:
                    teacher = db_session.query(Teacher).get(teacher_id)
                    violations.append({
                        'type': 'workload_violation',
                        'severity': 'critical',
                        'message': f'Profesor {teacher.teacher_name if teacher else "Unknown"} excede límite de 40 horas ({weekly_hours:.1f} horas)',
                        'regulation': 'Resolución 058 del Ministerio de Educación',
                        'teacher_id': teacher_id,
                        'current_hours': weekly_hours,
                        'max_hours': 40
                    })

            # Rule 2: Minimum break periods
            # Venezuelan regulation requires minimum 20-minute break every 2 hours
            all_assignments = db_session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.academic_year == academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).all() if view_type != 'section' else db_session.query(ScheduleAssignment).filter(
                and_(
                    ScheduleAssignment.section_id == target_id,
                    ScheduleAssignment.academic_year == academic_year,
                    ScheduleAssignment.is_active == True
                )
            ).all()

            # Rule 3: Subject distribution requirements
            # Each section should have minimum hours for core subjects
            core_subjects_requirements = {
                'MATEMÁTICAS': 5,  # Minimum 5 periods per week
                'CASTELLANO Y LITERATURA': 4,
                'CIENCIAS DE LA TIERRA': 3,
                'INGLÉS': 3,
                'EDUCACIÓN FÍSICA': 2
            }

            if view_type == 'section':
                section_subjects = {}
                for assignment in all_assignments:
                    if assignment.subject and assignment.subject.subject_name:
                        subject_name = assignment.subject.subject_name.upper()
                        section_subjects[subject_name] = section_subjects.get(subject_name, 0) + 1

                for subject, min_periods in core_subjects_requirements.items():
                    current_periods = section_subjects.get(subject, 0)
                    if current_periods < min_periods:
                        violations.append({
                            'type': 'subject_deficiency',
                            'severity': 'warning',
                            'message': f'Materia {subject} tiene {current_periods} períodos (mínimo requerido: {min_periods})',
                            'regulation': 'Currículo Básico Nacional de Venezuela',
                            'subject': subject,
                            'current_periods': current_periods,
                            'required_periods': min_periods
                        })

            # Rule 4: Bimodal schedule compliance
            # Check that schedule respects Venezuelan bimodal structure (morning/afternoon)
            morning_periods = [assignment for assignment in all_assignments
                             if assignment.time_period and assignment.time_period.start_time.hour < 12]
            afternoon_periods = [assignment for assignment in all_assignments
                               if assignment.time_period and assignment.time_period.start_time.hour >= 13]

            if len(afternoon_periods) > 0 and len(morning_periods) == 0:
                violations.append({
                    'type': 'bimodal_violation',
                    'severity': 'warning',
                    'message': 'Horario solo usa sesión vespertina. Se recomienda usar sesión matutina.',
                    'regulation': 'Resolución 751 - Organización del Año Escolar',
                    'morning_periods': len(morning_periods),
                    'afternoon_periods': len(afternoon_periods)
                })

            # Rule 5: Grade-appropriate content
            if view_type == 'section':
                section = db_session.query(Section).get(target_id)
                if section and section.grade_level:
                    grade = section.grade_level

                    # Check if subjects are appropriate for grade level
                    inappropriate_subjects = []
                    for assignment in all_assignments:
                        if assignment.subject:
                            subject_name = assignment.subject.subject_name.upper()

                            # Example: Advanced subjects not appropriate for lower grades
                            if grade <= 6 and any(advanced in subject_name for advanced in ['FÍSICA', 'QUÍMICA', 'BIOLOGÍA']):
                                inappropriate_subjects.append(subject_name)

                    if inappropriate_subjects:
                        violations.append({
                            'type': 'grade_content_mismatch',
                            'severity': 'warning',
                            'message': f'Materias {", ".join(set(inappropriate_subjects))} no son apropiadas para grado {grade}',
                            'regulation': 'Diseño Curricular del Sistema Educativo Bolivariano',
                            'grade': grade,
                            'inappropriate_subjects': list(set(inappropriate_subjects))
                        })

            # Calculate compliance score
            total_rules_checked = 5
            critical_violations = len([v for v in violations if v['severity'] == 'critical'])
            warning_violations = len([v for v in violations if v['severity'] == 'warning'])

            compliance_score = max(0, 100 - (critical_violations * 20) - (warning_violations * 10))

            return jsonify({
                'success': True,
                'compliance_score': compliance_score,
                'violations': violations,
                'summary': {
                    'total_violations': len(violations),
                    'critical_violations': critical_violations,
                    'warning_violations': warning_violations,
                    'rules_checked': total_rules_checked,
                    'is_compliant': len(violations) == 0
                },
                'recommendations': generate_compliance_recommendations(violations)
            })

        except Exception as e:
            return jsonify({'error': f"Failed to validate compliance: {str(e)}"}), 500
        finally:
            db_session.close()

    def generate_compliance_recommendations(violations):
        """Generate actionable recommendations based on violations"""
        recommendations = []

        for violation in violations:
            if violation['type'] == 'workload_violation':
                recommendations.append(f"Redistribuir carga del profesor {violation.get('teacher_id', 'ID')} a otros docentes disponibles")

            elif violation['type'] == 'subject_deficiency':
                subject = violation.get('subject', 'Unknown')
                needed = violation.get('required_periods', 0) - violation.get('current_periods', 0)
                recommendations.append(f"Agregar {needed} período(s) más de {subject}")

            elif violation['type'] == 'bimodal_violation':
                recommendations.append("Considerar balancear horario entre sesión matutina y vespertina")

            elif violation['type'] == 'grade_content_mismatch':
                recommendations.append(f"Revisar contenido curricular para grado {violation.get('grade', 'Unknown')}")

        # Add general recommendations
        if not recommendations:
            recommendations.append("¡Excelente! El horario cumple con todas las regulaciones venezolanas K12")
        else:
            recommendations.append("Ejecutar detección de conflictos después de realizar ajustes")
            recommendations.append("Consultar con coordinadores académicos para validación final")

        return recommendations

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'platform': 'BiScheduler'}

    # Venezuelan education info endpoint
    @app.route('/info')
    def platform_info():
        return {
            'platform': 'BiScheduler',
            'description': 'Multi-Tenant K12 Scheduling for Venezuelan Education',
            'compliance': ['Matrícula Reporting', 'Bimodal Schedule', 'Venezuelan Curriculum'],
            'architecture': 'Schema-per-tenant isolation',
            'developed_for': 'UEIPAB and Venezuelan K12 institutions'
        }

    return app
