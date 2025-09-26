"""
BiScheduler Database Manager
Enhanced database operations for multi-tenant Venezuelan K12 platform
"""

import logging
from typing import Dict, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.models.master import Base as MasterBase
from src.models.tenant import Base as TenantBase
from src.core.data_importer import VenezuelanDataImporter

logger = logging.getLogger(__name__)


class BiSchedulerDatabaseManager:
    """
    Comprehensive database management for BiScheduler platform
    Handles both master database and tenant-specific databases
    """

    def __init__(self, master_db_url: str):
        self.master_db_url = master_db_url
        self.master_engine = create_engine(master_db_url)
        self.MasterSession = sessionmaker(bind=self.master_engine)

    def initialize_master_database(self) -> bool:
        """
        Initialize master database with all tenant management tables
        """
        try:
            logger.info("Initializing BiScheduler master database...")
            MasterBase.metadata.create_all(bind=self.master_engine)
            logger.info("✅ Master database initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize master database: {str(e)}")
            return False

    def create_tenant_database(self, tenant_id: str, institution_code: str) -> str:
        """
        Create tenant-specific database with Venezuelan K12 schema

        Args:
            tenant_id: Unique tenant identifier
            institution_code: Institution code (e.g., 'UEIPAB')

        Returns:
            Database URL for the new tenant database
        """
        try:
            # Generate tenant database name
            db_name = f"bischeduler_{institution_code.lower()}"

            logger.info(f"Creating tenant database: {db_name}")

            # Create database
            with self.master_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
                conn.commit()

            # Generate tenant database URL
            base_url = self.master_db_url.rsplit('/', 1)[0]  # Remove database name
            tenant_db_url = f"{base_url}/{db_name}"

            # Initialize tenant schema
            tenant_engine = create_engine(tenant_db_url)
            TenantBase.metadata.create_all(bind=tenant_engine)

            logger.info(f"✅ Tenant database created: {db_name}")
            return tenant_db_url

        except Exception as e:
            logger.error(f"❌ Failed to create tenant database: {str(e)}")
            raise

    def import_venezuelan_data_to_tenant(
        self,
        tenant_db_url: str,
        academic_year: str = "2025-2026"
    ) -> Dict[str, int]:
        """
        Import Venezuelan education data to tenant database

        Args:
            tenant_db_url: Tenant database URL
            academic_year: Academic year for the data

        Returns:
            Dictionary with import results
        """
        try:
            logger.info(f"Importing Venezuelan education data for {academic_year}")

            # Create data importer
            importer = VenezuelanDataImporter(tenant_db_url, academic_year)

            # Import complete dataset
            migration_data_path = "/var/www/dev/bischeduler/migration_workspace/extracted_data"
            results = importer.import_complete_dataset(migration_data_path)

            logger.info("✅ Venezuelan education data imported successfully")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to import Venezuelan data: {str(e)}")
            return {"error": str(e)}

    def setup_ueipab_tenant(self) -> Dict[str, any]:
        """
        Set up UEIPAB as the primary tenant with complete data
        This creates the demo/primary tenant for the platform
        """
        try:
            logger.info("Setting up UEIPAB as primary tenant...")

            # Import tenant manager
            from src.tenants.manager import TenantManager
            from src.models.master import InstitutionType

            tenant_manager = TenantManager(self.master_db_url)

            # Create UEIPAB tenant
            ueipab_tenant = tenant_manager.create_tenant(
                institution_name="Universidad Experimental de las Fuerzas Armadas Nacional Bolivariana",
                institution_code="UEIPAB",
                institution_type=InstitutionType.UNIVERSIDAD,
                admin_email="admin@ueipab.edu.ve",
                contact_phone="+58-212-1234567",
                website_url="https://ueipab.edu.ve",
                state_region="Distrito Capital",
                municipality="Caracas",
                rif_number="G-20000000-0",
                max_students=1000,
                max_teachers=100,
                custom_branding=True
            )

            # Activate UEIPAB tenant
            tenant_manager.activate_tenant(ueipab_tenant.tenant_id)

            # Import Venezuelan education data
            import_results = self.import_venezuelan_data_to_tenant(
                ueipab_tenant.database_url,
                "2025-2026"
            )

            logger.info("✅ UEIPAB tenant setup completed successfully")

            return {
                'tenant_id': ueipab_tenant.tenant_id,
                'institution_name': ueipab_tenant.institution_name,
                'database_url': ueipab_tenant.database_url,
                'import_results': import_results,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"❌ Failed to setup UEIPAB tenant: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def validate_database_integrity(self, tenant_db_url: Optional[str] = None) -> Dict[str, any]:
        """
        Validate database integrity and relationships

        Args:
            tenant_db_url: Optional tenant database URL to validate

        Returns:
            Validation results
        """
        results = {'master_db': {}, 'tenant_db': {}}

        try:
            # Validate master database
            logger.info("Validating master database integrity...")

            session = self.MasterSession()
            try:
                from src.models.master import Tenant, TenantInvitation

                # Check master tables
                tenant_count = session.query(Tenant).count()
                invitation_count = session.query(TenantInvitation).count()

                results['master_db'] = {
                    'tenants': tenant_count,
                    'invitations': invitation_count,
                    'status': 'valid'
                }

            finally:
                session.close()

            # Validate tenant database if provided
            if tenant_db_url:
                logger.info("Validating tenant database integrity...")

                tenant_engine = create_engine(tenant_db_url)
                TenantSession = sessionmaker(bind=tenant_engine)
                session = TenantSession()

                try:
                    from src.models.tenant import (
                        TimePeriod, Classroom, Section, Subject, Teacher,
                        TeacherSubject, TeacherWorkload, ScheduleAssignment
                    )

                    # Check tenant tables
                    counts = {
                        'time_periods': session.query(TimePeriod).count(),
                        'classrooms': session.query(Classroom).count(),
                        'sections': session.query(Section).count(),
                        'subjects': session.query(Subject).count(),
                        'teachers': session.query(Teacher).count(),
                        'teacher_subjects': session.query(TeacherSubject).count(),
                        'teacher_workloads': session.query(TeacherWorkload).count(),
                        'schedule_assignments': session.query(ScheduleAssignment).count()
                    }

                    # Validate relationships
                    orphaned_assignments = session.query(ScheduleAssignment).filter(
                        ScheduleAssignment.teacher_id.is_(None)
                    ).count()

                    invalid_workloads = session.query(TeacherWorkload).filter(
                        TeacherWorkload.is_valid == False
                    ).count()

                    results['tenant_db'] = {
                        **counts,
                        'orphaned_assignments': orphaned_assignments,
                        'invalid_workloads': invalid_workloads,
                        'status': 'valid' if orphaned_assignments == 0 else 'warnings'
                    }

                finally:
                    session.close()

            logger.info("✅ Database integrity validation completed")
            return results

        except Exception as e:
            logger.error(f"❌ Database validation failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def get_platform_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive platform statistics
        """
        try:
            session = self.MasterSession()

            try:
                from src.models.master import Tenant, TenantInvitation

                # Master database stats
                total_tenants = session.query(Tenant).count()
                active_tenants = session.query(Tenant).filter_by(status='active').count()
                pending_invitations = session.query(TenantInvitation).filter_by(status='sent').count()

                # Get Venezuelan K12 specific stats
                k12_tenants = session.query(Tenant).filter(
                    Tenant.institution_type.in_(['colegio_publico', 'colegio_privado', 'escuela_basica', 'preescolar'])
                ).count()

                universities = session.query(Tenant).filter_by(institution_type='universidad').count()

                statistics = {
                    'platform': {
                        'total_tenants': total_tenants,
                        'active_tenants': active_tenants,
                        'pending_invitations': pending_invitations
                    },
                    'venezuelan_education': {
                        'k12_institutions': k12_tenants,
                        'universities': universities,
                        'compliance_ready': True
                    },
                    'features': {
                        'multi_tenant_logos': True,
                        'schema_per_tenant': True,
                        'venezuelan_curriculum': True,
                        'bimodal_schedules': True,
                        'workload_validation': True
                    },
                    'generated_at': logger.info
                }

                return statistics

            finally:
                session.close()

        except Exception as e:
            logger.error(f"Failed to get platform statistics: {str(e)}")
            return {'error': str(e)}

    def cleanup_orphaned_data(self, tenant_db_url: str) -> Dict[str, int]:
        """
        Clean up orphaned data in tenant database
        """
        try:
            tenant_engine = create_engine(tenant_db_url)
            TenantSession = sessionmaker(bind=tenant_engine)
            session = TenantSession()

            cleanup_results = {}

            try:
                from src.models.tenant import ScheduleAssignment, TeacherSubject

                # Remove schedule assignments with missing references
                orphaned_assignments = session.query(ScheduleAssignment).filter(
                    ScheduleAssignment.teacher_id.is_(None)
                ).delete()

                # Remove teacher-subject relationships for inactive records
                inactive_relationships = session.query(TeacherSubject).filter(
                    TeacherSubject.is_active == False
                ).delete()

                session.commit()

                cleanup_results = {
                    'orphaned_assignments': orphaned_assignments,
                    'inactive_relationships': inactive_relationships
                }

                logger.info(f"✅ Cleanup completed: {cleanup_results}")
                return cleanup_results

            finally:
                session.close()

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")
            return {'error': str(e)}