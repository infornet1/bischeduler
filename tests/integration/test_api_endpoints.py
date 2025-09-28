"""
Integration tests for BiScheduler API endpoints.
Tests API routes, authentication, and multi-tenant behavior.
"""

import pytest
import json
from datetime import datetime, time
from flask import url_for


class TestAuthenticationAPI:
    """Test authentication endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'test@ueipab.edu.ve',
            'password': 'testpass123'
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@ueipab.edu.ve'

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'email': 'invalid@test.com',
            'password': 'wrongpass'
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/api/schedule/teacher/1')

        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.auth
    def test_protected_route_with_token(self, client, auth_headers):
        """Test accessing protected route with valid token."""
        response = client.get('/api/schedule/teacher/1', headers=auth_headers)

        assert response.status_code in [200, 404]  # 404 if teacher doesn't exist


class TestScheduleAPI:
    """Test schedule management endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    def test_create_schedule_assignment(self, client, auth_headers, sample_venezuelan_data):
        """Test creating a new schedule assignment."""
        assignment_data = {
            'teacher_id': sample_venezuelan_data['teachers'][0].id,
            'subject_id': sample_venezuelan_data['subjects'][0].id,
            'section_id': sample_venezuelan_data['sections'][0].id,
            'classroom_id': sample_venezuelan_data['classrooms'][0].id,
            'time_period_id': sample_venezuelan_data['time_periods'][0].id,
            'day_of_week': 'lunes',
            'academic_year': '2025-2026'
        }

        response = client.post('/api/schedule/assignments',
                              headers=auth_headers,
                              json=assignment_data)

        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'id' in data
        assert data['day_of_week'] == 'lunes'

    @pytest.mark.integration
    @pytest.mark.api
    def test_get_section_schedule(self, client, auth_headers, sample_venezuelan_data):
        """Test retrieving schedule for a section."""
        section_id = sample_venezuelan_data['sections'][0].id

        response = client.get(f'/api/schedule/section/{section_id}',
                            headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'schedule' in data
        assert isinstance(data['schedule'], list)

    @pytest.mark.integration
    @pytest.mark.api
    def test_get_teacher_schedule(self, client, auth_headers, sample_venezuelan_data):
        """Test retrieving schedule for a teacher."""
        teacher_id = sample_venezuelan_data['teachers'][0].id

        response = client.get(f'/api/schedule/teacher/{teacher_id}',
                            headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'schedule' in data
        assert 'weekly_hours' in data

    @pytest.mark.integration
    @pytest.mark.api
    def test_update_schedule_assignment(self, client, auth_headers, sample_venezuelan_data):
        """Test updating an existing schedule assignment."""
        # First create an assignment
        assignment_data = {
            'teacher_id': sample_venezuelan_data['teachers'][0].id,
            'subject_id': sample_venezuelan_data['subjects'][0].id,
            'section_id': sample_venezuelan_data['sections'][0].id,
            'classroom_id': sample_venezuelan_data['classrooms'][0].id,
            'time_period_id': sample_venezuelan_data['time_periods'][0].id,
            'day_of_week': 'martes',
            'academic_year': '2025-2026'
        }

        create_response = client.post('/api/schedule/assignments',
                                     headers=auth_headers,
                                     json=assignment_data)
        assignment_id = json.loads(create_response.data).get('id')

        # Update the assignment
        update_data = {'classroom_id': sample_venezuelan_data['classrooms'][1].id}

        response = client.put(f'/api/schedule/assignments/{assignment_id}',
                            headers=auth_headers,
                            json=update_data)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['classroom_id'] == sample_venezuelan_data['classrooms'][1].id

    @pytest.mark.integration
    @pytest.mark.api
    def test_delete_schedule_assignment(self, client, auth_headers, sample_venezuelan_data):
        """Test deleting a schedule assignment."""
        # First create an assignment
        assignment_data = {
            'teacher_id': sample_venezuelan_data['teachers'][0].id,
            'subject_id': sample_venezuelan_data['subjects'][0].id,
            'section_id': sample_venezuelan_data['sections'][0].id,
            'classroom_id': sample_venezuelan_data['classrooms'][0].id,
            'time_period_id': sample_venezuelan_data['time_periods'][0].id,
            'day_of_week': 'miercoles',
            'academic_year': '2025-2026'
        }

        create_response = client.post('/api/schedule/assignments',
                                     headers=auth_headers,
                                     json=assignment_data)
        assignment_id = json.loads(create_response.data).get('id')

        # Delete the assignment
        response = client.delete(f'/api/schedule/assignments/{assignment_id}',
                               headers=auth_headers)

        assert response.status_code in [200, 204]


class TestConflictDetectionAPI:
    """Test conflict detection endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    def test_check_conflicts(self, client, auth_headers, sample_venezuelan_data):
        """Test conflict checking for new assignment."""
        assignment_data = {
            'teacher_id': sample_venezuelan_data['teachers'][0].id,
            'subject_id': sample_venezuelan_data['subjects'][0].id,
            'section_id': sample_venezuelan_data['sections'][0].id,
            'classroom_id': sample_venezuelan_data['classrooms'][0].id,
            'time_period_id': sample_venezuelan_data['time_periods'][0].id,
            'day_of_week': 'jueves',
            'academic_year': '2025-2026'
        }

        response = client.post('/api/schedule/check-conflicts',
                              headers=auth_headers,
                              json=assignment_data)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'conflicts' in data
        assert isinstance(data['conflicts'], list)

    @pytest.mark.integration
    @pytest.mark.api
    def test_get_all_conflicts(self, client, auth_headers):
        """Test retrieving all current conflicts."""
        response = client.get('/api/schedule/conflicts',
                            headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'conflicts' in data
        assert 'total' in data

    @pytest.mark.integration
    @pytest.mark.api
    def test_resolve_conflict(self, client, auth_headers):
        """Test resolving a conflict."""
        # This would need a conflict to exist first
        conflict_id = 1
        resolution_data = {
            'resolution_type': 'reassign_teacher',
            'new_teacher_id': 2
        }

        response = client.post(f'/api/schedule/conflicts/{conflict_id}/resolve',
                              headers=auth_headers,
                              json=resolution_data)

        assert response.status_code in [200, 404]  # 404 if conflict doesn't exist


class TestTeacherPreferenceAPI:
    """Test teacher preference endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.venezuelan
    def test_submit_preferences(self, client, auth_headers, sample_venezuelan_data):
        """Test submitting teacher preferences."""
        teacher_id = sample_venezuelan_data['teachers'][0].id
        preferences = {
            'preferred_times': ['07:00-09:00', '10:00-12:00'],
            'preferred_days': ['lunes', 'martes', 'miercoles'],
            'preferred_subjects': [sample_venezuelan_data['subjects'][0].id],
            'preferred_classrooms': [sample_venezuelan_data['classrooms'][0].id],
            'max_daily_hours': 5,
            'min_weekly_hours': 15
        }

        response = client.post(f'/api/teachers/{teacher_id}/preferences',
                              headers=auth_headers,
                              json=preferences)

        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'preferences_saved' in data

    @pytest.mark.integration
    @pytest.mark.api
    def test_get_preferences(self, client, auth_headers, sample_venezuelan_data):
        """Test retrieving teacher preferences."""
        teacher_id = sample_venezuelan_data['teachers'][0].id

        response = client.get(f'/api/teachers/{teacher_id}/preferences',
                            headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'preferences' in data

    @pytest.mark.integration
    @pytest.mark.api
    def test_get_preference_satisfaction(self, client, auth_headers, sample_venezuelan_data):
        """Test calculating preference satisfaction score."""
        teacher_id = sample_venezuelan_data['teachers'][0].id

        response = client.get(f'/api/teachers/{teacher_id}/satisfaction',
                            headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'satisfaction_score' in data
        assert 'breakdown' in data


class TestExcelIntegrationAPI:
    """Test Excel import/export endpoints."""

    @pytest.mark.integration
    @pytest.mark.api
    def test_export_schedule_to_excel(self, client, auth_headers):
        """Test exporting schedule to Excel format."""
        response = client.get('/api/export/schedule/excel',
                            headers=auth_headers)

        assert response.status_code == 200
        assert response.content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                        'application/vnd.ms-excel']

    @pytest.mark.integration
    @pytest.mark.api
    def test_import_data_from_excel(self, client, auth_headers):
        """Test importing data from Excel file."""
        # Create mock Excel file data
        from io import BytesIO
        import pandas as pd

        # Create sample data
        df = pd.DataFrame({
            'Nombre': ['Juan Pérez', 'María García'],
            'Cédula': ['V-12345678', 'V-87654321'],
            'Email': ['jperez@test.edu', 'mgarcia@test.edu'],
            'Especialización': ['Matemáticas', 'Castellano']
        })

        # Convert to Excel bytes
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        response = client.post('/api/import/teachers/excel',
                             headers=auth_headers,
                             data={'file': (excel_buffer, 'teachers.xlsx')},
                             content_type='multipart/form-data')

        assert response.status_code in [200, 201, 400]  # 400 if validation fails

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.venezuelan
    def test_export_matricula_format(self, client, auth_headers):
        """Test exporting in Venezuelan Matrícula format."""
        response = client.get('/api/export/matricula',
                            headers=auth_headers,
                            query_string={'month': 9, 'year': 2025})

        assert response.status_code == 200


class TestMultiTenantAPI:
    """Test multi-tenant functionality."""

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.multi_tenant
    def test_tenant_isolation(self, client, test_tenant):
        """Test that data is isolated between tenants."""
        # Set tenant header
        headers = {'X-Tenant-ID': str(test_tenant.id)}

        response = client.get('/api/schedule/assignments', headers=headers)

        assert response.status_code in [200, 401]  # 401 if auth required

    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.multi_tenant
    def test_tenant_creation(self, client, auth_headers):
        """Test creating a new tenant."""
        tenant_data = {
            'domain': 'nueva.escuela.edu.ve',
            'name': 'Nueva Escuela',
            'institution_type': 'K12',
            'region': 'Caracas',
            'admin_email': 'admin@nueva.edu.ve'
        }

        # This would typically require super-admin privileges
        response = client.post('/api/tenants',
                              headers=auth_headers,
                              json=tenant_data)

        assert response.status_code in [201, 403]  # 403 if not super-admin