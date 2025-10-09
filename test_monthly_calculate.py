"""
Test script to debug the monthly calculate endpoint
"""
import sys
import traceback
from datetime import date

# Add the project root to the path
sys.path.insert(0, 'c:/Users/Pc/Desktop/Ueipab/Bischeduler/bischeduler')

from src.core.app import create_app
from src.attendance.services import MonthlyReportService
from src.models.tenant import db

app = create_app()

with app.app_context():
    try:
        # Set up tenant context
        from flask import g
        from src.models.master import Tenant
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        master_engine = create_engine('mysql+pymysql://root:0000@localhost/bischeduler_master')
        MasterSession = sessionmaker(bind=master_engine)
        master_session = MasterSession()
        
        tenant = master_session.query(Tenant).filter_by(institution_code='UEIPAB001').first()
        master_session.close()
        
        if tenant:
            g.current_tenant = tenant
            print(f"✓ Tenant set: {tenant.institution_name}")
        
        # Test the calculate_monthly_summary method
        current_date = date.today()
        month = current_date.month
        year = current_date.year
        
        print(f"\nTesting calculate_monthly_summary({month}, {year})...")
        
        report_service = MonthlyReportService(db.session)
        summaries = report_service.calculate_monthly_summary(month, year)
        
        print(f"✓ Success! Calculated {len(summaries)} summaries")
        
        for summary in summaries:
            print(f"  - Grade {summary.grade_level}: {summary.total_students} students, {summary.attendance_percentage}%")
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
