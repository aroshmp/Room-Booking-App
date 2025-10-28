# calendar_helper.py
# US-03: Generate iCalendar (.ics) files for calendar invites

from datetime import datetime
import uuid


def generate_icalendar(booking_data):
    """
    Generate an iCalendar (.ics) file content for a booking

    Args:
        booking_data (dict): Booking information including:
            - booking_id
            - room_name
            - room_location
            - start_time (ISO format)
            - end_time (ISO format)
            - user_email

    Returns:
        str: iCalendar file content in RFC 5545 format
    """

    # Parse datetime strings
    start_dt = datetime.fromisoformat(booking_data['start_time'])
    end_dt = datetime.fromisoformat(booking_data['end_time'])

    # Format datetime for iCalendar (YYYYMMDDTHHMMSSZ format)
    start_str = start_dt.strftime('%Y%m%dT%H%M%S')
    end_str = end_dt.strftime('%Y%m%dT%H%M%S')
    created_str = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    # Generate unique UID for the event
    uid = f"{booking_data['booking_id']}@roombooking.com"

    # Create location string
    location = booking_data.get('room_location', booking_data['room_name'])

    # Create description
    description = f"""Conference Room Booking
Booking ID: {booking_data['booking_id']}
Room: {booking_data['room_name']}
Location: {location}

Please arrive 5 minutes early to set up.

This booking was made through the Conference Room Booking System.
"""

    # Generate iCalendar content (RFC 5545 format)
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Conference Room Booking System//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{created_str}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{booking_data['room_name']} - Conference Room Booking
LOCATION:{location}
DESCRIPTION:{description.replace(chr(10), '\\n')}
STATUS:CONFIRMED
SEQUENCE:0
ORGANIZER:mailto:noreply@roombooking.com
ATTENDEE;CN={booking_data['user_email']};RSVP=TRUE:mailto:{booking_data['user_email']}
BEGIN:VALARM
TRIGGER:-PT15M
DESCRIPTION:Room booking reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR"""

    return ics_content


def generate_cancellation_icalendar(booking_data):
    """
    Generate an iCalendar cancellation event

    Args:
        booking_data (dict): Original booking information

    Returns:
        str: iCalendar cancellation content
    """

    start_dt = datetime.fromisoformat(booking_data['start_time'])
    end_dt = datetime.fromisoformat(booking_data['end_time'])

    start_str = start_dt.strftime('%Y%m%dT%H%M%S')
    end_str = end_dt.strftime('%Y%m%dT%H%M%S')
    created_str = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    uid = f"{booking_data['booking_id']}@roombooking.com"
    location = booking_data.get('room_location', booking_data['room_name'])

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Conference Room Booking System//EN
METHOD:CANCEL
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{created_str}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:CANCELLED - {booking_data['room_name']}
LOCATION:{location}
STATUS:CANCELLED
SEQUENCE:1
ORGANIZER:mailto:noreply@roombooking.com
ATTENDEE:mailto:{booking_data['user_email']}
END:VEVENT
END:VCALENDAR"""

    return ics_content