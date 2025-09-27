"""
BiScheduler Master Database Models
Tenant management and central coordination for multi-K12 platform
Enhanced with authentication system integration
"""

from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.mysql import CHAR
import uuid

# Use Flask-SQLAlchemy db instance for proper integration
from src.core.app import db


class TenantStatus(Enum):
    """Tenant lifecycle status"""
    PENDING = "pending"           # Invitation sent, not yet activated
    ACTIVE = "active"             # Fully operational
    SUSPENDED = "suspended"       # Temporarily disabled
    DEACTIVATED = "deactivated"   # Permanently disabled


class InstitutionType(Enum):
    """Venezuelan education institution types"""
    UNIVERSIDAD = "universidad"           # Higher education (like UEIPAB)
    COLEGIO_PUBLICO = "colegio_publico"  # Public K12 school
    COLEGIO_PRIVADO = "colegio_privado"  # Private K12 school
    INSTITUTO = "instituto"               # Technical institute
    ESCUELA_BASICA = "escuela_basica"    # Elementary school
    PREESCOLAR = "preescolar"            # Preschool


class Tenant(db.Model):
    """
    Master tenant registry for multi-K12 institutions
    Each tenant gets isolated schema for complete data privacy
    """
    __tablename__ = 'tenants'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(CHAR(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Institution identification
    institution_name = Column(String(255), nullable=False)
    institution_code = Column(String(50), unique=True, nullable=False)  # Official government code
    institution_type = Column(SQLEnum(InstitutionType), nullable=False)

    # Database schema information
    schema_name = Column(String(100), unique=True, nullable=False)
    database_url = Column(Text, nullable=False)  # Tenant-specific database connection

    # Contact and administrative
    admin_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20))
    institution_address = Column(Text)
    website_url = Column(String(255))

    # Venezuelan compliance
    matricula_code = Column(String(20))  # Official Matrícula reporting code
    state_region = Column(String(100))   # Venezuelan state/region
    municipality = Column(String(100))   # Venezuelan municipality
    rif_number = Column(String(20))      # Venezuelan tax identification

    # Platform configuration
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.PENDING, nullable=False)
    max_students = Column(Integer, default=1000)  # Licensing limit
    max_teachers = Column(Integer, default=100)   # Licensing limit
    custom_branding = Column(Boolean, default=False)  # Enable custom logos/colors

    # Logo/branding fields (Phase 1.8 Enhancement)
    logo_filename = Column(String(255))  # Stored logo filename
    logo_original_name = Column(String(255))  # Original uploaded filename
    logo_file_size = Column(Integer)  # File size in bytes
    logo_mime_type = Column(String(100))  # MIME type for validation
    logo_uploaded_at = Column(DateTime)  # When logo was uploaded
    logo_uploaded_by = Column(String(255))  # Admin who uploaded

    # Timestamps
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    activated_at = Column(DateTime)
    last_accessed = Column(DateTime)
    subscription_expires = Column(DateTime)

    # Metadata
    configuration_json = Column(Text)  # Tenant-specific settings as JSON
    notes = Column(Text)              # Administrative notes

    def __repr__(self):
        return f'<Tenant {self.institution_name} ({self.tenant_id})>'

    @property
    def is_active(self):
        """Check if tenant is currently active"""
        return self.status == TenantStatus.ACTIVE

    @property
    def is_venezuelan_k12(self):
        """Check if this is a Venezuelan K12 institution"""
        k12_types = {
            InstitutionType.COLEGIO_PUBLICO,
            InstitutionType.COLEGIO_PRIVADO,
            InstitutionType.ESCUELA_BASICA,
            InstitutionType.PREESCOLAR
        }
        return self.institution_type in k12_types

    @property
    def has_custom_logo(self):
        """Check if tenant has uploaded a custom logo"""
        return bool(self.logo_filename)

    @property
    def logo_url(self):
        """Get the URL for the tenant's logo"""
        if self.logo_filename:
            return f"/static/tenants/logos/{self.logo_filename}"
        return None

    @property
    def logo_path(self):
        """Get the filesystem path for the tenant's logo"""
        if self.logo_filename:
            return f"static/tenants/logos/{self.logo_filename}"
        return None


class TenantInvitation(db.Model):
    """
    Invitation system for new Venezuelan schools
    Enables UEIPAB to invite other institutions to join the platform
    """
    __tablename__ = 'tenant_invitations'

    id = Column(Integer, primary_key=True)
    invitation_code = Column(CHAR(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Institution being invited
    institution_name = Column(String(255), nullable=False)
    institution_type = Column(SQLEnum(InstitutionType), nullable=False)
    admin_email = Column(String(255), nullable=False)

    # Invitation details
    invited_by_tenant_id = Column(CHAR(36), nullable=False)  # Who sent the invitation (usually UEIPAB)
    invitation_message = Column(Text)
    status = Column(String(20), default='sent')  # sent, accepted, expired, cancelled

    # Timestamps
    sent_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime)
    responded_at = Column(DateTime)

    # Resulting tenant (when accepted)
    resulting_tenant_id = Column(CHAR(36))

    def __repr__(self):
        return f'<TenantInvitation {self.institution_name} ({self.status})>'

    @property
    def is_expired(self):
        """Check if invitation has expired"""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_pending(self):
        """Check if invitation is still pending response"""
        return self.status == 'sent' and not self.is_expired


class TenantUsageMetrics(db.Model):
    """
    Track usage metrics for licensing and billing
    Important for platform sustainability and growth monitoring
    """
    __tablename__ = 'tenant_usage_metrics'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(CHAR(36), nullable=False)

    # Usage period
    metric_date = Column(DateTime, nullable=False)
    metric_type = Column(String(50), nullable=False)  # daily, weekly, monthly

    # Core metrics
    active_students = Column(Integer, default=0)
    active_teachers = Column(Integer, default=0)
    total_schedules = Column(Integer, default=0)
    api_requests = Column(Integer, default=0)

    # Feature usage
    matricula_exports = Column(Integer, default=0)
    schedule_conflicts_resolved = Column(Integer, default=0)
    custom_reports_generated = Column(Integer, default=0)

    # Performance metrics
    avg_response_time_ms = Column(Integer)
    error_count = Column(Integer, default=0)
    uptime_percentage = Column(Integer, default=100)

    # Storage metrics
    database_size_mb = Column(Integer)
    file_storage_mb = Column(Integer)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<TenantUsageMetrics {self.tenant_id} {self.metric_date}>'