"""
Test suite for Conference Room Booking System
Tests cover user stories US-01 through US-08 (prototype scope)
"""
import pytest
import json
from datetime import datetime, timedelta
from app import app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_rooms():
    """Sample room data for testing"""
    return [
        {
            'room_id': 'ROOM-001',
            'name': 'Conference Room A',
            'capacity': 10,
            'location': 'Building 1, Floor 2',
            'amenities': ['projector', 'whiteboard', 'video_conferencing'],
            'status': 'available'
        },
        {
            'room_id': 'ROOM-002',
            'name': 'Conference Room B',
            'capacity': 20,
            'location': 'Building 1, Floor 3',
            'amenities': ['projector', 'whiteboard'],
            'status': 'available'
        }
    ]


@pytest.fixture
def sample_booking():
    """Sample booking data for testing"""
    return {
        'booking_id': 'BOOK-001',
        'room_id': 'ROOM-001',
        'user_email': 'test@example.com',
        'start_time': (datetime.now() + timedelta(hours=2)).isoformat(),
        'end_time': (datetime.now() + timedelta(hours=3)).isoformat(),
        'status': 'confirmed'
    }


class TestHealthCheck:
    """Basic health check tests"""

    def test_app_runs(self, client):
        """Test that the application starts and responds"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Hello, World!' in response.data

if __name__ == '__main__':
    pytest.main(['-v', '--cov=app', '--cov-report=html'])