from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
from db_helper import (
    get_all_rooms,
    get_room_by_id,
    filter_rooms_by_criteria,
    create_booking,
    get_bookings_by_room,
    get_booking_by_id,
    update_booking_status,
    delete_booking,
    get_user_bookings,
    check_room_availability,
    get_user_by_email
)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration


# ============================================
# ROOM ENDPOINTS (US-01, US-04)
# ============================================

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Conference Room Booking API is running',
        'version': '1.0.0'
    })


@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """
    US-01: View Available Rooms
    Get all rooms or filter by criteria
    Query params: capacity, amenities, location, date, start_time, end_time
    """
    try:
        # Get query parameters
        capacity = request.args.get('capacity', type=int)
        amenities = request.args.getlist('amenities')
        location = request.args.get('location')
        date = request.args.get('date')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        # Get rooms based on filters
        if capacity or amenities or location:
            rooms = filter_rooms_by_criteria(capacity, amenities, location)
        else:
            rooms = get_all_rooms()

        # If date and time provided, check availability for each room
        if date and start_time and end_time:
            for room in rooms:
                is_available, _ = check_room_availability(
                    room['room_id'], date, start_time, end_time
                )
                room['is_available'] = is_available
        else:
            # Default to available if no time check
            for room in rooms:
                room['is_available'] = room.get('status') == 'available'

        return jsonify({
            'status': 'success',
            'count': len(rooms),
            'rooms': rooms
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/rooms/<room_id>', methods=['GET'])
def get_room(room_id):
    """Get details of a specific room"""
    try:
        room = get_room_by_id(room_id)

        if not room:
            return jsonify({
                'status': 'error',
                'message': 'Room not found'
            }), 404

        return jsonify({
            'status': 'success',
            'room': room
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# BOOKING ENDPOINTS (US-02, US-05)
# ============================================

@app.route('/api/bookings', methods=['POST'])
def create_new_booking():
    """
    US-02: Book a Conference Room
    Create a new booking with conflict detection
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['room_id', 'user_email', 'date', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        room_id = data['room_id']
        user_email = data['user_email']
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        # Validate booking duration (30 minutes to 4 hours)
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        duration = (end - start).total_seconds() / 60  # in minutes

        if duration < 30:
            return jsonify({
                'status': 'error',
                'message': 'Minimum booking duration is 30 minutes'
            }), 400

        if duration > 240:
            return jsonify({
                'status': 'error',
                'message': 'Maximum booking duration is 4 hours'
            }), 400

        # Check room availability
        is_available, message = check_room_availability(room_id, date, start_time, end_time)

        if not is_available:
            return jsonify({
                'status': 'error',
                'message': message
            }), 409  # Conflict

        # Create booking
        booking_id = str(uuid.uuid4())
        booking_data = {
            'booking_id': booking_id,
            'room_id': room_id,
            'user_email': user_email,
            'user_id': data.get('user_id', 'guest'),
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }

        success, result_message = create_booking(booking_data)

        if success:
            # US-03: In production, trigger SNS/SES for confirmation email here
            return jsonify({
                'status': 'success',
                'message': 'Booking created successfully',
                'booking_id': booking_id,
                'booking': booking_data
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': result_message
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get details of a specific booking"""
    try:
        booking = get_booking_by_id(booking_id)

        if not booking:
            return jsonify({
                'status': 'error',
                'message': 'Booking not found'
            }), 404

        return jsonify({
            'status': 'success',
            'booking': booking
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/bookings/user/<user_email>', methods=['GET'])
def get_user_bookings_endpoint(user_email):
    """Get all bookings for a specific user"""
    try:
        bookings = get_user_bookings(user_email)

        # Filter out cancelled bookings by default
        show_cancelled = request.args.get('show_cancelled', 'false').lower() == 'true'
        if not show_cancelled:
            bookings = [b for b in bookings if b.get('status') != 'cancelled']

        return jsonify({
            'status': 'success',
            'count': len(bookings),
            'bookings': bookings
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/bookings/<booking_id>', methods=['PUT'])
def modify_booking(booking_id):
    """
    US-05: Modify a booking (change time/date)
    Must be at least 1 hour before booking start time
    """
    try:
        booking = get_booking_by_id(booking_id)

        if not booking:
            return jsonify({
                'status': 'error',
                'message': 'Booking not found'
            }), 404

        # Check if booking can be modified (at least 1 hour before)
        booking_start = datetime.fromisoformat(booking['start_time'])
        now = datetime.now()
        time_until_booking = (booking_start - now).total_seconds() / 60  # minutes

        if time_until_booking < 60:
            return jsonify({
                'status': 'error',
                'message': 'Cannot modify booking less than 1 hour before start time'
            }), 403

        data = request.get_json()

        # If changing time/date, check new availability
        if 'date' in data or 'start_time' in data or 'end_time' in data:
            new_date = data.get('date', booking['date'])
            new_start = data.get('start_time', booking['start_time'])
            new_end = data.get('end_time', booking['end_time'])

            # Check availability for new time slot
            is_available, message = check_room_availability(
                booking['room_id'], new_date, new_start, new_end
            )

            if not is_available:
                return jsonify({
                    'status': 'error',
                    'message': message
                }), 409

            # Delete old booking and create new one
            delete_booking(booking_id)

            new_booking_id = str(uuid.uuid4())
            new_booking_data = {
                'booking_id': new_booking_id,
                'room_id': booking['room_id'],
                'user_email': booking['user_email'],
                'user_id': booking.get('user_id', 'guest'),
                'date': new_date,
                'start_time': new_start,
                'end_time': new_end,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'modified_from': booking_id
            }

            create_booking(new_booking_data)

            return jsonify({
                'status': 'success',
                'message': 'Booking modified successfully',
                'booking_id': new_booking_id,
                'booking': new_booking_data
            }), 200

        return jsonify({
            'status': 'error',
            'message': 'No modifications provided'
        }), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """
    US-05: Cancel a booking
    Must be at least 1 hour before booking start time
    """
    try:
        booking = get_booking_by_id(booking_id)

        if not booking:
            return jsonify({
                'status': 'error',
                'message': 'Booking not found'
            }), 404

        # Check if booking can be cancelled (at least 1 hour before)
        booking_start = datetime.fromisoformat(booking['start_time'])
        now = datetime.now()
        time_until_booking = (booking_start - now).total_seconds() / 60  # minutes

        if time_until_booking < 60:
            return jsonify({
                'status': 'error',
                'message': 'Cannot cancel booking less than 1 hour before start time'
            }), 403

        # Update status to cancelled instead of deleting
        success, message = update_booking_status(booking_id, 'cancelled')

        if success:
            # US-03: In production, trigger SNS/SES for cancellation email here
            return jsonify({
                'status': 'success',
                'message': 'Booking cancelled successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/rooms/<room_id>/bookings', methods=['GET'])
def get_room_bookings(room_id):
    """Get all bookings for a specific room"""
    try:
        date = request.args.get('date')
        bookings = get_bookings_by_room(room_id, date)

        # Filter out cancelled bookings by default
        show_cancelled = request.args.get('show_cancelled', 'false').lower() == 'true'
        if not show_cancelled:
            bookings = [b for b in bookings if b.get('status') != 'cancelled']

        return jsonify({
            'status': 'success',
            'room_id': room_id,
            'count': len(bookings),
            'bookings': bookings
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# AVAILABILITY CHECK ENDPOINT
# ============================================

@app.route('/api/availability', methods=['GET'])
def check_availability():
    """
    Check if a specific room is available for a time slot
    Query params: room_id, date, start_time, end_time
    """
    try:
        room_id = request.args.get('room_id')
        date = request.args.get('date')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        if not all([room_id, date, start_time, end_time]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters: room_id, date, start_time, end_time'
            }), 400

        is_available, message = check_room_availability(room_id, date, start_time, end_time)

        return jsonify({
            'status': 'success',
            'available': is_available,
            'message': message
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    print("=" * 50)
    print("Conference Room Booking API")
    print("=" * 50)
    print("\nAvailable endpoints:")
    print("GET    /                           - Health check")
    print("GET    /api/rooms                  - Get all rooms (with filters)")
    print("GET    /api/rooms/<room_id>        - Get specific room")
    print("POST   /api/bookings               - Create new booking")
    print("GET    /api/bookings/<booking_id>  - Get specific booking")
    print("PUT    /api/bookings/<booking_id>  - Modify booking")
    print("DELETE /api/bookings/<booking_id>  - Cancel booking")
    print("GET    /api/bookings/user/<email>  - Get user's bookings")
    print("GET    /api/rooms/<room_id>/bookings - Get room's bookings")
    print("GET    /api/availability            - Check availability")
    print("\n" + "=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)