"""
BiScheduler Authentication Package
Multi-tenant authentication for Venezuelan K12 platform
"""

from .jwt_service import JWTService, AuthenticationService
from .decorators import (
    jwt_required, roles_required, permissions_required, tenant_required,
    school_admin_required, teacher_or_admin_required, platform_admin_required,
    active_user_required, audit_action, AuthenticationMiddleware
)
from .views import auth_bp

__all__ = [
    'JWTService',
    'AuthenticationService',
    'jwt_required',
    'roles_required',
    'permissions_required',
    'tenant_required',
    'school_admin_required',
    'teacher_or_admin_required',
    'platform_admin_required',
    'active_user_required',
    'audit_action',
    'AuthenticationMiddleware',
    'auth_bp'
]