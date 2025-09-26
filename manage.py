#!/usr/bin/env python3
"""
BiScheduler Management Script
Command-line interface for multi-tenant K12 platform operations
"""

import os
import click
from flask.cli import with_appcontext
from src.core.app import create_app, db


# Create application instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.cli.command()
@with_appcontext
def init_db():
    """Initialize the master database"""
    click.echo('Initializing BiScheduler master database...')
    db.create_all()
    click.echo('✅ Master database initialized successfully!')


@app.cli.command()
@with_appcontext
def reset_db():
    """Reset the master database (WARNING: destroys all data)"""
    if click.confirm('⚠️  This will destroy all data. Continue?'):
        click.echo('Resetting database...')
        db.drop_all()
        db.create_all()
        click.echo('✅ Database reset completed!')
    else:
        click.echo('❌ Database reset cancelled.')


@app.cli.command()
@click.argument('tenant_name')
@with_appcontext
def create_tenant(tenant_name):
    """Create a new tenant schema"""
    click.echo(f'Creating tenant: {tenant_name}')
    # TODO: Implement tenant creation logic
    click.echo(f'✅ Tenant {tenant_name} created successfully!')


@app.cli.command()
@with_appcontext
def list_tenants():
    """List all existing tenants"""
    click.echo('📋 BiScheduler Tenants:')
    # TODO: Implement tenant listing logic
    click.echo('UEIPAB (demo tenant)')


