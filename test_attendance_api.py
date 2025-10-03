#!/usr/bin/env python3
"""
Test attendance API endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.core.app import create_app

app = create_app('development')

with app.app_context():
    with app.test_client() as client:
        print('🧪 Testing Attendance API Endpoints')
        print('=' * 70)
        
        # Test 1: Main attendance page
        print('\n1️⃣ Testing /bischeduler/attendance/')
        response = client.get('/bischeduler/attendance/')
        print(f'   Status: {response.status_code}')
        if response.status_code != 200:
            print(f'   Error: {response.data.decode()[:200]}')
        
        # Test 2: Sections API
        print('\n2️⃣ Testing /bischeduler/attendance/api/sections')
        response = client.get('/bischeduler/attendance/api/sections')
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            import json
            data = json.loads(response.data)
            print(f'   Sections found: {len(data) if isinstance(data, list) else "N/A"}')
        else:
            print(f'   Error: {response.data.decode()[:500]}')
        
        # Test 3: Admin statistics API
        print('\n3️⃣ Testing /bischeduler/attendance/api/admin/statistics')
        response = client.get('/bischeduler/attendance/api/admin/statistics')
        print(f'   Status: {response.status_code}')
        if response.status_code != 200:
            print(f'   Error: {response.data.decode()[:500]}')
        
        print('\n' + '=' * 70)
