"""
BiScheduler Branding Configuration
Professional visual identity for Venezuelan K12 institutions
"""

from typing import Dict, Any, Optional
from flask import current_app
from src.tenants.middleware import get_current_tenant


class BrandingManager:
    """
    Manages branding and visual identity for multi-tenant platform
    Supports custom branding per Venezuelan institution
    """

    # Default BiScheduler brand colors
    DEFAULT_COLORS = {
        'primary': '#1e3a5f',      # Deep Navy
        'secondary': '#2563eb',     # Bridge Blue
        'accent': '#f59e0b',       # Academic Gold
        'background': '#ffffff',    # Clean White
        'surface': '#f3f4f6',      # Soft Gray
        'success': '#10b981',      # Success Green
        'warning': '#f59e0b',      # Warning Orange
        'error': '#ef4444',        # Alert Red
        'text_primary': '#1e3a5f',
        'text_secondary': '#6b7280'
    }

    # Default typography
    DEFAULT_TYPOGRAPHY = {
        'font_family': 'Inter, Arial, sans-serif',
        'header_weight': 'bold',
        'body_weight': 'normal',
        'ui_weight': 'medium'
    }

    # Platform branding assets
    PLATFORM_ASSETS = {
        'logo_full': '/static/branding/logo_concept.svg',
        'logo_icon': '/static/branding/favicon.svg',
        'favicon': '/static/branding/favicon.svg'
    }

    def get_tenant_branding(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get branding configuration for tenant

        Args:
            tenant_id: Optional tenant ID, uses current tenant if None

        Returns:
            Dict containing branding configuration
        """
        tenant = get_current_tenant() if not tenant_id else None
        # TODO: Fetch tenant from database if tenant_id provided

        # Check if tenant has custom branding enabled
        if tenant and getattr(tenant, 'custom_branding', False):
            return self._get_custom_tenant_branding(tenant)

        # Return default BiScheduler branding
        return self._get_default_branding(tenant)

    def _get_default_branding(self, tenant=None) -> Dict[str, Any]:
        """Get default BiScheduler branding"""
        institution_name = tenant.institution_name if tenant else "BiScheduler"

        return {
            'platform_name': 'BiScheduler',
            'institution_name': institution_name,
            'tagline': 'Multi-Tenant K12 Scheduling for Venezuelan Education',
            'colors': self.DEFAULT_COLORS.copy(),
            'typography': self.DEFAULT_TYPOGRAPHY.copy(),
            'assets': self.PLATFORM_ASSETS.copy(),
            'is_custom': False,
            'venezuelan_compliance': True,
            'bimodal_schedule_support': True
        }

    def _get_custom_tenant_branding(self, tenant) -> Dict[str, Any]:
        """
        Get custom branding for tenant with custom branding enabled
        Maintains BiScheduler foundation with institution customization
        """
        # TODO: Implement custom branding logic
        # This would load tenant-specific:
        # - Custom colors (while maintaining accessibility)
        # - Institution logo alongside BiScheduler logo
        # - Custom taglines and messaging
        # - Venezuelan compliance indicators

        base_branding = self._get_default_branding(tenant)

        # Example customization for UEIPAB
        if tenant.institution_code == 'UEIPAB':
            base_branding.update({
                'institution_logo': '/static/tenants/ueipab/logo.png',
                'colors': {
                    **base_branding['colors'],
                    'accent': '#c49b61',  # UEIPAB gold
                    'primary': '#1a365d'  # Darker navy for UEIPAB
                },
                'tagline': 'Powered by UEIPAB - Venezuelan Military University Excellence',
                'is_custom': True
            })

        return base_branding

    def generate_css_variables(self, tenant_id: Optional[str] = None) -> str:
        """
        Generate CSS custom properties for tenant branding

        Args:
            tenant_id: Optional tenant ID

        Returns:
            CSS string with custom properties
        """
        branding = self.get_tenant_branding(tenant_id)
        colors = branding['colors']
        typography = branding['typography']

        css_vars = [
            ":root {",
            f"  --bs-primary: {colors['primary']};",
            f"  --bs-secondary: {colors['secondary']};",
            f"  --bs-accent: {colors['accent']};",
            f"  --bs-background: {colors['background']};",
            f"  --bs-surface: {colors['surface']};",
            f"  --bs-success: {colors['success']};",
            f"  --bs-warning: {colors['warning']};",
            f"  --bs-error: {colors['error']};",
            f"  --bs-text-primary: {colors['text_primary']};",
            f"  --bs-text-secondary: {colors['text_secondary']};",
            f"  --bs-font-family: {typography['font_family']};",
            f"  --bs-header-weight: {typography['header_weight']};",
            f"  --bs-body-weight: {typography['body_weight']};",
            f"  --bs-ui-weight: {typography['ui_weight']};",
            "}"
        ]

        return "\n".join(css_vars)

    def get_platform_metadata(self) -> Dict[str, Any]:
        """Get platform-wide metadata for branding"""
        return {
            'platform': 'BiScheduler',
            'version': '1.0.0',
            'description': 'Multi-Tenant K12 Scheduling Platform',
            'target_market': 'Venezuelan Educational Institutions',
            'compliance': ['Matrícula Reporting', 'Government Standards'],
            'architecture': 'Schema-per-tenant Multi-tenancy',
            'developer': 'UEIPAB Technology Initiative',
            'license': 'Proprietary',
            'support_email': 'support@bischeduler.ueipab.edu.ve'
        }


# Global branding manager instance
branding_manager = BrandingManager()


def get_branding_for_request() -> Dict[str, Any]:
    """
    Convenience function to get branding for current request
    Automatically uses current tenant context
    """
    return branding_manager.get_tenant_branding()


def inject_branding_context():
    """
    Flask context processor to inject branding into templates
    Use this to make branding available in all templates
    """
    return {
        'branding': get_branding_for_request(),
        'platform_meta': branding_manager.get_platform_metadata()
    }