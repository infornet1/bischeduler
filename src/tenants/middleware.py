"""
BiScheduler Multi-Tenant Middleware
Automatic tenant resolution and context switching for Venezuelan K12 institutions
"""

import logging
from flask import request, g, abort, jsonify
from functools import wraps
from typing import Optional

from src.tenants.manager import TenantManager, tenant_context
from src.models.master import Tenant, TenantStatus


logger = logging.getLogger(__name__)


class MultiTenantMiddleware:
    """
    Flask middleware for automatic tenant resolution and isolation
    Supports multiple tenant identification methods for Venezuelan schools
    """

    def __init__(self, app=None, tenant_manager: Optional[TenantManager] = None):
        self.tenant_manager = tenant_manager
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """
        Resolve tenant before each request
        Supports multiple tenant identification methods:
        1. Subdomain (ueipab.bischeduler.com)
        2. Header (X-Tenant-ID)
        3. Query parameter (?tenant=ueipab)
        4. API path (/api/tenants/ueipab/...)
        """
        # Skip tenant resolution for certain endpoints
        if self._should_skip_tenant_resolution():
            return

        tenant = None
        tenant_identifier = None

        try:
            # Method 1: Subdomain-based tenant resolution
            if hasattr(request, 'host') and '.' in request.host:
                subdomain = request.host.split('.')[0]
                if subdomain not in ['www', 'api', 'admin']:
                    tenant_identifier = subdomain
                    tenant = self.tenant_manager.get_tenant_by_domain(request.host)

            # Method 2: X-Tenant-ID header
            if not tenant and 'X-Tenant-ID' in request.headers:
                tenant_identifier = request.headers['X-Tenant-ID']
                tenant = self.tenant_manager.get_tenant_by_id(tenant_identifier)

            # Method 3: Query parameter
            if not tenant and 'tenant' in request.args:
                tenant_identifier = request.args['tenant']
                tenant = self.tenant_manager.get_tenant_by_id(tenant_identifier)

            # Method 4: API path-based resolution
            if not tenant and request.path.startswith('/api/tenants/'):
                path_parts = request.path.split('/')
                if len(path_parts) >= 4:
                    tenant_identifier = path_parts[3]
                    tenant = self.tenant_manager.get_tenant_by_id(tenant_identifier)

            # Validate and set tenant context
            if tenant:
                if not self._validate_tenant_access(tenant):
                    abort(403, description="Tenant access denied")

                # Set tenant context for request
                tenant_context.set_tenant(tenant)
                g.current_tenant = tenant

                # Update last accessed timestamp
                self._update_tenant_last_accessed(tenant)

                logger.debug(f"Resolved tenant: {tenant.institution_name} ({tenant.tenant_id})")
            else:
                # No tenant resolved - this might be OK for public endpoints
                if self._requires_tenant():
                    abort(400, description="Tenant identification required")

        except Exception as e:
            logger.error(f"Tenant resolution failed: {str(e)}")
            abort(500, description="Tenant resolution error")

    def after_request(self, response):
        """Clean up tenant context after request"""
        tenant_context.clear_tenant()
        if hasattr(g, 'current_tenant'):
            delattr(g, 'current_tenant')
        return response

    def _should_skip_tenant_resolution(self) -> bool:
        """
        Determine if tenant resolution should be skipped
        Skip for health checks, documentation, admin endpoints
        """
        skip_paths = [
            '/health',
            '/info',
            '/docs',
            '/admin',
            '/api/admin',
            '/api/invitations/accept',  # Invitation acceptance before tenant exists
            '/static'
        ]

        return any(request.path.startswith(path) for path in skip_paths)

    def _requires_tenant(self) -> bool:
        """
        Determine if current endpoint requires tenant context
        Most API endpoints require tenant, but some are tenant-agnostic
        """
        # Endpoints that don't require tenant
        no_tenant_paths = [
            '/api/auth/login',
            '/api/platform/status',
            '/api/invitations'
        ]

        return not any(request.path.startswith(path) for path in no_tenant_paths)

    def _validate_tenant_access(self, tenant: Tenant) -> bool:
        """
        Validate that tenant can be accessed
        Check tenant status and subscription validity
        """
        # Check tenant is active
        if tenant.status != TenantStatus.ACTIVE:
            logger.warning(f"Access attempt to inactive tenant: {tenant.institution_name}")
            return False

        # Check subscription expiry (if applicable)
        if tenant.subscription_expires:
            from datetime import datetime, timezone
            if datetime.now(timezone.utc) > tenant.subscription_expires:
                logger.warning(f"Access attempt to expired tenant: {tenant.institution_name}")
                return False

        return True

    def _update_tenant_last_accessed(self, tenant: Tenant):
        """Update tenant's last accessed timestamp"""
        try:
            # TODO: Implement async update to avoid blocking request
            # For now, just log the access
            logger.debug(f"Tenant accessed: {tenant.institution_name}")
        except Exception as e:
            logger.error(f"Failed to update tenant last accessed: {str(e)}")


def require_tenant(f):
    """
    Decorator to require tenant context for endpoint
    Use on API endpoints that must have tenant context
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_tenant') or not g.current_tenant:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'This endpoint requires tenant identification'
            }), 400
        return f(*args, **kwargs)
    return decorated_function


def require_tenant_admin(f):
    """
    Decorator to require tenant admin privileges
    Use on endpoints that modify tenant configuration
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_tenant') or not g.current_tenant:
            return jsonify({
                'error': 'Tenant context required',
                'message': 'This endpoint requires tenant identification'
            }), 400

        # TODO: Check if current user has admin privileges for this tenant
        # For now, assume user with tenant context has admin rights
        return f(*args, **kwargs)
    return decorated_function


def get_current_tenant() -> Optional[Tenant]:
    """
    Helper function to get current tenant from context
    Returns None if no tenant context
    """
    return getattr(g, 'current_tenant', None)


def get_current_tenant_id() -> Optional[str]:
    """
    Helper function to get current tenant ID
    Returns None if no tenant context
    """
    tenant = get_current_tenant()
    return tenant.tenant_id if tenant else None


def get_current_schema_name() -> Optional[str]:
    """
    Helper function to get current tenant's database schema name
    Returns None if no tenant context
    """
    tenant = get_current_tenant()
    return tenant.schema_name if tenant else None