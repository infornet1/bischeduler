"""
BiScheduler Authentication Views
Authentication endpoints for Venezuelan K12 platform
Enhanced with multi-tenant support and security features
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden
from datetime import datetime, timezone
import re

from src.auth.jwt_service import JWTService, AuthenticationService
from src.auth.decorators import jwt_required, platform_admin_required, audit_action
from src.models.auth import User, UserRole, UserStatus
from src.models.master import TenantInvitation


# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize services
jwt_service = JWTService()
auth_service = AuthenticationService(jwt_service)


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength for Venezuelan security requirements

    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, ""


def get_request_info():
    """Extract request information for logging"""
    return {
        'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        'user_agent': request.headers.get('User-Agent'),
        'device_info': {
            'method': request.method,
            'endpoint': request.endpoint
        }
    }


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens

    Request JSON:
        {
            "email": "admin@ueipab.edu.ve",
            "password": "password123",
            "tenant_id": "optional_tenant_id"
        }

    Response:
        {
            "access_token": "jwt_token",
            "refresh_token": "jwt_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {...}
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'JSON data required'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        tenant_id = data.get('tenant_id')

        # Validate required fields
        if not email or not password:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Email and password are required'
            }), 400

        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400

        # Authenticate user
        session_info = get_request_info()
        token_data, user = auth_service.authenticate_user(email, password, tenant_id, session_info)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            **token_data
        }), 200

    except Unauthorized as e:
        return jsonify({
            'error': 'Authentication failed',
            'message': str(e)
        }), 401
    except Forbidden as e:
        return jsonify({
            'error': 'Access denied',
            'message': str(e)
        }), 403
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Login failed',
            'message': 'An error occurred during login'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """
    Logout user and revoke current session

    Headers:
        Authorization: Bearer <access_token>

    Response:
        {
            "success": true,
            "message": "Logout successful"
        }
    """
    try:
        from flask import g

        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            session_info = get_request_info()
            auth_service.logout_user(token, session_info)

        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': True,  # Always return success for logout
            'message': 'Logout completed'
        }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using refresh token

    Request JSON:
        {
            "refresh_token": "jwt_refresh_token"
        }

    Response:
        {
            "access_token": "new_jwt_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'JSON data required'}), 400

        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({
                'error': 'Refresh token required',
                'message': 'Refresh token must be provided'
            }), 400

        # Refresh tokens
        session_info = get_request_info()
        token_data = auth_service.refresh_user_token(refresh_token, session_info)

        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            **token_data
        }), 200

    except Unauthorized as e:
        return jsonify({
            'error': 'Token refresh failed',
            'message': str(e)
        }), 401
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'Refresh failed',
            'message': 'Unable to refresh token'
        }), 500


@auth_bp.route('/register', methods=['POST'])
@platform_admin_required
@audit_action('user_registration', 'user')
def register():
    """
    Register new user (platform admin only)

    Request JSON:
        {
            "email": "teacher@ueipab.edu.ve",
            "password": "SecurePass123!",
            "first_name": "María",
            "last_name": "González",
            "role": "teacher",
            "tenant_id": "ueipab_tenant_id",
            "cedula": "12345678"
        }
    """
    try:
        from src.core.app import db

        data = request.get_json()

        if not data:
            return jsonify({'error': 'JSON data required'}), 400

        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'Missing field: {field}',
                    'message': f'{field} is required'
                }), 400

        email = data['email'].strip().lower()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        role = data['role']
        tenant_id = data.get('tenant_id')
        cedula = data.get('cedula', '').strip()

        # Validate email
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400

        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return jsonify({
                'error': 'Invalid password',
                'message': password_error
            }), 400

        # Validate role
        valid_roles = [role.value for role in UserRole]
        if role not in valid_roles:
            return jsonify({
                'error': 'Invalid role',
                'message': f'Role must be one of: {", ".join(valid_roles)}'
            }), 400

        # Check if user already exists
        existing_user = db.session.query(User).filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'error': 'User exists',
                'message': 'User with this email already exists'
            }), 409

        # Check for duplicate cedula if provided
        if cedula:
            existing_cedula = db.session.query(User).filter_by(cedula=cedula).first()
            if existing_cedula:
                return jsonify({
                    'error': 'Cedula exists',
                    'message': 'User with this cedula already exists'
                }), 409

        # Create new user
        user = User(
            email=email,
            username=email.split('@')[0],  # Use email prefix as username
            first_name=first_name,
            last_name=last_name,
            role=role,
            tenant_id=tenant_id,
            cedula=cedula,
            status=UserStatus.ACTIVE.value,  # Direct activation for admin-created users
            email_verified_at=datetime.now(timezone.utc)
        )

        user.set_password(password)

        # Set creator
        from flask import g
        user.created_by = g.current_user.get('user_id')

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'tenant_id': user.tenant_id
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Registration failed',
            'message': 'An error occurred during registration'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    """
    Get current user profile

    Headers:
        Authorization: Bearer <access_token>

    Response:
        {
            "user": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "User Name",
                "role": "teacher",
                "permissions": ["view_schedules"]
            }
        }
    """
    try:
        from flask import g
        from src.core.app import db

        user_id = g.current_user.get('user_id')
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User account no longer exists'
            }), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'role': user.role,
                'display_role': user.display_role,
                'tenant_id': user.tenant_id,
                'cedula': user.cedula,
                'phone': user.phone,
                'language': user.language,
                'timezone': user.timezone,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat(),
                'permissions': g.current_user.get('permissions', [])
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Profile error: {str(e)}")
        return jsonify({
            'error': 'Profile retrieval failed',
            'message': 'Unable to retrieve user profile'
        }), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required
@audit_action('profile_update', 'user')
def update_profile():
    """
    Update current user profile

    Request JSON:
        {
            "first_name": "Updated Name",
            "last_name": "Updated Last",
            "phone": "+58-212-1234567",
            "language": "es",
            "timezone": "America/Caracas"
        }
    """
    try:
        from flask import g
        from src.core.app import db

        data = request.get_json()

        if not data:
            return jsonify({'error': 'JSON data required'}), 400

        user_id = g.current_user.get('user_id')
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User account no longer exists'
            }), 404

        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'language', 'timezone']
        updated_fields = []

        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'updated_fields': updated_fields
        }), 200

    except Exception as e:
        current_app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({
            'error': 'Profile update failed',
            'message': 'Unable to update profile'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required
@audit_action('password_change', 'user')
def change_password():
    """
    Change user password

    Request JSON:
        {
            "current_password": "current_password",
            "new_password": "new_secure_password"
        }
    """
    try:
        from flask import g
        from src.core.app import db

        data = request.get_json()

        if not data:
            return jsonify({'error': 'JSON data required'}), 400

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({
                'error': 'Passwords required',
                'message': 'Both current and new passwords are required'
            }), 400

        user_id = g.current_user.get('user_id')
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User account no longer exists'
            }), 404

        # Verify current password
        if not user.check_password(current_password):
            return jsonify({
                'error': 'Invalid password',
                'message': 'Current password is incorrect'
            }), 400

        # Validate new password
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            return jsonify({
                'error': 'Invalid new password',
                'message': password_error
            }), 400

        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        # Revoke all existing sessions except current one
        current_session_id = g.current_user.get('session_id')
        jwt_service.revoke_all_user_tokens(user.id, 'password_change')

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200

    except Exception as e:
        current_app.logger.error(f"Password change error: {str(e)}")
        return jsonify({
            'error': 'Password change failed',
            'message': 'Unable to change password'
        }), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    Verify if token is valid (for frontend validation)

    Request JSON:
        {
            "token": "jwt_access_token"
        }

    Response:
        {
            "valid": true,
            "user": {...},
            "expires_at": "2024-01-01T00:00:00Z"
        }
    """
    try:
        data = request.get_json()

        if not data or not data.get('token'):
            return jsonify({
                'valid': False,
                'message': 'Token required'
            }), 400

        token = data['token']
        payload = jwt_service.decode_token(token)

        return jsonify({
            'valid': True,
            'user': {
                'id': payload.get('user_id'),
                'email': payload.get('email'),
                'role': payload.get('role'),
                'tenant_id': payload.get('tenant_id')
            },
            'expires_at': payload.get('exp')
        }), 200

    except Unauthorized:
        return jsonify({
            'valid': False,
            'message': 'Invalid or expired token'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'valid': False,
            'message': 'Token verification failed'
        }), 500


@auth_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad request',
        'message': 'Invalid request data'
    }), 400


@auth_bp.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized errors"""
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401


@auth_bp.errorhandler(403)
def forbidden(error):
    """Handle forbidden errors"""
    return jsonify({
        'error': 'Forbidden',
        'message': 'Insufficient privileges'
    }), 403


@auth_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    current_app.logger.error(f"Internal error in auth views: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500