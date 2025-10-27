import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# DynamoDB Configuration
class DynamoDBConfig:
    def __init__(self):
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=self.region,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        # Table names
        self.ROOMS_TABLE = 'Rooms'
        self.BOOKINGS_TABLE = 'Bookings'
        self.USERS_TABLE = 'Users'

        # Initialize table references
        self.rooms_table = self.dynamodb.Table(self.ROOMS_TABLE)
        self.bookings_table = self.dynamodb.Table(self.BOOKINGS_TABLE)
        self.users_table = self.dynamodb.Table(self.USERS_TABLE)


# Create global instance
db_config = DynamoDBConfig()


# Helper Functions for Room Operations
def get_all_rooms():
    """Retrieve all conference rooms"""
    try:
        response = db_config.rooms_table.scan()
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error retrieving rooms: {e}")
        return []


def get_room_by_id(room_id):
    """Get a specific room by ID"""
    try:
        response = db_config.rooms_table.get_item(Key={'room_id': room_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error retrieving room: {e}")
        return None


def filter_rooms_by_criteria(capacity=None, amenities=None, location=None):
    """Filter rooms based on criteria"""
    try:
        filter_expression = None

        if capacity:
            filter_expression = Attr('capacity').gte(capacity)

        if amenities:
            for amenity in amenities:
                amenity_filter = Attr('amenities').contains(amenity)
                filter_expression = filter_expression & amenity_filter if filter_expression else amenity_filter

        if location:
            location_filter = Attr('location').contains(location)
            filter_expression = filter_expression & location_filter if filter_expression else location_filter

        if filter_expression:
            response = db_config.rooms_table.scan(FilterExpression=filter_expression)
        else:
            response = db_config.rooms_table.scan()

        return response.get('Items', [])
    except ClientError as e:
        print(f"Error filtering rooms: {e}")
        return []


# Helper Functions for Booking Operations
def create_booking(booking_data):
    """Create a new booking"""
    try:
        db_config.bookings_table.put_item(Item=booking_data)
        return True, "Booking created successfully"
    except ClientError as e:
        print(f"Error creating booking: {e}")
        return False, str(e)


def get_bookings_by_room(room_id, start_date=None):
    """Get all bookings for a specific room"""
    try:
        if start_date:
            response = db_config.bookings_table.query(
                IndexName='room_id-start_time-index',
                KeyConditionExpression=Key('room_id').eq(room_id) & Key('start_time').gte(start_date)
            )
        else:
            response = db_config.bookings_table.query(
                IndexName='room_id-start_time-index',
                KeyConditionExpression=Key('room_id').eq(room_id)
            )
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error retrieving bookings: {e}")
        return []


def get_booking_by_id(booking_id):
    """Get a specific booking by ID"""
    try:
        response = db_config.bookings_table.get_item(Key={'booking_id': booking_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error retrieving booking: {e}")
        return None


def update_booking_status(booking_id, status):
    """Update booking status (active, cancelled, completed)"""
    try:
        db_config.bookings_table.update_item(
            Key={'booking_id': booking_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': status}
        )
        return True, "Booking updated successfully"
    except ClientError as e:
        print(f"Error updating booking: {e}")
        return False, str(e)


def delete_booking(booking_id):
    """Delete a booking (for cancellation)"""
    try:
        db_config.bookings_table.delete_item(Key={'booking_id': booking_id})
        return True, "Booking deleted successfully"
    except ClientError as e:
        print(f"Error deleting booking: {e}")
        return False, str(e)


def get_user_bookings(user_email):
    """Get all bookings for a specific user"""
    try:
        response = db_config.bookings_table.scan(
            FilterExpression=Attr('user_email').eq(user_email)
        )
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error retrieving user bookings: {e}")
        return []


def check_room_availability(room_id, date, start_time, end_time):
    """Check if a room is available for the specified time slot"""
    try:
        # Get all bookings for this room on this date
        bookings = get_bookings_by_room(room_id, start_date=date)

        # Filter bookings for the same date and check for conflicts
        for booking in bookings:
            if booking.get('status') == 'cancelled':
                continue

            booking_date = booking.get('date')
            if booking_date != date:
                continue

            booking_start = booking.get('start_time')
            booking_end = booking.get('end_time')

            # Check for time overlap
            if (start_time < booking_end and end_time > booking_start):
                return False, "Room is already booked for this time slot"

        return True, "Room is available"
    except Exception as e:
        print(f"Error checking availability: {e}")
        return False, str(e)


# Helper Functions for User Operations
def create_user(user_data):
    """Create a new user"""
    try:
        db_config.users_table.put_item(Item=user_data)
        return True, "User created successfully"
    except ClientError as e:
        print(f"Error creating user: {e}")
        return False, str(e)


def get_user_by_email(email):
    """Get user by email"""
    try:
        response = db_config.users_table.scan(
            FilterExpression=Attr('email').eq(email)
        )
        items = response.get('Items', [])
        return items[0] if items else None
    except ClientError as e:
        print(f"Error retrieving user: {e}")
        return None