"""
BiScheduler Tenant Manager
Core multi-tenant functionality for Venezuelan K12 institutions
"""

import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.models.master import Tenant, TenantInvitation, TenantStatus, InstitutionType
from src.core.app import db


logger = logging.getLogger(__name__)


class TenantManager:
    """
    Manages tenant lifecycle and schema operations
    Implements schema-per-tenant isolation for complete data privacy
    """

    def __init__(self, master_db_url: str):
        self.master_db_url = master_db_url
        self.engine = create_engine(master_db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tenant(
        self,
        institution_name: str,
        institution_code: str,
        institution_type: InstitutionType,
        admin_email: str,
        **kwargs
    ) -> Tenant:
        """
        Create a new tenant with isolated database schema

        Args:
            institution_name: Official institution name
            institution_code: Government institution code
            institution_type: Type of Venezuelan educational institution
            admin_email: Administrative contact email
            **kwargs: Additional tenant configuration

        Returns:
            Tenant: Created tenant instance

        Raises:
            ValueError: If tenant parameters are invalid
            SQLAlchemyError: If database operations fail
        """
        session = self.SessionLocal()
        try:
            # Generate unique identifiers
            tenant_id = str(uuid.uuid4())
            schema_name = f"tenant_{institution_code.lower().replace('-', '_')}"

            # Create tenant record
            tenant = Tenant(
                tenant_id=tenant_id,
                institution_name=institution_name,
                institution_code=institution_code,
                institution_type=institution_type,
                schema_name=schema_name,
                database_url=self._build_tenant_db_url(schema_name),
                admin_email=admin_email,
                status=TenantStatus.PENDING,
                **kwargs
            )

            session.add(tenant)
            session.commit()

            # Create isolated database schema
            self._create_tenant_schema(schema_name)

            # Initialize tenant database with base tables
            self._initialize_tenant_database(tenant)

            logger.info(f"Created tenant: {institution_name} ({tenant_id})")
            return tenant

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create tenant {institution_name}: {str(e)}")
            raise
        finally:
            session.close()

    def activate_tenant(self, tenant_id: str) -> bool:
        """
        Activate a pending tenant

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            bool: True if activation successful
        """
        session = self.SessionLocal()
        try:
            tenant = session.query(Tenant).filter_by(tenant_id=tenant_id).first()
            if not tenant:
                raise ValueError(f"Tenant {tenant_id} not found")

            if tenant.status != TenantStatus.PENDING:
                raise ValueError(f"Tenant {tenant_id} is not in pending status")

            tenant.status = TenantStatus.ACTIVE
            tenant.activated_at = datetime.now(timezone.utc)
            session.commit()

            logger.info(f"Activated tenant: {tenant.institution_name} ({tenant_id})")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to activate tenant {tenant_id}: {str(e)}")
            return False
        finally:
            session.close()

    def send_invitation(
        self,
        institution_name: str,
        institution_type: InstitutionType,
        admin_email: str,
        invited_by_tenant_id: str,
        message: Optional[str] = None
    ) -> TenantInvitation:
        """
        Send invitation to Venezuelan school to join platform

        Args:
            institution_name: Name of institution to invite
            institution_type: Type of Venezuelan educational institution
            admin_email: Administrative contact email
            invited_by_tenant_id: Tenant ID sending invitation (usually UEIPAB)
            message: Optional custom invitation message

        Returns:
            TenantInvitation: Created invitation instance
        """
        session = self.SessionLocal()
        try:
            invitation = TenantInvitation(
                institution_name=institution_name,
                institution_type=institution_type,
                admin_email=admin_email,
                invited_by_tenant_id=invited_by_tenant_id,
                invitation_message=message,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30)
            )

            session.add(invitation)
            session.commit()

            # TODO: Send email invitation
            self._send_invitation_email(invitation)

            logger.info(f"Sent invitation to {institution_name} ({admin_email})")
            return invitation

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to send invitation to {institution_name}: {str(e)}")
            raise
        finally:
            session.close()

    def accept_invitation(self, invitation_code: str, additional_data: Dict[str, Any]) -> Tenant:
        """
        Accept tenant invitation and create tenant

        Args:
            invitation_code: Unique invitation code
            additional_data: Additional tenant setup data

        Returns:
            Tenant: Created tenant from accepted invitation
        """
        session = self.SessionLocal()
        try:
            invitation = session.query(TenantInvitation).filter_by(
                invitation_code=invitation_code
            ).first()

            if not invitation:
                raise ValueError("Invalid invitation code")

            if invitation.is_expired:
                raise ValueError("Invitation has expired")

            if invitation.status != 'sent':
                raise ValueError("Invitation already processed")

            # Create tenant from invitation
            tenant = self.create_tenant(
                institution_name=invitation.institution_name,
                institution_code=additional_data.get('institution_code'),
                institution_type=invitation.institution_type,
                admin_email=invitation.admin_email,
                **additional_data
            )

            # Update invitation status
            invitation.status = 'accepted'
            invitation.accepted_at = datetime.now(timezone.utc)
            invitation.resulting_tenant_id = tenant.tenant_id

            session.commit()

            logger.info(f"Accepted invitation: {tenant.institution_name}")
            return tenant

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to accept invitation {invitation_code}: {str(e)}")
            raise
        finally:
            session.close()

    def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        session = self.SessionLocal()
        try:
            return session.query(Tenant).filter_by(tenant_id=tenant_id).first()
        finally:
            session.close()

    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain/subdomain"""
        # Extract tenant identifier from domain
        # e.g., ueipab.bischeduler.com -> ueipab
        tenant_code = domain.split('.')[0]

        session = self.SessionLocal()
        try:
            return session.query(Tenant).filter_by(institution_code=tenant_code).first()
        finally:
            session.close()

    def list_active_tenants(self) -> List[Tenant]:
        """List all active tenants"""
        session = self.SessionLocal()
        try:
            return session.query(Tenant).filter_by(status=TenantStatus.ACTIVE).all()
        finally:
            session.close()

    def _create_tenant_schema(self, schema_name: str):
        """Create isolated database schema for tenant"""
        with self.engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            conn.commit()
            logger.info(f"Created database schema: {schema_name}")

    def _initialize_tenant_database(self, tenant: Tenant):
        """Initialize tenant database with base tables and Venezuelan data"""
        # TODO: Implement tenant schema initialization
        # This will include:
        # - Creating all tenant-specific tables
        # - Importing Venezuelan curriculum data
        # - Setting up default time periods
        # - Configuring Venezuelan compliance settings
        logger.info(f"Initialized database for tenant: {tenant.institution_name}")

    def _build_tenant_db_url(self, schema_name: str) -> str:
        """Build database URL for tenant schema"""
        # For now, use same database with different schema
        # In production, could be separate databases
        base_url = self.master_db_url.replace('/bischeduler_master', f'/{schema_name}')
        return base_url

    def _send_invitation_email(self, invitation: TenantInvitation):
        """Send invitation email to institution"""
        # TODO: Implement email sending
        # Template should include:
        # - BiScheduler platform benefits
        # - Venezuelan education compliance features
        # - Multi-tenant security assurance
        # - Invitation acceptance link
        logger.info(f"Email sent to {invitation.admin_email} (invitation: {invitation.invitation_code})")


class TenantContext:
    """
    Thread-local tenant context for request processing
    Ensures all database operations target correct tenant schema
    """

    def __init__(self):
        self._tenant = None

    def set_tenant(self, tenant: Tenant):
        """Set current tenant for request context"""
        self._tenant = tenant
        # TODO: Switch database schema/connection
        logger.debug(f"Set tenant context: {tenant.institution_name}")

    def get_tenant(self) -> Optional[Tenant]:
        """Get current tenant from context"""
        return self._tenant

    def clear_tenant(self):
        """Clear tenant context"""
        self._tenant = None

    @property
    def tenant_id(self) -> Optional[str]:
        """Get current tenant ID"""
        return self._tenant.tenant_id if self._tenant else None

    @property
    def schema_name(self) -> Optional[str]:
        """Get current tenant schema name"""
        return self._tenant.schema_name if self._tenant else None


# Global tenant context instance
tenant_context = TenantContext()