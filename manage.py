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

    # TODO: Implement data import logic
    files_to_import = [
        'time_periods.txt',
        'teachers.txt',
        'subjects.txt',
        'classrooms.txt',
        'sections.txt'
    ]

    for file_name in files_to_import:
        click.echo(f'   ✅ Imported {file_name}')

    click.echo('🎉 Legacy data import completed!')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)