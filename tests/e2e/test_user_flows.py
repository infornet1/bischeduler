"""
End-to-end tests for BiScheduler critical user flows.
Tests complete user journeys through the application.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch


class TestCompleteScheduleCreationFlow:
    """Test complete schedule creation workflow."""

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_admin_creates_complete_schedule(self, client, test_admin, sample_venezuelan_data):
        """Test admin creating a complete weekly schedule."""
        # Step 1: Login as admin
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@ueipab.edu.ve',
            'password': 'adminpass123'
        })
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Step 2: Create multiple schedule assignments for a week
        created_assignments = []
        days = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']

        for day_idx, day in enumerate(days):
            for period_idx in range(3):  # 3 periods per day
                assignment_data = {
                    'teacher_id': sample_venezuelan_data['teachers'][0].id,
                    'subject_id': sample_venezuelan_data['subjects'][0].id,
                    'section_id': sample_venezuelan_data['sections'][0].id,
                    'classroom_id': sample_venezuelan_data['classrooms'][0].id,
                    'time_period_id': sample_venezuelan_data['time_periods'][period_idx].id,
                    'day_of_week': day,
                    'academic_year': '2025-2026'
                }

                response = client.post('/api/schedule/assignments',
                                      headers=headers,
                                      json=assignment_data)

                if response.status_code in [200, 201]:
                    created_assignments.append(json.loads(response.data))

        # Step 3: Verify schedule was created
        assert len(created_assignments) >= 10  # At least 10 assignments created

        # Step 4: Check for conflicts
        conflicts_response = client.get('/api/schedule/conflicts', headers=headers)
        assert conflicts_response.status_code == 200

        # Step 5: View complete section schedule
        section_id = sample_venezuelan_data['sections'][0].id
        schedule_response = client.get(f'/api/schedule/section/{section_id}',
                                      headers=headers)
        assert schedule_response.status_code == 200
        schedule_data = json.loads(schedule_response.data)
        assert len(schedule_data['schedule']) > 0

        # Step 6: Export to Excel
        export_response = client.get('/api/export/schedule/excel',
                                    headers=headers)
        assert export_response.status_code == 200


class TestTeacherPreferenceFlow:
    """Test teacher preference and satisfaction workflow."""

    @pytest.mark.e2e
    @pytest.mark.venezuelan
    def test_teacher_preference_workflow(self, client, test_user, sample_venezuelan_data):
        """Test complete teacher preference submission and satisfaction flow."""
        # Step 1: Teacher logs in
        login_response = client.post('/api/auth/login', json={
            'email': 'test@ueipab.edu.ve',
            'password': 'testpass123'
        })
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        teacher_id = sample_venezuelan_data['teachers'][0].id

        # Step 2: Teacher submits preferences
        preferences = {
            'preferred_times': ['07:00-09:00', '10:00-12:00'],
            'preferred_days': ['lunes', 'martes', 'miercoles'],
            'preferred_subjects': [sample_venezuelan_data['subjects'][0].id],
            'preferred_classrooms': [sample_venezuelan_data['classrooms'][0].id],
            'max_daily_hours': 5,
            'min_weekly_hours': 18,
            'max_weekly_hours': 26
        }

        pref_response = client.post(f'/api/teachers/{teacher_id}/preferences',
                                   headers=headers,
                                   json=preferences)
        assert pref_response.status_code in [200, 201]

        # Step 3: Admin creates schedule considering preferences
        admin_headers = headers  # Assume admin privileges

        # Create assignments that match preferences
        for day in ['lunes', 'martes']:
            assignment_data = {
                'teacher_id': teacher_id,
                'subject_id': sample_venezuelan_data['subjects'][0].id,
                'section_id': sample_venezuelan_data['sections'][0].id,
                'classroom_id': sample_venezuelan_data['classrooms'][0].id,
                'time_period_id': sample_venezuelan_data['time_periods'][0].id,
                'day_of_week': day,
                'academic_year': '2025-2026'
            }
            client.post('/api/schedule/assignments',
                       headers=admin_headers,
                       json=assignment_data)

        # Step 4: Teacher views their schedule
        schedule_response = client.get(f'/api/schedule/teacher/{teacher_id}',
                                      headers=headers)
        assert schedule_response.status_code == 200

        # Step 5: Calculate satisfaction score
        satisfaction_response = client.get(f'/api/teachers/{teacher_id}/satisfaction',
                                         headers=headers)
        assert satisfaction_response.status_code == 200
        satisfaction_data = json.loads(satisfaction_response.data)
        assert 'satisfaction_score' in satisfaction_data
        assert satisfaction_data['satisfaction_score'] >= 0.5  # At least 50% satisfied

        # Step 6: Teacher requests schedule change
        change_request = {
            'reason': 'Personal commitment on Tuesday mornings',
            'requested_changes': [
                {
                    'assignment_id': 1,
                    'new_day': 'jueves',
                    'new_time_period': sample_venezuelan_data['time_periods'][2].id
                }
            ]
        }
        change_response = client.post(f'/api/teachers/{teacher_id}/change-request',
                                     headers=headers,
                                     json=change_request)
        assert change_response.status_code in [200, 201]


class TestParentPortalFlow:
    """Test parent portal complete workflow."""

    @pytest.mark.e2e
    def test_parent_views_children_information(self, client, sample_venezuelan_data):
        """Test parent accessing children's schedules and information."""
        # Step 1: Parent logs in
        parent_credentials = {
            'email': 'parent@test.edu.ve',
            'password': 'parentpass123'
        }

        # Create parent account first
        client.post('/api/auth/register', json={
            **parent_credentials,
            'first_name': 'Parent',
            'last_name': 'Test',
            'role': 'parent',
            'children_ids': [s.id for s in sample_venezuelan_data['students'][:2]]
        })

        login_response = client.post('/api/auth/login', json=parent_credentials)
        if login_response.status_code == 200:
            token = json.loads(login_response.data)['access_token']
            headers = {'Authorization': f'Bearer {token}'}

            # Step 2: View children list
            children_response = client.get('/api/parent/children', headers=headers)
            assert children_response.status_code == 200

            # Step 3: View first child's schedule
            child_id = sample_venezuelan_data['students'][0].id
            schedule_response = client.get(f'/api/parent/child/{child_id}/schedule',
                                         headers=headers)
            assert schedule_response.status_code in [200, 404]

            # Step 4: View upcoming exams
            exams_response = client.get(f'/api/parent/child/{child_id}/exams',
                                       headers=headers)
            assert exams_response.status_code == 200

            # Step 5: View attendance records
            attendance_response = client.get(f'/api/parent/child/{child_id}/attendance',
                                           headers=headers,
                                           query_string={'month': 9, 'year': 2025})
            assert attendance_response.status_code == 200

            # Step 6: View grades
            grades_response = client.get(f'/api/parent/child/{child_id}/grades',
                                        headers=headers)
            assert grades_response.status_code == 200