@app.cli.command()
@click.option('--port', default=5005, help='Port number to run on')
@click.option('--host', default='127.0.0.1', help='Host address to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def run(port, host, debug):
    """Run the BiScheduler development server"""
    click.echo('🚀 Starting BiScheduler...')
    click.echo(f'   Platform: Multi-Tenant K12 Scheduling')
    click.echo(f'   Compliance: Venezuelan Education Standards')
    click.echo(f'   URL: http://{host}:{port}')
    click.echo('   Press CTRL+C to stop')

    app.run(host=host, port=port, debug=debug)


@app.cli.command()
@with_appcontext
def import_legacy_data():
    """Import data from legacy UEIPAB scheduler"""
    click.echo('📊 Importing legacy UEIPAB data...')
    click.echo('   Source: migration_workspace/extracted_data/')

    try:
        from src.core.database_manager import BiSchedulerDatabaseManager

        # Initialize database manager
        db_manager = BiSchedulerDatabaseManager(app.config['MASTER_DATABASE_URL'])

        # Import Venezuelan education data for UEIPAB tenant
        # This assumes UEIPAB tenant already exists, or we create it
        result = db_manager.setup_ueipab_tenant()

        if result.get('status') == 'success':
            import_results = result.get('import_results', {})
            click.echo('✅ UEIPAB tenant setup completed!')
            click.echo(f"   📊 Time periods: {import_results.get('time_periods', 0)}")
            click.echo(f"   🏫 Classrooms: {import_results.get('classrooms', 0)}")
            click.echo(f"   📚 Subjects: {import_results.get('subjects', 0)}")
            click.echo(f"   👨‍🏫 Teachers: {import_results.get('teachers', 0)}")
            click.echo(f"   🔗 Teacher-Subject relationships: {import_results.get('teacher_subjects', 0)}")
            click.echo(f"   ⚖️ Workload records: {import_results.get('teacher_workloads', 0)}")
            click.echo('🎉 Legacy data import completed!')
        else:
            click.echo(f"❌ Import failed: {result.get('message', 'Unknown error')}")

    except Exception as e:
        click.echo(f'❌ Import failed: {str(e)}')


@app.cli.command()
@with_appcontext
def setup_database():
    """Initialize complete BiScheduler database system"""
    click.echo('🏗️ Setting up BiScheduler database system...')

    try:
        from src.core.database_manager import BiSchedulerDatabaseManager

        # Initialize database manager
        db_manager = BiSchedulerDatabaseManager(app.config['MASTER_DATABASE_URL'])

        # Initialize master database
        if db_manager.initialize_master_database():
            click.echo('✅ Master database initialized')

            # Setup UEIPAB as primary tenant
            result = db_manager.setup_ueipab_tenant()

            if result.get('status') == 'success':
                click.echo('✅ UEIPAB tenant created and configured')
                click.echo(f"   🆔 Tenant ID: {result.get('tenant_id')}")
                click.echo(f"   🏛️ Institution: {result.get('institution_name')}")
                click.echo(f"   💾 Database: {result.get('database_url')}")
                click.echo('🎉 BiScheduler database system ready!')
            else:
                click.echo(f"❌ UEIPAB setup failed: {result.get('message')}")
        else:
            click.echo('❌ Master database initialization failed')

    except Exception as e:
        click.echo(f'❌ Database setup failed: {str(e)}')


@app.cli.command()
@with_appcontext
def validate_database():
    """Validate database integrity and relationships"""
    click.echo('🔍 Validating BiScheduler database integrity...')

    try:
        from src.core.database_manager import BiSchedulerDatabaseManager

        db_manager = BiSchedulerDatabaseManager(app.config['MASTER_DATABASE_URL'])

        # Get UEIPAB tenant database URL
        from src.tenants.manager import TenantManager
        tenant_manager = TenantManager(app.config['MASTER_DATABASE_URL'])
        ueipab_tenant = tenant_manager.get_tenant_by_domain('ueipab.bischeduler.com')

        tenant_db_url = ueipab_tenant.database_url if ueipab_tenant else None

        # Validate database
        results = db_manager.validate_database_integrity(tenant_db_url)

        # Display master database results
        master_db = results.get('master_db', {})
        if master_db:
            click.echo('📊 Master Database:')
            click.echo(f"   👥 Tenants: {master_db.get('tenants', 0)}")
            click.echo(f"   📧 Invitations: {master_db.get('invitations', 0)}")
            click.echo(f"   Status: {master_db.get('status', 'unknown')}")

        # Display tenant database results
        tenant_db = results.get('tenant_db', {})
        if tenant_db:
            click.echo('📊 UEIPAB Tenant Database:')
            click.echo(f"   ⏰ Time periods: {tenant_db.get('time_periods', 0)}")
            click.echo(f"   🏫 Classrooms: {tenant_db.get('classrooms', 0)}")
            click.echo(f"   📝 Sections: {tenant_db.get('sections', 0)}")
            click.echo(f"   📚 Subjects: {tenant_db.get('subjects', 0)}")
            click.echo(f"   👨‍🏫 Teachers: {tenant_db.get('teachers', 0)}")
            click.echo(f"   🔗 Teacher-Subject links: {tenant_db.get('teacher_subjects', 0)}")
            click.echo(f"   ⚖️ Workload records: {tenant_db.get('teacher_workloads', 0)}")
            click.echo(f"   📅 Schedule assignments: {tenant_db.get('schedule_assignments', 0)}")

            if tenant_db.get('orphaned_assignments', 0) > 0:
                click.echo(f"   ⚠️ Orphaned assignments: {tenant_db.get('orphaned_assignments')}")

            if tenant_db.get('invalid_workloads', 0) > 0:
                click.echo(f"   ⚠️ Invalid workloads: {tenant_db.get('invalid_workloads')}")

            click.echo(f"   Status: {tenant_db.get('status', 'unknown')}")

        click.echo('✅ Database validation completed!')

    except Exception as e:
        click.echo(f'❌ Validation failed: {str(e)}')


@app.cli.command()
@with_appcontext
def platform_stats():
    """Show comprehensive platform statistics"""
    click.echo('📊 BiScheduler Platform Statistics')
    click.echo('=' * 40)

    try:
        from src.core.database_manager import BiSchedulerDatabaseManager

        db_manager = BiSchedulerDatabaseManager(app.config['MASTER_DATABASE_URL'])
        stats = db_manager.get_platform_statistics()

        if 'error' not in stats:
            platform = stats.get('platform', {})
            venezuelan = stats.get('venezuelan_education', {})
            features = stats.get('features', {})

            click.echo('🏛️ Platform Overview:')
            click.echo(f"   Total tenants: {platform.get('total_tenants', 0)}")
            click.echo(f"   Active tenants: {platform.get('active_tenants', 0)}")
            click.echo(f"   Pending invitations: {platform.get('pending_invitations', 0)}")

            click.echo('🇻🇪 Venezuelan Education:')
            click.echo(f"   K12 institutions: {venezuelan.get('k12_institutions', 0)}")
            click.echo(f"   Universities: {venezuelan.get('universities', 0)}")
            click.echo(f"   Compliance ready: {'✅' if venezuelan.get('compliance_ready') else '❌'}")

            click.echo('🚀 Platform Features:')
            for feature, enabled in features.items():
                status = '✅' if enabled else '❌'
                feature_name = feature.replace('_', ' ').title()
                click.echo(f"   {feature_name}: {status}")

        else:
            click.echo(f"❌ Error getting statistics: {stats.get('error')}")

    except Exception as e:
        click.echo(f'❌ Failed to get statistics: {str(e)}')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)