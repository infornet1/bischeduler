"""
Check the structure of monthly_attendance_summary table
"""
import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='0000',
        database='ueipab001_tenant'
    )
    
    cursor = connection.cursor()
    
    # Show table structure
    cursor.execute("DESCRIBE monthly_attendance_summary")
    
    print("Current table structure:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[0]:30} {row[1]:20} {row[2]:10} {row[3]:10} {row[4]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
