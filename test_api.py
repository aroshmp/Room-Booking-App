import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5000/api"


def print_response(response, title):
    """Pretty print API response"""
    print("\n" + "=" * 60)
    print(f"TEST: {title}")
    print("=" * 60)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def test_health_check():
    """Test 1: Health check endpoint"""
    response = requests.get("http://localhost:5000/")
    print_response(response, "Health Check")


def test_get_all_rooms():
    """Test 2: Get all rooms (US-01)"""
    response = requests.get(f"{BASE_URL}/rooms")
    print_response(response, "Get All Rooms")
    return response.json().get('rooms', [])[0] if response.status_code == 200 else None


def test_filter_rooms():
    """Test 3: Filter rooms by capacity (US-04)"""
    response = requests.get(f"{BASE_URL}/rooms?capacity=10")
    print_response(response, "Filter Rooms by Capacity >= 10")


def test_filter_rooms_by_amenities():
    """Test 4: Filter rooms by amenities (US-04)"""
    response = requests.get(f"{BASE_URL}/rooms?amenities=projector&amenities=whiteboard")
    print_response(response, "Filter Rooms by Amenities")


def test_create_booking(room_id):
    """Test 5: Create a new booking (US-02)"""
    tomorrow = (datetime.now() + timedelta(days=1)).date()

    booking_data = {
        "room_id": room_id,
        "user_email": "test.user@company.com",
        "user_id": "test-user-001",
        "date": str(tomorrow),
        "start_time": f"{tomorrow}T10:00:00",
        "end_time": f"{tomorrow}T11:00:00"
    }

    response = requests.post(f"{BASE_URL}/bookings", json=booking_data)
    print_response(response, "Create New Booking")
    return response.json().get('booking_id') if response.status_code == 201 else None


def test_create_conflicting_booking(room_id):
    """Test 6: Attempt to create a conflicting booking (should fail)"""
    tomorrow = (datetime.now() + timedelta(days=1)).date()

    booking_data = {
        "room_id": room_id,
        "user_email": "another.user@company.com",
        "user_id": "test-user-002",
        "date": str(tomorrow),
        "start_time": f"{tomorrow}T10:30:00",  # Overlaps with previous booking
        "end_time": f"{tomorrow}T11:30:00"
    }

    response = requests.post(f"{BASE_URL}/bookings", json=booking_data)
    print_response(response, "Create Conflicting Booking (Should Fail)")


def test_get_user_bookings():
    """Test 7: Get all bookings for a user"""
    response = requests.get(f"{BASE_URL}/bookings/user/test.user@company.com")
    print_response(response, "Get User Bookings")


def test_get_booking(booking_id):
    """Test 8: Get specific booking details"""
    if booking_id:
        response = requests.get(f"{BASE_URL}/bookings/{booking_id}")
        print_response(response, "Get Specific Booking")


def test_check_availability(room_id):
    """Test 9: Check room availability"""
    tomorrow = (datetime.now() + timedelta(days=1)).date()

    # Check available time slot
    params = {
        "room_id": room_id,
        "date": str(tomorrow),
        "start_time": f"{tomorrow}T14:00:00",
        "end_time": f"{tomorrow}T15:00:00"
    }

    response = requests.get(f"{BASE_URL}/availability", params=params)
    print_response(response, "Check Room Availability (Available Slot)")

    # Check occupied time slot
    params["start_time"] = f"{tomorrow}T10:00:00"
    params["end_time"] = f"{tomorrow}T11:00:00"

    response = requests.get(f"{BASE_URL}/availability", params=params)
    print_response(response, "Check Room Availability (Occupied Slot)")


def test_get_room_bookings(room_id):
    """Test 10: Get all bookings for a specific room"""
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/bookings")
    print_response(response, "Get Room Bookings")


def test_cancel_booking(booking_id):
    """Test 11: Cancel a booking (US-05)"""
    if booking_id:
        response = requests.delete(f"{BASE_URL}/bookings/{booking_id}")
        print_response(response, "Cancel Booking")


def test_short_booking():
    """Test 12: Try to create booking shorter than 30 minutes (should fail)"""
    tomorrow = (datetime.now() + timedelta(days=1)).date()

    booking_data = {
        "room_id": "room-001",
        "user_email": "test.user@company.com",
        "user_id": "test-user-001",
        "date": str(tomorrow),
        "start_time": f"{tomorrow}T13:00:00",
        "end_time": f"{tomorrow}T13:15:00"  # Only 15 minutes
    }

    response = requests.post(f"{BASE_URL}/bookings", json=booking_data)
    print_response(response, "Create Short Booking (Should Fail)")


def test_long_booking():
    """Test 13: Try to create booking longer than 4 hours (should fail)"""
    tomorrow = (datetime.now() + timedelta(days=1)).date()

    booking_data = {
        "room_id": "room-001",
        "user_email": "test.user@company.com",
        "user_id": "test-user-001",
        "date": str(tomorrow),
        "start_time": f"{tomorrow}T09:00:00",
        "end_time": f"{tomorrow}T14:00:00"  # 5 hours
    }

    response = requests.post(f"{BASE_URL}/bookings", json=booking_data)
    print_response(response, "Create Long Booking (Should Fail)")


def main():
    print("\n" + "=" * 60)
    print("CONFERENCE ROOM BOOKING API - TEST SUITE")
    print("=" * 60)
    print("\nMake sure the Flask app is running on http://localhost:5000")
    print("Starting tests in 3 seconds...")

    import time
    time.sleep(3)

    try:
        # Run tests
        test_health_check()

        # Get a room to use for testing
        room = test_get_all_rooms()
        if not room:
            print("\nERROR: Could not retrieve rooms. Make sure tables are seeded.")
            return

        room_id = room['room_id']
        print(f"\nUsing room: {room['name']} ({room_id}) for testing")

        test_filter_rooms()
        test_filter_rooms_by_amenities()

        # Create a booking
        booking_id = test_create_booking(room_id)

        # Try to create conflicting booking
        test_create_conflicting_booking(room_id)

        test_get_user_bookings()
        test_get_booking(booking_id)
        test_check_availability(room_id)
        test_get_room_bookings(room_id)

        # Validation tests
        test_short_booking()
        test_long_booking()

        # Cancel the booking
        test_cancel_booking(booking_id)

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to Flask app.")
        print("Make sure the app is running: python app_enhanced.py")
    except Exception as e:
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    main()