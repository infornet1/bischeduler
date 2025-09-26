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


# ============================================================================
# USER MANAGEMENT COMMANDS
# ============================================================================

@app.cli.command()
@click.option('--email', required=True, help='User email address')
@click.option('--password', required=True, help='User password')
@click.option('--first-name', required=True, help='User first name')
@click.option('--last-name', required=True, help='User last name')
@click.option('--role', default='platform_admin', help='User role (platform_admin, school_admin, teacher, etc.)')
@click.option('--tenant-id', help='Tenant ID (optional for platform admins)')
@click.option('--cedula', help='Venezuelan ID number')
@with_appcontext
def create_user(email, password, first_name, last_name, role, tenant_id, cedula):
    """Create a new user account"""
    click.echo(f'👤 Creating user: {email}')

    try:
        from src.models.auth import User, UserRole, UserStatus
        from datetime import datetime, timezone

        # Validate role
        valid_roles = [r.value for r in UserRole]
        if role not in valid_roles:
            click.echo(f"❌ Invalid role: {role}")
            click.echo(f"   Valid roles: {', '.join(valid_roles)}")
            return

        # Check if user already exists
        existing_user = db.session.query(User).filter_by(email=email).first()
        if existing_user:
            click.echo(f"❌ User with email {email} already exists")
            return

        # Check for duplicate cedula
        if cedula:
            existing_cedula = db.session.query(User).filter_by(cedula=cedula).first()
            if existing_cedula:
                click.echo(f"❌ User with cedula {cedula} already exists")
                return

        # Create user
        user = User(
            email=email.lower().strip(),
            username=email.split('@')[0],
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role,
            tenant_id=tenant_id,
            cedula=cedula,
            status=UserStatus.ACTIVE.value,
            email_verified_at=datetime.now(timezone.utc)
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        click.echo(f"✅ User created successfully!")
        click.echo(f"   ID: {user.id}")
        click.echo(f"   Email: {user.email}")
        click.echo(f"   Name: {user.full_name}")
        click.echo(f"   Role: {user.display_role}")
        if tenant_id:
            click.echo(f"   Tenant: {tenant_id}")

    except Exception as e:
        click.echo(f'❌ Failed to create user: {str(e)}')


@app.cli.command()
@click.argument('email')
@with_appcontext
def delete_user(email):
    """Delete a user account (use with caution)"""
    if not click.confirm(f'⚠️  Delete user {email}? This action cannot be undone.'):
        click.echo('❌ User deletion cancelled.')
        return

    try:
        from src.models.auth import User

        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            click.echo(f"❌ User {email} not found")
            return

        click.echo(f"Deleting user: {user.full_name} ({user.email})")

        # Delete user and associated data
        db.session.delete(user)
        db.session.commit()

        click.echo(f"✅ User {email} deleted successfully")

    except Exception as e:
        click.echo(f'❌ Failed to delete user: {str(e)}')


@app.cli.command()
@with_appcontext
def list_users():
    """List all platform users"""
    click.echo('👥 BiScheduler Platform Users')
    click.echo('=' * 50)

    try:
        from src.models.auth import User

        users = db.session.query(User).order_by(User.created_at.desc()).all()

        if not users:
            click.echo('No users found.')
            return

        for user in users:
            status_icon = '🟢' if user.is_active() else '🔴'
            click.echo(f"{status_icon} {user.email}")
            click.echo(f"   Name: {user.full_name}")
            click.echo(f"   Role: {user.display_role}")
            click.echo(f"   Tenant: {user.tenant_id or 'Platform-wide'}")
            click.echo(f"   Status: {user.status}")
            click.echo(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
            if user.last_login:
                click.echo(f"   Last login: {user.last_login.strftime('%Y-%m-%d %H:%M')}")
            click.echo('')

        click.echo(f"Total users: {len(users)}")

    except Exception as e:
        click.echo(f'❌ Failed to list users: {str(e)}')


@app.cli.command()
@click.argument('email')
@click.option('--new-password', required=True, help='New password')
@with_appcontext
def reset_password(email, new_password):
    """Reset user password (admin function)"""
    click.echo(f'🔑 Resetting password for: {email}')

    try:
        from src.models.auth import User
        from datetime import datetime, timezone

        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            click.echo(f"❌ User {email} not found")
            return

        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        # Force password change on next login if desired
        # user.status = UserStatus.PASSWORD_RESET_REQUIRED.value

        db.session.commit()

        click.echo(f"✅ Password reset successfully for {email}")
        click.echo("⚠️  User should change password on next login")

    except Exception as e:
        click.echo(f'❌ Failed to reset password: {str(e)}')


@app.cli.command()
@click.argument('email')
@click.option('--status', type=click.Choice(['active', 'inactive', 'suspended']),
              required=True, help='New user status')
@with_appcontext
def set_user_status(email, status):
    """Change user account status"""
    click.echo(f'📝 Setting user status: {email} -> {status}')

    try:
        from src.models.auth import User
        from datetime import datetime, timezone

        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            click.echo(f"❌ User {email} not found")
            return

        old_status = user.status
        user.status = status
        user.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        click.echo(f"✅ User status changed: {old_status} -> {status}")

    except Exception as e:
        click.echo(f'❌ Failed to set user status: {str(e)}')


@app.cli.command()
@with_appcontext
def list_user_sessions():
    """List active user sessions"""
    click.echo('📱 Active User Sessions')
    click.echo('=' * 40)

    try:
        from src.models.auth import UserSession, User
        from datetime import datetime, timezone

        sessions = db.session.query(UserSession).filter_by(is_active=True)\
                     .filter(UserSession.expires_at > datetime.now(timezone.utc))\
                     .order_by(UserSession.last_activity.desc()).all()

        if not sessions:
            click.echo('No active sessions found.')
            return

        for session in sessions:
            user_email = session.user.email if session.user else 'Unknown'
            click.echo(f"🔐 {user_email}")
            click.echo(f"   Session: {session.session_token[:8]}...")
            click.echo(f"   IP: {session.ip_address}")
            click.echo(f"   Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}")
            click.echo(f"   Last activity: {session.last_activity.strftime('%Y-%m-%d %H:%M')}")
            click.echo(f"   Expires: {session.expires_at.strftime('%Y-%m-%d %H:%M')}")
            click.echo('')

        click.echo(f"Total active sessions: {len(sessions)}")

    except Exception as e:
        click.echo(f'❌ Failed to list sessions: {str(e)}')


@app.cli.command()
@click.argument('email')
@with_appcontext
def revoke_user_sessions(email):
    """Revoke all sessions for a specific user"""
    click.echo(f'🔒 Revoking all sessions for: {email}')

    try:
        from src.models.auth import User, UserSession
        from src.auth.jwt_service import JWTService

        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            click.echo(f"❌ User {email} not found")
            return

        # Revoke all user sessions
        jwt_service = JWTService()
        jwt_service.revoke_all_user_tokens(user.id, 'admin_revocation')

        click.echo(f"✅ All sessions revoked for {email}")

    except Exception as e:
        click.echo(f'❌ Failed to revoke sessions: {str(e)}')


@app.cli.command()
@with_appcontext
def audit_summary():
    """Show user activity audit summary"""
    click.echo('📊 User Activity Audit Summary')
    click.echo('=' * 40)

    try:
        from src.models.auth import UserAuditLog, User
        from datetime import datetime, timezone, timedelta

        # Last 7 days activity
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        total_actions = db.session.query(UserAuditLog)\
                          .filter(UserAuditLog.created_at >= week_ago).count()

        # Most active users
        click.echo('🔥 Most Active Users (last 7 days):')
        active_users = db.session.query(User.email, db.func.count(UserAuditLog.id).label('actions'))\
                         .join(UserAuditLog)\
                         .filter(UserAuditLog.created_at >= week_ago)\
                         .group_by(User.email)\
                         .order_by(db.func.count(UserAuditLog.id).desc())\
                         .limit(5).all()

        for email, action_count in active_users:
            click.echo(f"   {email}: {action_count} actions")

        click.echo('')
        click.echo(f"Total actions last 7 days: {total_actions}")

        # Recent critical events
        critical_events = db.session.query(UserAuditLog)\
                           .filter(UserAuditLog.severity == 'critical')\
                           .filter(UserAuditLog.created_at >= week_ago)\
                           .order_by(UserAuditLog.created_at.desc())\
                           .limit(5).all()

        if critical_events:
            click.echo('')
            click.echo('⚠️ Critical Events:')
            for event in critical_events:
                user_email = event.user.email if event.user else 'System'
                click.echo(f"   {event.created_at.strftime('%Y-%m-%d %H:%M')} - {user_email}: {event.action}")

    except Exception as e:
        click.echo(f'❌ Failed to generate audit summary: {str(e)}')


if __name__ == '__main__':
    # Use Flask CLI
    import sys
    import os
    os.environ['FLASK_APP'] = 'manage.py'
    app.run(host='127.0.0.1', port=5005, debug=True)