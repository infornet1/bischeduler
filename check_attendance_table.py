#!/usr/bin/env python3
"""
Check the structure of daily_attendance table
"""

import mysql.connector

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '0000',
    'database': 'ueipab_2025_data',
    'charset': 'utf8mb4'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SHOW TABLES LIKE 'daily_attendance'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✅ Table 'daily_attendance' exists")
        print("\n📋 Table structure:")
        cursor.execute("DESCRIBE daily_attendance")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   - {col[0]} ({col[1]})")
    else:
        print("❌ Table 'daily_attendance' does not exist")
        print("\n💡 Available tables:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
