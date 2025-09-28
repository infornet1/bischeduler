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
    app.register_blueprint(auth_bp)

    # Import and register scheduling blueprint
    from src.scheduling.views import scheduling_bp
    app.register_blueprint(scheduling_bp)

    # Import and register schedule optimizer blueprint (Phase 8)
    from src.api.schedule_optimizer import schedule_optimizer_bp
    app.register_blueprint(schedule_optimizer_bp)

    # Import and register attendance blueprint (Phase 11)
    from src.attendance.views import attendance_bp
    app.register_blueprint(attendance_bp)

    # Main landing page
    @app.route('/')
    def index():
        from flask import render_template, g
        from src.tenants.middleware import get_current_tenant
        from src.models.master import Tenant

        # For demo purposes, default to UEIPAB tenant if no tenant context
        current_tenant = get_current_tenant()
        if not current_tenant:
            # Default to UEIPAB tenant for direct access
            current_tenant = db.session.query(Tenant).filter_by(institution_name='UEIPAB').first()

        return render_template('index.html', current_tenant=current_tenant)

    # Login page
    @app.route('/login')
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
    def dashboard():
        from flask import render_template
        return render_template('dashboard.html')

    # Teacher portal page (Phase 4 - Teacher Self-Service)
    @app.route('/teacher-portal')
    def teacher_portal():
        from flask import render_template
        return render_template('teacher_portal.html')

    # Exam calendar page (Phase 6 - Exam Scheduling)
    @app.route('/exam-calendar')
    def exam_calendar():
        from flask import render_template
        return render_template('exam_calendar.html')

    # Student exam dashboard (Phase 6 - Student exam alerts)
    @app.route('/student-exams')
    def student_exam_dashboard():
        from flask import render_template
        return render_template('student_exam_dashboard.html')

    # Core Management Routes (Should exist from Phases 1-4)
    @app.route('/schedules')
    def schedules():
        from flask import render_template
        return render_template('schedules.html')

    @app.route('/schedule-management')
    def schedule_management():
        from flask import render_template
        return render_template('schedule_management.html')

    @app.route('/section-schedules')
    def section_schedules():
        from flask import render_template
        return render_template('section_schedules.html')

    @app.route('/conflict-resolution')
    def conflict_resolution():
        from flask import render_template
        return render_template('conflict_resolution.html')

    @app.route('/students')
    def students():
        from flask import render_template
        return render_template('students.html')

    @app.route('/teachers')
    def teachers():
        from flask import render_template
        return render_template('teachers.html')

    @app.route('/classrooms')
    def classrooms():
        from flask import render_template
        return render_template('classrooms.html')

    # Phase 7: Parent Portal
    @app.route('/parent-portal')
    def parent_portal():
        from flask import render_template
        return render_template('parent_portal.html')

    # Phase 8: Schedule Optimizer
    @app.route('/schedule-optimizer')
    def schedule_optimizer():
        from flask import render_template
        return render_template('schedule_optimizer.html')

    # Future Phase Routes (Placeholder pages)
    @app.route('/bimodal')
    def bimodal():
        from flask import render_template
        return render_template('coming_soon.html',
                             feature_name="Gestión Bimodal",
                             feature_description="Horarios presencial/virtual",
                             phase="Fase 7")

    @app.route('/matricula')
    def matricula():
        from flask import render_template
        return render_template('coming_soon.html',
                             feature_name="Reportes de Matrícula",
                             feature_description="Informes oficiales MINED",
                             phase="Fase 8")

    @app.route('/reports')
    def reports():
        from flask import render_template
        return render_template('coming_soon.html',
                             feature_name="Sistema de Reportes",
                             feature_description="Informes académicos y administrativos",
                             phase="Fase 9")

    @app.route('/admin')
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