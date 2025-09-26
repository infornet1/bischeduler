"""
BiScheduler Authentication Decorators
Role-based access control for Venezuelan K12 platform
Enhanced with tenant context and permission validation
"""

from functools import wraps
from typing import List, Optional, Union
from flask import request, jsonify, g, current_app
from werkzeug.exceptions import Unauthorized, Forbidden
import jwt

from src.auth.jwt_service import JWTService


def get_session_info() -> dict:
    """Extract session information from request"""
    return {
        'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        'user_agent': request.headers.get('User-Agent'),
        'device_info': {
            'method': request.method,
            'endpoint': request.endpoint,
            'url': request.url
        }
    }


def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove 'Bearer ' prefix
    return None


def jwt_required(f):
    """
    Decorator to require valid JWT token
    Sets g.current_user with decoded token payload
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()

        if not token:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Missing or invalid Authorization header'
            }), 401

        try:
            jwt_service = JWTService()
            payload = jwt_service.decode_token(token)

            # Set current user context
            g.current_user = payload
            g.session_info = get_session_info()

            return f(*args, **kwargs)

        except Unauthorized as e:
            return jsonify({
                'error': 'Authentication failed',
                'message': str(e)
            }), 401
        except Exception as e:
            current_app.logger.error(f"JWT validation error: {str(e)}")
            return jsonify({
                'error': 'Authentication error',
                'message': 'Token validation failed'
            }), 401

    return decorated_function


def roles_required(*roles: str):
    """
    Decorator to require specific user roles
    Can accept multiple roles (user needs at least one)

    Usage:
        @roles_required('school_admin', 'platform_admin')
        def admin_only_view():
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            user_role = g.current_user.get('role')

            if user_role not in roles:
                return jsonify({
                    'error': 'Insufficient privileges',
                    'message': f'Required role: {" or ".join(roles)}',
                    'user_role': user_role
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permissions_required(*permissions: str):
    """
    Decorator to require specific permissions
    Checks permissions in user's JWT payload

    Usage:
        @permissions_required('manage_schedules', 'view_reports')
        def schedule_management():
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            user_permissions = g.current_user.get('permissions', [])

            # Platform admins have all permissions
            if '*' in user_permissions:
                return f(*args, **kwargs)

            # Check if user has any of the required permissions
            if not any(perm in user_permissions for perm in permissions):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'Required permissions: {", ".join(permissions)}',
                    'user_permissions': user_permissions
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def tenant_required(tenant_param: str = 'tenant_id'):
    """
    Decorator to validate tenant access
    Ensures user can only access their assigned tenant

    Args:
        tenant_param: URL parameter name containing tenant ID

    Usage:
        @tenant_required('tenant_id')
        def tenant_specific_view(tenant_id):
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            # Get tenant ID from URL parameters
            required_tenant_id = kwargs.get(tenant_param)

            if not required_tenant_id:
                return jsonify({
                    'error': 'Tenant required',
                    'message': 'Tenant ID not specified in request'
                }), 400

            # Validate tenant access
            jwt_service = JWTService()
            if not jwt_service.validate_tenant_access(g.current_user, required_tenant_id):
                return jsonify({
                    'error': 'Tenant access denied',
                    'message': 'You do not have access to this tenant',
                    'user_tenant': g.current_user.get('tenant_id'),
                    'requested_tenant': required_tenant_id
                }), 403

            # Set tenant context
            g.current_tenant_id = required_tenant_id

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def school_admin_required(f):
    """Decorator for school administrator access"""
    return roles_required('school_admin', 'platform_admin')(f)


def teacher_or_admin_required(f):
    """Decorator for teacher or administrator access"""
    return roles_required('teacher', 'academic_coordinator', 'school_admin', 'platform_admin')(f)


def platform_admin_required(f):
    """Decorator for platform administrator access only"""
    return roles_required('platform_admin')(f)


def active_user_required(f):
    """
    Decorator to ensure user account is active
    Validates user status in database
    """
    @wraps(f)
    @jwt_required
    def decorated_function(*args, **kwargs):
        from src.core.app import db
        from src.models.auth import User

        user_id = g.current_user.get('user_id')
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user or not user.is_active():
            return jsonify({
                'error': 'Account inactive',
                'message': 'User account is not active'
            }), 403

        # Update last activity
        user.update_last_activity()
        db.session.commit()

        return f(*args, **kwargs)
    return decorated_function


def audit_action(action: str, resource_type: str = None):
    """
    Decorator to automatically log user actions
    Creates audit trail for Venezuelan compliance

    Usage:
        @audit_action('create_schedule', 'schedule')
        def create_schedule():
            pass
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            from src.core.app import db
            from src.models.auth import UserAuditLog

            # Execute the function first
            result = f(*args, **kwargs)

            # Log the action
            try:
                user_id = g.current_user.get('user_id')
                tenant_id = g.current_user.get('tenant_id')
                session_info = getattr(g, 'session_info', {})

                UserAuditLog.log_action(
                    db.session,
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    tenant_id=tenant_id,
                    description=f"User action: {action}",
                    ip_address=session_info.get('ip_address'),
                    user_agent=session_info.get('user_agent'),
                    session_id=g.current_user.get('session_id')
                )

                db.session.commit()

            except Exception as e:
                current_app.logger.error(f"Audit logging failed: {str(e)}")
                # Don't fail the request if audit logging fails

            return result
        return decorated_function
    return decorator


def rate_limit(max_requests: int = 100, window_minutes: int = 60):
    """
    Simple rate limiting decorator
    Limits requests per user per time window

    Args:
        max_requests: Maximum requests allowed
        window_minutes: Time window in minutes
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            # In production, implement with Redis or database
            # For now, this is a placeholder

            user_id = g.current_user.get('user_id')

            # TODO: Implement actual rate limiting logic
            # Check user's request count in the time window
            # Increment counter or reject if limit exceeded

            return f(*args, **kwargs)
        return decorated_function
    return decorator


class AuthenticationMiddleware:
    """
    Flask authentication middleware for BiScheduler
    Handles global authentication and security headers
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize authentication middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """Process request before route handler"""
        # Skip authentication for certain endpoints
        if request.endpoint in ['auth.login', 'auth.register', 'health', 'static']:
            return

        # Add request ID for tracking
        g.request_id = request.headers.get('X-Request-ID', 'unknown')

        # Add CORS headers for Venezuelan domain access
        if request.origin and 'ueipab.edu.ve' in request.origin:
            g.cors_origin = request.origin

    def after_request(self, response):
        """Process response after route handler"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Add CORS headers if origin is allowed
        if hasattr(g, 'cors_origin'):
            response.headers['Access-Control-Allow-Origin'] = g.cors_origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        return response


def optional_jwt(f):
    """
    Decorator for optional JWT authentication
    Sets g.current_user if token is present and valid
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_request()

        if token:
            try:
                jwt_service = JWTService()
                payload = jwt_service.decode_token(token)
                g.current_user = payload
                g.session_info = get_session_info()
            except Exception:
                # Token is invalid, but continue without authentication
                g.current_user = None
        else:
            g.current_user = None

        return f(*args, **kwargs)
    return decorated_function