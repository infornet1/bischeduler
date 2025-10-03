#!/usr/bin/env python3
"""
Test login functionality and database connection
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import mysql.connector
from werkzeug.security import check_password_hash

def test_database_connection():
    """Test direct database connection"""
    print('🔍 Testing Database Connection')
    print('=' * 60)
    
    master_db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '0000',
        'database': 'bischeduler_master',
        'charset': 'utf8mb4'
    }
    
    try:
        # Connect to master database
        print('📡 Connecting to bischeduler_master...')
        conn = mysql.connector.connect(**master_db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print('❌ Table "users" does not exist in bischeduler_master')
            print('   Please run: python manage.py init-db')
            cursor.close()
            conn.close()
            return
        
        print('✅ Connected to bischeduler_master')
        print('✅ Table "users" exists')
        
        # Check for admin user
        cursor.execute("""
            SELECT id, email, username, password_hash, first_name, last_name, 
                   role, status, failed_login_attempts, locked_until
            FROM users 
            WHERE email = 'admin@ueipab.edu.ve'
        """)
        
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print('\n❌ Admin user not found!')
            print('   Email: admin@ueipab.edu.ve')
            print('\n💡 To create admin user, run:')
            print('   python create_admin.py')
        else:
            print(f'\n✅ Admin user found:')
            print(f'   ID: {admin_user["id"]}')
            print(f'   Email: {admin_user["email"]}')
            print(f'   Username: {admin_user["username"]}')
            print(f'   Name: {admin_user["first_name"]} {admin_user["last_name"]}')
            print(f'   Role: {admin_user["role"]}')
            print(f'   Status: {admin_user["status"]}')
            print(f'   Failed login attempts: {admin_user["failed_login_attempts"]}')
            print(f'   Locked until: {admin_user["locked_until"]}')
            
            # Test password
            print('\n🔐 Testing password verification...')
            test_password = 'Admin123!'
            
            if admin_user['password_hash']:
                try:
                    # Test with werkzeug's check_password_hash
                    is_valid = check_password_hash(admin_user['password_hash'], test_password)
                    if is_valid:
                        print(f'   ✅ Password "Admin123!" is correct')
                    else:
                        print(f'   ❌ Password "Admin123!" is incorrect')
                        print(f'   💡 You may need to reset the password')
                except Exception as e:
                    print(f'   ❌ Error checking password: {e}')
            else:
                print('   ❌ No password hash found for admin user')
        
        # Count total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()
        print(f'\n📊 Total users in database: {user_count["count"]}')
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f'❌ Database connection error: {e}')
        print(f'\n💡 Troubleshooting:')
        print(f'   1. Check if MySQL is running')
        print(f'   2. Verify credentials: user=root, password=0000')
        print(f'   3. Verify database "bischeduler_master" exists')
        print(f'   4. Check MySQL port (default: 3306)')
    
    print('=' * 60)

if __name__ == '__main__':
    test_database_connection()
