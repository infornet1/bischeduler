#!/usr/bin/env python3
"""
Test database connections
"""

import mysql.connector
from sqlalchemy import create_engine, text

print("🔍 Testing Database Connections")
print("=" * 70)

# Test 1: Master Database
print("\n1️⃣ Testing Master Database (bischeduler_master)")
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='0000',
        database='bischeduler_master'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tenants")
    count = cursor.fetchone()[0]
    print(f"   ✅ Connected! Found {count} tenants")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Tenant Database
print("\n2️⃣ Testing Tenant Database (ueipab_2025_data)")
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='0000',
        database='ueipab_2025_data'
    )
    cursor = conn.cursor()
    
    # Check students
    cursor.execute("SELECT COUNT(*) FROM students WHERE is_active = 1")
    students = cursor.fetchone()[0]
    print(f"   ✅ Connected! Found {students} active students")
    
    # Check teachers
    cursor.execute("SELECT COUNT(*) FROM teachers WHERE is_active = 1")
    teachers = cursor.fetchone()[0]
    print(f"   ✅ Found {teachers} active teachers")
    
    # Check sections
    cursor.execute("SELECT COUNT(*) FROM sections WHERE is_active = 1")
    sections = cursor.fetchone()[0]
    print(f"   ✅ Found {sections} active sections")
    
    # Check daily_attendance table structure
    cursor.execute("DESCRIBE daily_attendance")
    columns = cursor.fetchall()
    print(f"   ✅ daily_attendance table has {len(columns)} columns:")
    for col in columns:
        print(f"      - {col[0]} ({col[1]})")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: SQLAlchemy connection
print("\n3️⃣ Testing SQLAlchemy Connection")
try:
    engine = create_engine('mysql+pymysql://root:0000@localhost/ueipab_2025_data')
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM students"))
        count = result.scalar()
        print(f"   ✅ SQLAlchemy connected! Found {count} students")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Test get_tenant_session()
print("\n4️⃣ Testing get_tenant_session()")
try:
    from src.models.tenant import get_tenant_session, Student
    session = get_tenant_session()
    count = session.query(Student).count()
    print(f"   ✅ get_tenant_session() works! Found {count} students")
    session.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
