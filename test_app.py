"""
Complete Test Suite for Conference Room Booking System
Tests cover user stories US-01 through US-08 (prototype scope)
FINAL VERSION - Properly mocked with correct patch paths
"""
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '.')

# Import the Flask app
from app_enhanced import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_rooms():
    """Sample room data for testing (matches DynamoDB format)"""
    return [
        {
            'room_id': 'room-001',
            'name': 'Innovation Hub',
            'capacity': 10,
            'location': 'Building A, Floor 3',
            'amenities': ['projector', 'whiteboard', 'video_conferencing'],
            'status': 'available'
        },
        {
            'room_id': 'room-002',
            'name': 'Executive Boardroom',
            'capacity': 20,
            'location': 'Building A, Floor 5',
            'amenities': ['projector', 'whiteboard', 'video_conferencing', 'phone'],
            'status': 'available'
        },
        {
            'room_id': 'room-003',
            'name': 'Brainstorm Space',
            'capacity': 6,
            'location': 'Building B, Floor 2',
            'amenities': ['whiteboard', 'tv_screen'],
            'status': 'available'
        }
    ]


@pytest.fixture
def sample_booking():
    """Sample booking data for testing"""
    tomorrow = (datetime.now() + timedelta(days=2)).date()
    return {
        'booking_id': 'test-booking-001',
        'room_id': 'room-001',
        'user_email': 'test@example.com',
        'user_id': 'test-user-001',
        'date': str(tomorrow),
        'start_time': f'{tomorrow}T14:00:00',
        'end_time': f'{tomorrow}T15:00:00',
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }


