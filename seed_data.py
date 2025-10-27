import boto3
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


def seed_rooms():
    """Add sample conference rooms"""
    rooms_table = dynamodb.Table('Rooms')

    rooms = [
        {
            'room_id': 'room-001',
            'name': 'Innovation Hub',
            'capacity': 10,
            'location': 'Building A, Floor 3',
            'amenities': ['projector', 'whiteboard', 'video_conferencing'],
            'photo_url': 'https://example.com/rooms/innovation-hub.jpg',
            'status': 'available'
        },
        {
            'room_id': 'room-002',
            'name': 'Executive Boardroom',
            'capacity': 20,
            'location': 'Building A, Floor 5',
            'amenities': ['projector', 'whiteboard', 'video_conferencing', 'phone'],
            'photo_url': 'https://example.com/rooms/boardroom.jpg',
            'status': 'available'
        },
        {
            'room_id': 'room-003',
            'name': 'Brainstorm Space',
            'capacity': 6,
            'location': 'Building B, Floor 2',
            'amenities': ['whiteboard', 'tv_screen'],
            'photo_url': 'https://example.com/rooms/brainstorm.jpg',
            'status': 'available'
        },
        {
            'room_id': 'room-004',
            'name': 'Team Collaboration Room',
            'capacity': 8,
            'location': 'Building A, Floor 2',
            'amenities': ['projector', 'whiteboard'],
            'photo_url': 'https://example.com/rooms/collaboration.jpg',
            'status': 'available'
        },
        {
            'room_id': 'room-005',
            'name': 'Conference Hall',
            'capacity': 50,
            'location': 'Building C, Floor 1',
            'amenities': ['projector', 'whiteboard', 'video_conferencing', 'phone', 'sound_system'],
            'photo_url': 'https://example.com/rooms/hall.jpg',
            'status': 'available'
        },
        {
            'room_id': 'room-006',
            'name': 'Quick Meeting Pod',
            'capacity': 4,
            'location': 'Building B, Floor 1',
            'amenities': ['whiteboard'],
            'photo_url': 'https://example.com/rooms/pod.jpg',
            'status': 'available'
        }
    ]

    print("Seeding Rooms table...")
    for room in rooms:
        try:
            rooms_table.put_item(Item=room)
            print(f"✓ Added room: {room['name']}")
        except Exception as e:
            print(f"✗ Error adding room {room['name']}: {e}")


def seed_users():
    """Add sample users"""
    users_table = dynamodb.Table('Users')

    users = [
        {
            'user_id': 'user-001',
            'email': 'john.doe@company.com',
            'name': 'John Doe',
            'department': 'Engineering',
            'notification_preferences': {
                'email': True,
                'sms': False,
                'reminder_minutes': 15
            }
        },
        {
            'user_id': 'user-002',
            'email': 'jane.smith@company.com',
            'name': 'Jane Smith',
            'department': 'Marketing',
            'notification_preferences': {
                'email': True,
                'sms': True,
                'reminder_minutes': 15
            }
        },
        {
            'user_id': 'user-003',
            'email': 'admin@company.com',
            'name': 'Admin User',
            'department': 'IT',
            'role': 'administrator',
            'notification_preferences': {
                'email': True,
                'sms': False,
                'reminder_minutes': 30
            }
        }
    ]

    print("\nSeeding Users table...")
    for user in users:
        try:
            users_table.put_item(Item=user)
            print(f"✓ Added user: {user['name']}")
        except Exception as e:
            print(f"✗ Error adding user {user['name']}: {e}")


def seed_sample_bookings():
    """Add some sample bookings for testing"""
    bookings_table = dynamodb.Table('Bookings')

    # Create bookings for today and tomorrow
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    bookings = [
        {
            'booking_id': str(uuid.uuid4()),
            'user_id': 'user-001',
            'user_email': 'john.doe@company.com',
            'room_id': 'room-001',
            'date': str(today),
            'start_time': f'{today}T10:00:00',
            'end_time': f'{today}T11:00:00',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        },
        {
            'booking_id': str(uuid.uuid4()),
            'user_id': 'user-002',
            'user_email': 'jane.smith@company.com',
            'room_id': 'room-002',
            'date': str(today),
            'start_time': f'{today}T14:00:00',
            'end_time': f'{today}T15:30:00',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        },
        {
            'booking_id': str(uuid.uuid4()),
            'user_id': 'user-001',
            'user_email': 'john.doe@company.com',
            'room_id': 'room-003',
            'date': str(tomorrow),
            'start_time': f'{tomorrow}T09:00:00',
            'end_time': f'{tomorrow}T10:00:00',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
    ]

    print("\nSeeding Bookings table...")
    for booking in bookings:
        try:
            bookings_table.put_item(Item=booking)
            print(f"✓ Added booking for {booking['room_id']} on {booking['date']}")
        except Exception as e:
            print(f"✗ Error adding booking: {e}")


def main():
    print("=" * 50)
    print("Seeding Sample Data for Room Booking System")
    print("=" * 50)
    print()

    seed_rooms()
    seed_users()
    seed_sample_bookings()

    print()
    print("=" * 50)
    print("Sample data seeding complete!")
    print("=" * 50)
    print("\nData added:")
    print("- 6 conference rooms")
    print("- 3 sample users")
    print("- 3 sample bookings")
    print("\nYou can now run 'python app.py' to start the application")


if __name__ == "__main__":
    main()