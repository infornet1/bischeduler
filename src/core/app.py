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

    # Main landing page
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    # Login page
    @app.route('/login')
    def login_page():
        from flask import render_template
        return render_template('login.html')

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