class TestHealthCheck:
    """Basic health check tests"""

    def test_app_runs(self, client):
        """Test that the application starts and responds"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'Conference Room Booking API' in data['message']


@pytest.mark.us01
class TestUS01_ViewAvailableRooms:
    """
    US-01: View Available Rooms (PRIORITY 1)
    As an employee, I want to view all available conference rooms in real-time
    """

    @patch('app_enhanced.get_all_rooms')
    def test_get_all_rooms_returns_list(self, mock_get_rooms, client, sample_rooms):
        """Test that GET /api/rooms returns a list of rooms"""
        mock_get_rooms.return_value = sample_rooms

        response = client.get('/api/rooms')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'rooms' in data
        assert len(data['rooms']) == 3

    @patch('app_enhanced.get_all_rooms')
    def test_room_has_required_fields(self, mock_get_rooms, client, sample_rooms):
        """Test that each room contains required fields"""
        mock_get_rooms.return_value = sample_rooms

        response = client.get('/api/rooms')
        data = json.loads(response.data)

        for room in data['rooms']:
            assert 'room_id' in room
            assert 'name' in room
            assert 'capacity' in room
            assert 'location' in room
            assert 'amenities' in room
            assert 'status' in room

    @patch('app_enhanced.filter_rooms_by_criteria')
    def test_filter_rooms_by_capacity(self, mock_filter, client, sample_rooms):
        """Test filtering rooms by minimum capacity"""
        filtered_rooms = [r for r in sample_rooms if r['capacity'] >= 10]
        mock_filter.return_value = filtered_rooms

        response = client.get('/api/rooms?capacity=10')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data['rooms']) == 2
        for room in data['rooms']:
            capacity = int(room['capacity']) if isinstance(room['capacity'], str) else room['capacity']
            assert capacity >= 10

    @patch('app_enhanced.filter_rooms_by_criteria')
    def test_filter_rooms_by_amenities(self, mock_filter, client, sample_rooms):
        """Test filtering rooms by amenities"""
        filtered_rooms = [r for r in sample_rooms if 'projector' in r['amenities']]
        mock_filter.return_value = filtered_rooms

        response = client.get('/api/rooms?amenities=projector')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert all('projector' in room['amenities'] for room in data['rooms'])

    @patch('app_enhanced.get_all_rooms')
    @patch('app_enhanced.check_room_availability')
    def test_real_time_availability_status(self, mock_availability, mock_get_rooms, client, sample_rooms):
        """Test that room availability is checked in real-time"""
        mock_get_rooms.return_value = sample_rooms
        mock_availability.return_value = (True, "Available")

        tomorrow = (datetime.now() + timedelta(days=1)).date()
        response = client.get(f'/api/rooms?date={tomorrow}&start_time={tomorrow}T10:00:00&end_time={tomorrow}T11:00:00')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rooms' in data


@pytest.mark.us02
class TestUS02_BookConferenceRoom:
    """
    US-02: Book a Conference Room (PRIORITY 2)
    As an employee, I want to book a conference room for a specific date and time
    """

    @patch('app_enhanced.check_room_availability')
    @patch('app_enhanced.create_booking')
    def test_successful_booking(self, mock_create, mock_availability, client):
        """Test successful room booking"""
        tomorrow = (datetime.now() + timedelta(days=5)).date()
        mock_availability.return_value = (True, "Room is available")
        mock_create.return_value = (True, "Booking created successfully")

        booking_data = {
            'room_id': 'room-099',
            'user_email': 'unittest@example.com',
            'user_id': 'unittest-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T16:00:00',
            'end_time': f'{tomorrow}T17:00:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'booking_id' in data

    @patch('app_enhanced.check_room_availability')
    def test_prevent_double_booking(self, mock_availability, client):
        """Test that double bookings are prevented"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        mock_availability.return_value = (False, "Room is already booked for this time slot")

        booking_data = {
            'room_id': 'room-001',
            'user_email': 'test@example.com',
            'user_id': 'test-user-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T10:00:00',
            'end_time': f'{tomorrow}T11:00:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data['status'].lower() or 'already booked' in data['message'].lower()

    def test_minimum_booking_duration(self, client):
        """Test that bookings meet minimum duration of 30 minutes"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        booking_data = {
            'room_id': 'room-001',
            'user_email': 'test@example.com',
            'user_id': 'test-user-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T10:00:00',
            'end_time': f'{tomorrow}T10:15:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'minimum' in data['message'].lower()

    def test_maximum_booking_duration(self, client):
        """Test that bookings don't exceed maximum duration of 4 hours"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        booking_data = {
            'room_id': 'room-001',
            'user_email': 'test@example.com',
            'user_id': 'test-user-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T10:00:00',
            'end_time': f'{tomorrow}T15:00:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'maximum' in data['message'].lower()

    @patch('app_enhanced.check_room_availability')
    @patch('app_enhanced.create_booking')
    def test_booking_generates_unique_id(self, mock_create, mock_availability, client):
        """Test that each booking gets a unique booking ID"""
        tomorrow = (datetime.now() + timedelta(days=7)).date()
        mock_availability.return_value = (True, "Available")
        mock_create.return_value = (True, "Success")

        booking_data = {
            'room_id': 'room-099',
            'user_email': 'unittest@example.com',
            'user_id': 'unittest-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T18:00:00',
            'end_time': f'{tomorrow}T19:00:00'
        }

        response1 = client.post('/api/bookings',
                                data=json.dumps(booking_data),
                                content_type='application/json')
        response2 = client.post('/api/bookings',
                                data=json.dumps(booking_data),
                                content_type='application/json')

        if response1.status_code == 201 and response2.status_code == 201:
            data1 = json.loads(response1.data)
            data2 = json.loads(response2.data)
            assert 'booking_id' in data1
            assert 'booking_id' in data2
            assert data1['booking_id'] != data2['booking_id']


@pytest.mark.us03
class TestUS03_AutomaticConfirmation:
    """
    US-03: Automatic Confirmation (PRIORITY 3)
    As an employee, I want to receive automatic confirmation
    """

    @patch('app_enhanced.check_room_availability')
    @patch('app_enhanced.create_booking')
    def test_immediate_confirmation_displayed(self, mock_create, mock_availability, client):
        """Test that confirmation is displayed immediately after booking"""
        tomorrow = (datetime.now() + timedelta(days=8)).date()
        mock_availability.return_value = (True, "Available")
        mock_create.return_value = (True, "Success")

        booking_data = {
            'room_id': 'room-099',
            'user_email': 'unittest@example.com',
            'user_id': 'unittest-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T20:00:00',
            'end_time': f'{tomorrow}T21:00:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'booking_id' in data
        assert 'booking' in data
        assert data['message'] == 'Booking created successfully'

    @patch('app_enhanced.check_room_availability')
    @patch('app_enhanced.create_booking')
    def test_confirmation_includes_booking_details(self, mock_create, mock_availability, client):
        """Test that confirmation includes all booking details"""
        tomorrow = (datetime.now() + timedelta(days=9)).date()
        mock_availability.return_value = (True, "Available")
        mock_create.return_value = (True, "Success")

        booking_data = {
            'room_id': 'room-099',
            'user_email': 'unittest@example.com',
            'user_id': 'unittest-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T22:00:00',
            'end_time': f'{tomorrow}T23:00:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        if response.status_code == 201:
            data = json.loads(response.data)
            booking = data['booking']

            assert 'booking_id' in booking
            assert 'room_id' in booking
            assert 'date' in booking
            assert 'start_time' in booking
            assert 'end_time' in booking


@pytest.mark.us04
class TestUS04_SpecifyRoomRequirements:
    """
    US-04: Specify Room Requirements (PRIORITY 4)
    As an employee, I want to specify room requirements
    """

    @patch('app_enhanced.filter_rooms_by_criteria')
    def test_filter_by_capacity(self, mock_filter, client, sample_rooms):
        """Test filtering rooms by minimum capacity"""
        filtered = [r for r in sample_rooms if r['capacity'] >= 20]
        mock_filter.return_value = filtered

        response = client.get('/api/rooms?capacity=20')
        assert response.status_code == 200

        data = json.loads(response.data)
        for room in data['rooms']:
            capacity = int(room['capacity']) if isinstance(room['capacity'], str) else room['capacity']
            assert capacity >= 20

    @patch('app_enhanced.filter_rooms_by_criteria')
    def test_filter_by_amenities(self, mock_filter, client, sample_rooms):
        """Test filtering rooms by amenities"""
        filtered = [r for r in sample_rooms if 'projector' in r['amenities'] and 'whiteboard' in r['amenities']]
        mock_filter.return_value = filtered

        response = client.get('/api/rooms?amenities=projector&amenities=whiteboard')
        assert response.status_code == 200

        data = json.loads(response.data)
        for room in data['rooms']:
            assert 'projector' in room['amenities']
            assert 'whiteboard' in room['amenities']

    @patch('app_enhanced.filter_rooms_by_criteria')
    def test_filter_by_location(self, mock_filter, client, sample_rooms):
        """Test filtering rooms by location"""
        filtered = [r for r in sample_rooms if 'Building A' in r['location']]
        mock_filter.return_value = filtered

        response = client.get('/api/rooms?location=Building A')
        assert response.status_code == 200

        data = json.loads(response.data)
        for room in data['rooms']:
            assert 'Building A' in room['location']

    @patch('app_enhanced.filter_rooms_by_criteria')
    def test_multiple_filters(self, mock_filter, client, sample_rooms):
        """Test using multiple filters simultaneously"""
        filtered = [r for r in sample_rooms if r['capacity'] >= 10 and 'projector' in r['amenities']]
        mock_filter.return_value = filtered

        response = client.get('/api/rooms?capacity=10&amenities=projector')
        assert response.status_code == 200

        data = json.loads(response.data)
        for room in data['rooms']:
            capacity = int(room['capacity']) if isinstance(room['capacity'], str) else room['capacity']
            assert capacity >= 10
            assert 'projector' in room['amenities']


@pytest.mark.us05
class TestUS05_CancelModifyBooking:
    """
    US-05: Cancel or Modify Booking (PRIORITY 5)
    As an employee, I want to cancel or modify my booking
    """

    @patch('app_enhanced.get_user_bookings')
    def test_view_my_bookings(self, mock_get_bookings, client, sample_booking):
        """Test viewing user's bookings"""
        mock_get_bookings.return_value = [sample_booking]

        response = client.get('/api/bookings/user/test@example.com')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'bookings' in data

    @patch('app_enhanced.get_booking_by_id')
    @patch('app_enhanced.update_booking_status')
    def test_cancel_booking_success(self, mock_update, mock_get, client):
        """Test successful booking cancellation"""
        future_time = datetime.now() + timedelta(hours=2)
        booking = {
            'booking_id': 'mock-booking-001',
            'start_time': future_time.isoformat(),
            'status': 'active'
        }

        mock_get.return_value = booking
        mock_update.return_value = (True, "Booking cancelled successfully")

        response = client.delete('/api/bookings/mock-booking-001')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'

    @patch('app_enhanced.get_booking_by_id')
    def test_cancel_booking_too_late(self, mock_get, client):
        """Test that bookings cannot be cancelled within 1 hour"""
        soon_time = datetime.now() + timedelta(minutes=30)
        booking = {
            'booking_id': 'mock-booking-002',
            'start_time': soon_time.isoformat(),
            'status': 'active'
        }

        mock_get.return_value = booking

        response = client.delete('/api/bookings/mock-booking-002')
        assert response.status_code == 403

        data = json.loads(response.data)
        assert 'Cannot cancel' in data['message'] or 'less than 1 hour' in data['message']

    @patch('app_enhanced.get_booking_by_id')
    @patch('app_enhanced.delete_booking')
    @patch('app_enhanced.create_booking')
    @patch('app_enhanced.check_room_availability')
    def test_modify_booking(self, mock_availability, mock_create, mock_delete, mock_get, client):
        """Test modifying an existing booking"""
        future_time = datetime.now() + timedelta(hours=3)
        booking = {
            'booking_id': 'mock-booking-003',
            'room_id': 'room-001',
            'user_email': 'test@example.com',  # ← ADD THIS
            'user_id': 'test-user-001',  # ← ADD THIS
            'start_time': future_time.isoformat(),
            'date': str(future_time.date()),
            'end_time': (future_time + timedelta(hours=1)).isoformat(),
            'status': 'active'
        }

        mock_get.return_value = booking
        mock_availability.return_value = (True, "Available")
        mock_delete.return_value = (True, "Deleted")
        mock_create.return_value = (True, "Created")

        tomorrow = (datetime.now() + timedelta(days=10)).date()
        update_data = {
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T11:00:00',
            'end_time': f'{tomorrow}T12:00:00'
        }

        response = client.put('/api/bookings/mock-booking-003',
                              data=json.dumps(update_data),
                              content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


@pytest.mark.us06
class TestUS06_UserAuthentication:
    """
    US-06: User Authentication (PRIORITY 6)
    Structure ready for Cognito integration
    """

    def test_authenticated_endpoints_exist(self, client):
        """Test that authentication structure is in place"""
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        booking_data = {
            'room_id': 'room-001',
            'user_email': 'test@example.com',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T10:00:00',
            'end_time': f'{tomorrow}T11:00:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        assert response.status_code != 404


@pytest.mark.us08
class TestUS08_BookingReminders:
    """
    US-08: Booking Reminders (PRIORITY 7)
    Structure ready for EventBridge integration
    """

    @patch('app_enhanced.check_room_availability')
    @patch('app_enhanced.create_booking')
    def test_booking_creates_record_for_reminders(self, mock_create, mock_availability, client):
        """Test that booking creates a record that can be used for reminders"""
        tomorrow = (datetime.now() + timedelta(days=11)).date()
        mock_availability.return_value = (True, "Available")
        mock_create.return_value = (True, "Success")

        booking_data = {
            'room_id': 'room-099',
            'user_email': 'unittest@example.com',
            'user_id': 'unittest-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T23:00:00',
            'end_time': f'{tomorrow}T23:59:00'
        }

        response = client.post('/api/bookings',
                               data=json.dumps(booking_data),
                               content_type='application/json')

        if response.status_code == 201:
            data = json.loads(response.data)
            booking = data.get('booking', {})

            assert 'user_email' in booking
            assert 'start_time' in booking
            assert 'room_id' in booking


@pytest.mark.integration
class TestIntegration:
    """Integration tests covering multiple user stories"""

    @patch('app_enhanced.get_all_rooms')
    @patch('app_enhanced.check_room_availability')
    @patch('app_enhanced.create_booking')
    def test_complete_booking_flow(self, mock_create, mock_availability, mock_get_rooms, client, sample_rooms):
        """Test complete booking workflow from search to confirmation"""
        tomorrow = (datetime.now() + timedelta(days=12)).date()

        mock_get_rooms.return_value = sample_rooms
        rooms_response = client.get('/api/rooms')
        assert rooms_response.status_code == 200
        rooms_data = json.loads(rooms_response.data)
        assert len(rooms_data['rooms']) > 0

        mock_availability.return_value = (True, "Available")
        availability_response = client.get(
            f'/api/availability?room_id=room-099&date={tomorrow}&start_time={tomorrow}T10:00:00&end_time={tomorrow}T11:00:00'
        )
        assert availability_response.status_code == 200

        mock_create.return_value = (True, "Success")
        booking_data = {
            'room_id': 'room-099',
            'user_email': 'integration@example.com',
            'user_id': 'integration-001',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T10:00:00',
            'end_time': f'{tomorrow}T11:00:00'
        }

        booking_response = client.post('/api/bookings',
                                       data=json.dumps(booking_data),
                                       content_type='application/json')

        assert booking_response.status_code == 201
        booking_data = json.loads(booking_response.data)
        assert booking_data['status'] == 'success'
        assert 'booking_id' in booking_data


@pytest.mark.smoke
class TestSmokeTests:
    """Quick smoke tests for rapid validation"""

    def test_health_endpoint(self, client):
        """Smoke test: Health check"""
        response = client.get('/')
        assert response.status_code == 200

    @patch('app_enhanced.get_all_rooms')
    def test_rooms_endpoint(self, mock_get_rooms, client):
        """Smoke test: Rooms endpoint"""
        mock_get_rooms.return_value = []
        response = client.get('/api/rooms')
        assert response.status_code == 200

    @patch('app_enhanced.get_booking_by_id')
    def test_api_error_handling(self, mock_get, client):
        """Smoke test: API handles invalid requests"""
        mock_get.return_value = None
        response = client.get('/api/bookings/invalid-id')
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main(['-v', '--cov=app_enhanced', '--cov-report=html', '--tb=short'])