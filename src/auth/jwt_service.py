"""
BiScheduler JWT Authentication Service
Multi-tenant JWT management for Venezuelan K12 platform
Enhanced with security features and tenant context
"""

import jwt
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple
from flask import current_app, request
from werkzeug.exceptions import Unauthorized, Forbidden
import hashlib
import json

from src.models.auth import User, UserSession, UserAuditLog
from flask import current_app


class JWTService:
    """
    JWT authentication service for BiScheduler multi-tenant platform
    Handles token generation, validation, and tenant context
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize JWT service with Flask app"""
        app.config.setdefault('JWT_SECRET_KEY', secrets.token_urlsafe(32))
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=8))
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_ISSUER', 'BiScheduler-Venezuela')

    def generate_tokens(self, user: User, tenant_id: str = None, session_info: Dict = None) -> Dict[str, str]:
        """
        Generate access and refresh tokens for user with tenant context

        Args:
            user: User object
            tenant_id: Optional tenant context
            session_info: Session metadata (IP, user agent, etc.)

        Returns:
            Dictionary with access_token, refresh_token, and metadata
        """
        now = datetime.now(timezone.utc)

        # Base payload for both tokens
        base_payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'tenant_id': tenant_id or user.tenant_id,
            'iss': current_app.config['JWT_ISSUER'],
            'iat': now,
            'sub': str(user.id)
        }

        # Access token (short-lived)
        access_payload = {
            **base_payload,
            'type': 'access',
            'exp': now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'permissions': self._get_user_permissions(user, tenant_id),
            'session_id': secrets.token_urlsafe(16)
        }

        # Refresh token (long-lived)
        refresh_payload = {
            **base_payload,
            'type': 'refresh',
            'exp': now + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
            'jti': secrets.token_urlsafe(32)  # JWT ID for revocation
        }

        # Generate tokens
        access_token = jwt.encode(
            access_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm=current_app.config['JWT_ALGORITHM']
        )

        refresh_token = jwt.encode(
            refresh_payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm=current_app.config['JWT_ALGORITHM']
        )

        # Create session record
        session_record = self._create_session_record(
            user, access_token, session_info, access_payload['session_id']
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()),
            'session_id': access_payload['session_id'],
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'full_name': user.full_name,
                'tenant_id': tenant_id or user.tenant_id
            }
        }

    def decode_token(self, token: str, verify_session: bool = True) -> Dict:
        """
        Decode and validate JWT token

        Args:
            token: JWT token string
            verify_session: Whether to verify active session

        Returns:
            Decoded token payload

        Raises:
            Unauthorized: Invalid or expired token
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=[current_app.config['JWT_ALGORITHM']],
                issuer=current_app.config['JWT_ISSUER']
            )

            # Verify session if requested
            if verify_session and payload.get('type') == 'access':
                if not self._verify_session(payload.get('session_id'), token):
                    raise Unauthorized('Session is no longer valid')

            return payload

        except jwt.ExpiredSignatureError:
            raise Unauthorized('Token has expired')
        except jwt.InvalidTokenError as e:
            raise Unauthorized(f'Invalid token: {str(e)}')

    def refresh_access_token(self, refresh_token: str, session_info: Dict = None) -> Dict[str, str]:
        """
        Generate new access token using refresh token

        Args:
            refresh_token: Valid refresh token
            session_info: Updated session metadata

        Returns:
            New token set
        """
        try:
            payload = self.decode_token(refresh_token, verify_session=False)

            if payload.get('type') != 'refresh':
                raise Unauthorized('Invalid refresh token')

            # Get user and validate
            from src.core.app import db
            user = db.session.query(User).filter_by(id=payload['user_id']).first()

            if not user or not user.is_active():
                raise Unauthorized('User account is not active')

            # Check if refresh token is revoked
            if self._is_token_revoked(refresh_token):
                raise Unauthorized('Refresh token has been revoked')

            # Generate new access token
            return self.generate_tokens(user, payload.get('tenant_id'), session_info)

        except jwt.ExpiredSignatureError:
            raise Unauthorized('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise Unauthorized('Invalid refresh token')

    def revoke_token(self, token: str, reason: str = 'user_logout'):
        """
        Revoke token and associated session

        Args:
            token: Token to revoke
            reason: Revocation reason
        """
        try:
            payload = self.decode_token(token, verify_session=False)
            session_id = payload.get('session_id')

            if session_id:
                self._revoke_session(session_id, reason)

        except Exception:
            # Token might already be invalid, but we still want to clean up
            pass

    def revoke_all_user_tokens(self, user_id: int, reason: str = 'security'):
        """
        Revoke all active tokens for a user

        Args:
            user_id: User ID
            reason: Revocation reason
        """
        from src.core.app import db

        # Revoke all active sessions
        sessions = db.session.query(UserSession).filter_by(
            user_id=user_id,
            is_active=True
        ).all()

        for session in sessions:
            session.revoke(reason)

        db.session.commit()

    def validate_tenant_access(self, user_payload: Dict, required_tenant_id: str) -> bool:
        """
        Validate user has access to specific tenant

        Args:
            user_payload: Decoded JWT payload
            required_tenant_id: Tenant ID to validate access for

        Returns:
            True if access is allowed
        """
        user_role = user_payload.get('role')
        user_tenant = user_payload.get('tenant_id')

        # Platform admins have access to all tenants
        if user_role == 'platform_admin':
            return True

        # Users can only access their assigned tenant
        return user_tenant == required_tenant_id

    def _get_user_permissions(self, user: User, tenant_id: str = None) -> list:
        """Get user permissions for JWT payload"""
        permissions = []

        if user.role == 'platform_admin':
            permissions = ['*']  # All permissions
        elif user.role == 'school_admin':
            permissions = [
                'manage_schedules', 'manage_teachers', 'manage_students',
                'manage_classrooms', 'view_reports', 'manage_users'
            ]
        elif user.role == 'academic_coordinator':
            permissions = [
                'manage_schedules', 'manage_teachers', 'manage_classrooms', 'view_reports'
            ]
        elif user.role == 'teacher':
            permissions = ['view_schedules', 'view_students', 'update_profile']
        elif user.role == 'parent':
            permissions = ['view_student_schedules', 'view_student_grades']
        elif user.role == 'viewer':
            permissions = ['view_schedules']

        # Add tenant-specific permissions if available
        if user.tenant_permissions and isinstance(user.tenant_permissions, list):
            permissions.extend(user.tenant_permissions)

        return list(set(permissions))  # Remove duplicates

    def _create_session_record(self, user: User, token: str, session_info: Dict, session_id: str) -> UserSession:
        """Create session record in database"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Check if this is a master database user
        if hasattr(user, '_is_master_user') and user._is_master_user:
            # Create session in master database
            import mysql.connector

            master_db_config = {
                'host': 'localhost',
                'user': 'root',
                'password': '0000',
                'database': 'bischeduler_master',
                'charset': 'utf8mb4'
            }

            try:
                master_conn = mysql.connector.connect(**master_db_config)
                master_cursor = master_conn.cursor()

                expires_at = datetime.now(timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']

                master_cursor.execute("""
                    INSERT INTO user_sessions
                    (user_id, session_token, jwt_token_hash, ip_address, user_agent,
                     device_info, created_at, last_activity, expires_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user.id, session_id, token_hash,
                    session_info.get('ip_address') if session_info else None,
                    session_info.get('user_agent') if session_info else None,
                    json.dumps(session_info.get('device_info')) if session_info and session_info.get('device_info') else None,
                    datetime.now(timezone.utc), datetime.now(timezone.utc), expires_at, True
                ))

                master_conn.commit()
                master_cursor.close()
                master_conn.close()

                # Create a dummy session object for return
                session = UserSession()
                session.user_id = user.id
                session.session_token = session_id
                session.jwt_token_hash = token_hash
                session.expires_at = expires_at
                session.is_active = True
                return session

            except Exception as e:
                current_app.logger.error(f"Failed to create master user session: {e}")
                raise
        else:
            # Create session in tenant database
            from src.core.app import db

            session = UserSession(
                user_id=user.id,
                session_token=session_id,
                jwt_token_hash=token_hash,
                ip_address=session_info.get('ip_address') if session_info else None,
                user_agent=session_info.get('user_agent') if session_info else None,
                device_info=session_info.get('device_info') if session_info else None,
                expires_at=datetime.now(timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            )

            db.session.add(session)
            db.session.commit()

            return session

    def _verify_session(self, session_id: str, token: str) -> bool:
        """Verify session is still active"""
        from src.core.app import db

        if not session_id:
            return False

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        session = db.session.query(UserSession).filter_by(
            session_token=session_id,
            jwt_token_hash=token_hash
        ).first()

        if not session:
            return False

        if not session.is_valid():
            return False

        # Update last activity
        session.update_activity()
        db.session.commit()

        return True

    def _revoke_session(self, session_id: str, reason: str):
        """Revoke specific session"""
        from src.core.app import db

        session = db.session.query(UserSession).filter_by(
            session_token=session_id
        ).first()

        if session:
            session.revoke(reason)
            db.session.commit()

    def _is_token_revoked(self, token: str) -> bool:
        """Check if token is in revocation list"""
        # In production, this could check a Redis cache or database
        # For now, we'll check if the session exists and is active
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=[current_app.config['JWT_ALGORITHM']],
                options={"verify_exp": False}  # Don't verify expiration for this check
            )

            if payload.get('type') == 'refresh':
                jti = payload.get('jti')
                # Check revocation list (implement as needed)
                return False

        except jwt.InvalidTokenError:
            return True

        return False


class AuthenticationService:
    """
    High-level authentication service for BiScheduler
    Handles login, logout, and user management
    """

    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service

    def authenticate_user(self, email: str, password: str, tenant_id: str = None,
                         session_info: Dict = None) -> Tuple[Dict, User]:
        """
        Authenticate user and generate tokens

        Args:
            email: User email
            password: User password
            tenant_id: Optional tenant context
            session_info: Session metadata

        Returns:
            Tuple of (token_data, user_object)

        Raises:
            Unauthorized: Invalid credentials or account issues
        """
        from src.core.app import db
        from src.tenants.manager import TenantManager
        import mysql.connector

        # First, try to find user in master database (for platform admins)
        user = None
        master_db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '0000',
            'database': 'bischeduler_master',
            'charset': 'utf8mb4'
        }

        try:
            # Check master database for platform admin users
            master_conn = mysql.connector.connect(**master_db_config)
            master_cursor = master_conn.cursor(dictionary=True)

            master_cursor.execute("""
                SELECT id, email, username, password_hash, first_name, last_name,
                       cedula, phone, role, status, password_reset_token,
                       password_reset_expires, email_verification_token,
                       email_verified_at, failed_login_attempts, locked_until,
                       tenant_id, tenant_permissions, last_login, last_activity,
                       current_session_token, language, timezone, ui_preferences,
                       created_at, updated_at, created_by
                FROM users WHERE email = %s AND status = 'active'
            """, (email.lower(),))

            master_user_data = master_cursor.fetchone()
            master_cursor.close()
            master_conn.close()

            if master_user_data:
                # Create User object from master database data
                user = User()
                for key, value in master_user_data.items():
                    setattr(user, key, value)
                # Mark this as a master database user for proper session handling
                user._is_master_user = True

        except Exception as e:
            current_app.logger.warning(f"Master database lookup failed: {e}")

        # If not found in master, try tenant database
        if not user:
            user = db.session.query(User).filter_by(email=email.lower()).first()
            if user:
                user._is_master_user = False

        if not user:
            # Log failed login attempt
            self._log_authentication_event('login_failed_no_user', email, session_info)
            raise Unauthorized('Invalid email or password')

        # Check if account is locked
        if user.is_locked():
            self._log_authentication_event('login_failed_locked', email, session_info, user.id)
            raise Unauthorized('Account is temporarily locked due to failed login attempts')

        # Check password
        if not user.check_password(password):
            if hasattr(user, '_is_master_user') and user._is_master_user:
                # Update failed login attempts in master database
                self._update_master_user_failed_login(user.id)
            else:
                user.increment_failed_login()
                db.session.commit()

            self._log_authentication_event('login_failed_password', email, session_info, user.id)
            raise Unauthorized('Invalid email or password')

        # Check account status
        if not user.is_active():
            self._log_authentication_event('login_failed_inactive', email, session_info, user.id)
            raise Unauthorized('Account is not active')

        # Reset failed login attempts on successful authentication
        if user.failed_login_attempts > 0:
            if hasattr(user, '_is_master_user') and user._is_master_user:
                # Reset failed login attempts in master database
                self._reset_master_user_failed_login(user.id)
            else:
                user.unlock_account()

        # Validate tenant access if specified
        if tenant_id and not user.has_permission('access', tenant_id):
            if user.role != 'platform_admin' and user.tenant_id != tenant_id:
                self._log_authentication_event('login_failed_tenant', email, session_info, user.id)
                raise Forbidden('Access denied to specified tenant')

        # Update login timestamp
        if hasattr(user, '_is_master_user') and user._is_master_user:
            # Update login timestamp in master database
            self._update_master_user_login(user.id)
        else:
            user.last_login = datetime.now(timezone.utc)
            user.update_last_activity()
            db.session.commit()

        # Generate tokens
        token_data = self.jwt_service.generate_tokens(user, tenant_id, session_info)

        # Log successful login
        self._log_authentication_event('login_success', email, session_info, user.id, tenant_id)

        return token_data, user

    def logout_user(self, token: str, session_info: Dict = None):
        """
        Logout user and revoke token

        Args:
            token: Access token to revoke
            session_info: Session metadata
        """
        try:
            payload = self.jwt_service.decode_token(token, verify_session=False)
            user_id = payload.get('user_id')

            # Revoke token
            self.jwt_service.revoke_token(token, 'user_logout')

            # Log logout
            self._log_authentication_event('logout', payload.get('email'), session_info, user_id)

        except Exception as e:
            # Log logout attempt even if token is invalid
            self._log_authentication_event('logout_failed', None, session_info, error=str(e))

    def refresh_user_token(self, refresh_token: str, session_info: Dict = None) -> Dict:
        """
        Refresh user access token

        Args:
            refresh_token: Valid refresh token
            session_info: Updated session metadata

        Returns:
            New token data
        """
        try:
            token_data = self.jwt_service.refresh_access_token(refresh_token, session_info)

            # Log token refresh
            payload = self.jwt_service.decode_token(refresh_token, verify_session=False)
            self._log_authentication_event(
                'token_refresh',
                payload.get('email'),
                session_info,
                payload.get('user_id')
            )

            return token_data

        except Exception as e:
            self._log_authentication_event('token_refresh_failed', None, session_info, error=str(e))
            raise

    def _log_authentication_event(self, action: str, email: str = None, session_info: Dict = None,
                                user_id: int = None, tenant_id: str = None, error: str = None):
        """Log authentication events for audit trail"""
        from src.core.app import db

        description = f"Authentication event: {action}"
        if email:
            description += f" for {email}"
        if error:
            description += f" - Error: {error}"

        severity = 'info'
        if 'failed' in action or error:
            severity = 'warning'
        if 'locked' in action:
            severity = 'error'

        log_entry = UserAuditLog(
            user_id=user_id,
            action=action,
            resource_type='authentication',
            tenant_id=tenant_id,
            description=description,
            ip_address=session_info.get('ip_address') if session_info else None,
            user_agent=session_info.get('user_agent') if session_info else None,
            severity=severity
        )

        db.session.add(log_entry)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    def _update_master_user_failed_login(self, user_id: int):
        """Update failed login attempts for master database user"""
        import mysql.connector

        master_db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '0000',
            'database': 'bischeduler_master',
            'charset': 'utf8mb4'
        }

        try:
            master_conn = mysql.connector.connect(**master_db_config)
            master_cursor = master_conn.cursor()

            # Increment failed login attempts and set lock if needed
            master_cursor.execute("""
                UPDATE users
                SET failed_login_attempts = failed_login_attempts + 1,
                    locked_until = CASE
                        WHEN failed_login_attempts >= 4 THEN DATE_ADD(NOW(), INTERVAL 30 MINUTE)
                        ELSE locked_until
                    END
                WHERE id = %s
            """, (user_id,))

            master_conn.commit()
            master_cursor.close()
            master_conn.close()

        except Exception as e:
            current_app.logger.error(f"Failed to update master user failed login: {e}")

    def _reset_master_user_failed_login(self, user_id: int):
        """Reset failed login attempts for master database user"""
        import mysql.connector

        master_db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '0000',
            'database': 'bischeduler_master',
            'charset': 'utf8mb4'
        }

        try:
            master_conn = mysql.connector.connect(**master_db_config)
            master_cursor = master_conn.cursor()

            master_cursor.execute("""
                UPDATE users
                SET failed_login_attempts = 0, locked_until = NULL
                WHERE id = %s
            """, (user_id,))

            master_conn.commit()
            master_cursor.close()
            master_conn.close()

        except Exception as e:
            current_app.logger.error(f"Failed to reset master user failed login: {e}")

    def _update_master_user_login(self, user_id: int):
        """Update login timestamp for master database user"""
        import mysql.connector

        master_db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '0000',
            'database': 'bischeduler_master',
            'charset': 'utf8mb4'
        }

        try:
            master_conn = mysql.connector.connect(**master_db_config)
            master_cursor = master_conn.cursor()

            master_cursor.execute("""
                UPDATE users
                SET last_login = NOW(), last_activity = NOW()
                WHERE id = %s
            """, (user_id,))

            master_conn.commit()
            master_cursor.close()
            master_conn.close()

        except Exception as e:
            current_app.logger.error(f"Failed to update master user login timestamp: {e}")