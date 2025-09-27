"""
BiScheduler Authentication Models
Multi-tenant user management for Venezuelan K12 platform
Enhanced with role-based access control
"""

from datetime import datetime, timezone, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import secrets

# Use Flask-SQLAlchemy db instance for proper integration
from src.core.app import db


class UserRole(Enum):
    """User roles for Venezuelan K12 education system"""
    PLATFORM_ADMIN = "platform_admin"      # BiScheduler platform management
    SCHOOL_ADMIN = "school_admin"           # School director/coordinator
    ACADEMIC_COORDINATOR = "academic_coordinator"  # Academic planning
    TEACHER = "teacher"                     # Teaching staff
    PARENT = "parent"                       # Student parent/guardian
    STUDENT = "student"                     # Student access (future)
    VIEWER = "viewer"                       # Read-only access


class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    PASSWORD_RESET_REQUIRED = "password_reset_required"


class User(db.Model):
    """
    Multi-tenant user model for Venezuelan K12 platform
    Handles authentication across all tenants with role-based access
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Personal information (Venezuelan context)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(155), nullable=False)
    cedula = Column(String(20), unique=True)  # Venezuelan ID number
    phone = Column(String(20))

    # Authentication settings
    role = Column(String(50), nullable=False)  # UserRole enum value
    status = Column(String(50), default=UserStatus.PENDING_VERIFICATION.value)

    # Security features
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime)
    email_verification_token = Column(String(255))
    email_verified_at = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)

    # Multi-tenant association
    tenant_id = Column(String(100))  # Associated tenant (can be null for platform admins)
    tenant_permissions = Column(JSON)  # Specific permissions within tenant

    # Session management
    last_login = Column(DateTime)
    last_activity = Column(DateTime)
    current_session_token = Column(String(255))

    # Platform preferences
    language = Column(String(10), default='es')  # Spanish default for Venezuela
    timezone = Column(String(50), default='America/Caracas')
    ui_preferences = Column(JSON)  # Theme, layout preferences

    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, ForeignKey('users.id'))

    # Relationships
    created_by_user = relationship("User", remote_side=[id])
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("UserAuditLog", back_populates="user")

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

    def set_password(self, password: str):
        """Set password hash with Venezuelan security standards"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def generate_password_reset_token(self) -> str:
        """Generate secure password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        return token

    def generate_email_verification_token(self) -> str:
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        return token

    def verify_email(self):
        """Mark email as verified"""
        self.email_verified_at = datetime.now(timezone.utc)
        self.email_verification_token = None
        if self.status == UserStatus.PENDING_VERIFICATION.value:
            self.status = UserStatus.ACTIVE.value

    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE.value

    def is_locked(self) -> bool:
        """Check if account is temporarily locked"""
        if self.locked_until:
            return datetime.now(timezone.utc) < self.locked_until
        return False

    def lock_account(self, duration_minutes: int = 30):
        """Temporarily lock account after failed login attempts"""
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)

    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0

    def increment_failed_login(self):
        """Increment failed login counter and lock if necessary"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()

    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now(timezone.utc)

    def has_permission(self, permission: str, tenant_id: str = None) -> bool:
        """Check if user has specific permission"""
        # Platform admins have all permissions
        if self.role == UserRole.PLATFORM_ADMIN.value:
            return True

        # Check tenant-specific permissions
        if tenant_id and self.tenant_id == tenant_id:
            if self.tenant_permissions:
                return permission in self.tenant_permissions

            # Default role permissions
            role_permissions = {
                UserRole.SCHOOL_ADMIN.value: [
                    'manage_schedules', 'manage_teachers', 'manage_students',
                    'manage_classrooms', 'view_reports', 'manage_users'
                ],
                UserRole.ACADEMIC_COORDINATOR.value: [
                    'manage_schedules', 'manage_teachers', 'manage_classrooms', 'view_reports'
                ],
                UserRole.TEACHER.value: [
                    'view_schedules', 'view_students', 'update_profile'
                ],
                UserRole.PARENT.value: [
                    'view_student_schedules', 'view_student_grades'
                ],
                UserRole.VIEWER.value: [
                    'view_schedules'
                ]
            }

            return permission in role_permissions.get(self.role, [])

        return False

    @property
    def full_name(self):
        """Get formatted full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_role(self):
        """Get user-friendly role name"""
        role_names = {
            UserRole.PLATFORM_ADMIN.value: "Administrador de Plataforma",
            UserRole.SCHOOL_ADMIN.value: "Director de Institución",
            UserRole.ACADEMIC_COORDINATOR.value: "Coordinador Académico",
            UserRole.TEACHER.value: "Docente",
            UserRole.PARENT.value: "Representante",
            UserRole.STUDENT.value: "Estudiante",
            UserRole.VIEWER.value: "Observador"
        }
        return role_names.get(self.role, self.role)


class UserSession(db.Model):
    """
    User session tracking for security and audit
    Supports Venezuelan security requirements
    """
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    jwt_token_hash = Column(String(255))  # Hashed JWT for revocation

    # Session details
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    device_info = Column(JSON)
    location_info = Column(JSON)  # Country, city if available

    # Session lifecycle
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime)
    revoked_reason = Column(String(100))  # logout, timeout, security, admin

    # Security flags
    is_active = Column(Boolean, default=True)
    is_suspicious = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="user_sessions")

    def __repr__(self):
        return f'<UserSession {self.user.email} - {self.session_token[:8]}...>'

    def is_valid(self) -> bool:
        """Check if session is still valid"""
        if self.revoked_at or not self.is_active:
            return False
        return datetime.now(timezone.utc) < self.expires_at

    def revoke(self, reason: str = "logout"):
        """Revoke session"""
        self.revoked_at = datetime.now(timezone.utc)
        self.revoked_reason = reason
        self.is_active = False

    def extend_session(self, hours: int = 8):
        """Extend session expiration"""
        if self.is_valid():
            self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
            self.last_activity = datetime.now(timezone.utc)

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now(timezone.utc)


class UserAuditLog(db.Model):
    """
    Comprehensive audit logging for Venezuelan compliance
    Tracks all user actions for security and regulatory requirements
    """
    __tablename__ = 'user_audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Action details
    action = Column(String(100), nullable=False)  # login, logout, create_schedule, etc.
    resource_type = Column(String(50))  # schedule, teacher, student, etc.
    resource_id = Column(String(100))  # ID of affected resource
    tenant_id = Column(String(100))  # Tenant context

    # Event details
    description = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(255))

    # Data changes (for detailed auditing)
    old_values = Column(JSON)  # Previous values
    new_values = Column(JSON)  # New values

    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    severity = Column(String(20), default='info')  # info, warning, error, critical

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f'<UserAuditLog {self.user.email if self.user else "system"} - {self.action}>'

    @classmethod
    def log_action(cls, session, user_id: int, action: str, **kwargs):
        """Create audit log entry"""
        log_entry = cls(
            user_id=user_id,
            action=action,
            resource_type=kwargs.get('resource_type'),
            resource_id=kwargs.get('resource_id'),
            tenant_id=kwargs.get('tenant_id'),
            description=kwargs.get('description'),
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            session_id=kwargs.get('session_id'),
            old_values=kwargs.get('old_values'),
            new_values=kwargs.get('new_values'),
            severity=kwargs.get('severity', 'info')
        )
        session.add(log_entry)
        return log_entry


# TenantInvitation is defined in src.models.master to avoid circular imports