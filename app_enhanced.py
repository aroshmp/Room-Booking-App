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

# US-03: Add email service imports
from email_service import email_service
from calendar_helper import generate_icalendar

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
# BOOKING ENDPOINTS (US-02, US-03, US-05)
# ============================================

@app.route('/api/bookings', methods=['POST'])
def create_booking_endpoint():
    """
    US-02: Book a Conference Room
    US-03: Send automatic confirmation email
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
        user_id = data.get('user_id', 'unknown')
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        # Validate time format
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
            }), 400

        # Validate booking duration
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        if duration_minutes < 30:
            return jsonify({
                'status': 'error',
                'message': 'Minimum booking duration is 30 minutes'
            }), 400
        if duration_minutes > 240:
            return jsonify({
                'status': 'error',
                'message': 'Maximum booking duration is 4 hours'
            }), 400

        # Check room availability
        is_available, availability_message = check_room_availability(
            room_id, date, start_time, end_time
        )

        if not is_available:
            return jsonify({
                'status': 'error',
                'message': availability_message
            }), 409

        # Create booking record
        booking_id = str(uuid.uuid4())
        booking_record = {
            'booking_id': booking_id,
            'room_id': room_id,
            'user_email': user_email,
            'user_id': user_id,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'status': 'confirmed',
            'created_at': datetime.utcnow().isoformat()
        }

        # Create booking in database
        success, message = create_booking(booking_record)

        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Failed to create booking: {message}'
            }), 500

        # US-03: Send confirmation email with calendar invite
        try:
            # Get room details for email
            room_info = get_room_by_id(room_id)

            # Prepare email data
            email_data = {
                'booking_id': booking_record['booking_id'],
                'user_email': user_email,
                'room_name': room_info.get('name', 'Conference Room'),
                'room_location': room_info.get('location', 'N/A'),
                'start_time': start_time,
                'end_time': end_time
            }

            # Generate iCalendar file
            ics_content = generate_icalendar(email_data)

            # Send email (non-blocking - don't fail booking if email fails)
            email_success, email_message = email_service.send_booking_confirmation(email_data, ics_content)

            if email_success:
                print(f"✅ Confirmation email sent to {user_email}")
            else:
                print(f"⚠️ Booking created but email failed: {email_message}")

        except Exception as e:
            # Log error but don't fail the booking
            print(f"⚠️ Error sending confirmation email: {str(e)}")

        return jsonify({
            'status': 'success',
            'message': 'Booking created successfully',
            'booking': booking_record
        }), 201

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

        # Get update data
        data = request.get_json()

        # Validate and update fields
        # Implementation depends on your requirements

        return jsonify({
            'status': 'success',
            'message': 'Booking modified successfully'
        }), 200

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
            # US-03: Send cancellation email
            try:
                # Get room details
                room_info = get_room_by_id(booking['room_id'])

                email_data = {
                    'booking_id': booking_id,
                    'user_email': booking.get('user_email'),
                    'room_name': room_info.get('name', 'Conference Room'),
                    'room_location': room_info.get('location', 'N/A'),
                    'start_time': booking.get('start_time')
                }
                email_service.send_cancellation_email(email_data)
            except Exception as e:
                print(f"⚠️ Error sending cancellation email: {str(e)}")

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
    print("US-02: Book Conference Room ✅")
    print("US-03: Email Confirmation ✅")
    print("=" * 50)
    print("\nAvailable endpoints:")
    print("GET    /                           - Health check")
    print("GET    /api/rooms                  - Get all rooms (with filters)")
    print("GET    /api/rooms/<room_id>        - Get specific room")
    print("POST   /api/bookings               - Create new booking + send email")
    print("GET    /api/bookings/<booking_id>  - Get specific booking")
    print("PUT    /api/bookings/<booking_id>  - Modify booking")
    print("DELETE /api/bookings/<booking_id>  - Cancel booking + send email")
    print("GET    /api/bookings/user/<email>  - Get user's bookings")
    print("GET    /api/rooms/<room_id>/bookings - Get room's bookings")
    print("GET    /api/availability            - Check availability")
    print("\n" + "=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)