class TestScheduleGenerationFlow:
    """Test automatic schedule generation workflow."""

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_automatic_schedule_generation(self, client, test_admin, sample_venezuelan_data):
        """Test complete automatic schedule generation with optimization."""
        # Step 1: Admin logs in
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@ueipab.edu.ve',
            'password': 'adminpass123'
        })
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Step 2: Configure generation parameters
        generation_config = {
            'algorithm': 'hybrid',  # Genetic + Constraint Solver
            'parameters': {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8,
                'constraints': {
                    'max_daily_hours': 6,
                    'min_weekly_hours': 12,
                    'max_consecutive_hours': 3,
                    'respect_preferences': True,
                    'venezuelan_compliance': True
                }
            },
            'sections': [s.id for s in sample_venezuelan_data['sections']],
            'academic_year': '2025-2026'
        }

        # Step 3: Trigger generation
        generate_response = client.post('/api/schedule/generate',
                                       headers=headers,
                                       json=generation_config)
        assert generate_response.status_code in [200, 202]  # 202 for async
        job_data = json.loads(generate_response.data)

        # Step 4: Check generation progress (if async)
        if 'job_id' in job_data:
            job_id = job_data['job_id']

            # Poll for completion
            import time
            for _ in range(30):  # Try for 30 seconds
                progress_response = client.get(f'/api/schedule/generate/{job_id}/status',
                                              headers=headers)
                status = json.loads(progress_response.data)

                if status['status'] == 'completed':
                    break
                time.sleep(1)

        # Step 5: Preview generated schedule
        preview_response = client.get('/api/schedule/preview',
                                     headers=headers)
        assert preview_response.status_code == 200
        preview_data = json.loads(preview_response.data)
        assert 'assignments' in preview_data
        assert 'statistics' in preview_data

        # Step 6: Apply generated schedule
        apply_response = client.post('/api/schedule/apply',
                                    headers=headers,
                                    json={'confirm': True})
        assert apply_response.status_code == 200

        # Step 7: Verify applied schedule
        for section in sample_venezuelan_data['sections']:
            schedule_response = client.get(f'/api/schedule/section/{section.id}',
                                         headers=headers)
            assert schedule_response.status_code == 200
            schedule = json.loads(schedule_response.data)
            assert len(schedule['schedule']) > 0


class TestAttendanceMonitoringFlow:
    """Test Venezuelan attendance monitoring workflow."""

    @pytest.mark.e2e
    @pytest.mark.venezuelan
    def test_attendance_tracking_and_reporting(self, client, test_user, sample_venezuelan_data):
        """Test complete attendance tracking and government reporting flow."""
        # Step 1: Teacher logs in
        login_response = client.post('/api/auth/login', json={
            'email': 'test@ueipab.edu.ve',
            'password': 'testpass123'
        })
        assert login_response.status_code == 200
        token = json.loads(login_response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        section_id = sample_venezuelan_data['sections'][0].id
        students = sample_venezuelan_data['students']

        # Step 2: Mark daily attendance for a month
        for day in range(1, 21):  # 20 school days
            attendance_data = {
                'section_id': section_id,
                'date': f'2025-09-{day:02d}',
                'attendance': [
                    {
                        'student_id': students[0].id,
                        'status': 'present' if day % 3 != 0 else 'absent',
                        'notes': 'Sick' if day % 3 == 0 else None
                    },
                    {
                        'student_id': students[1].id,
                        'status': 'present',
                        'notes': None
                    }
                ]
            }

            response = client.post('/api/attendance/mark',
                                  headers=headers,
                                  json=attendance_data)
            assert response.status_code in [200, 201]

        # Step 3: Generate monthly summary
        summary_response = client.get('/api/attendance/summary',
                                     headers=headers,
                                     query_string={'month': 9, 'year': 2025})
        assert summary_response.status_code == 200
        summary_data = json.loads(summary_response.data)
        assert 'total_students' in summary_data
        assert 'average_attendance' in summary_data

        # Step 4: Generate government report (Matrícula format)
        report_response = client.get('/api/attendance/export/matricula',
                                    headers=headers,
                                    query_string={'month': 9, 'year': 2025})
        assert report_response.status_code == 200
        assert 'application/vnd' in report_response.content_type

        # Step 5: Check for attendance alerts
        alerts_response = client.get('/api/attendance/alerts',
                                    headers=headers)
        assert alerts_response.status_code == 200
        alerts = json.loads(alerts_response.data)
        assert isinstance(alerts['alerts'], list)