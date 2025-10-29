# app_enhanced.py - COMPLETE VERSION WITH US-06 AUTHENTICATION
"""
Conference Room Booking System - Flask Backend
Includes US-01 through US-06
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv

# US-06: Authentication imports
import jwt
import hashlib
import secrets
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
SESSION_TIMEOUT = 7200  # 2 hours in seconds


# ============================================
# US-06: AUTHENTICATION HELPER FUNCTIONS
# ============================================

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_data, remember_me=False):
    """Generate JWT token for authenticated user"""
    if remember_me:
        expiration = datetime.utcnow() + timedelta(days=30)
    else:
        expiration = datetime.utcnow() + timedelta(seconds=SESSION_TIMEOUT)

    payload = {
        'user_id': user_data['user_id'],
        'email': user_data['email'],
        'role': user_data.get('role', 'employee'),
        'exp': expiration,
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_by_email(email):
    """Get user from database (demo users for prototype)"""
    demo_users = {
        'demo@company.com': {
            'user_id': 'user-demo-001',
            'email': 'demo@company.com',
            'name': 'Demo User',
            'password_hash': hash_password('demo123'),
            'role': 'employee',
            'department': 'Engineering'
        },
        'admin@company.com': {
            'user_id': 'user-admin-001',
            'email': 'admin@company.com',
            'name': 'Admin User',
            'password_hash': hash_password('admin123'),
            'role': 'administrator',
            'department': 'IT'
        }
    }
    return demo_users.get(email.lower())


def require_auth(role=None):
    """Decorator to protect routes requiring authentication"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')

            if not auth_header.startswith('Bearer '):
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401

            token = auth_header.split(' ')[1]
            user_data = verify_token(token)

            if not user_data:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid or expired token'
                }), 401

            if role and user_data.get('role') != role:
                return jsonify({
                    'status': 'error',
                    'message': 'Insufficient permissions'
                }), 403

            request.user = user_data
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ============================================
# MOCK DATABASE (Replace with DynamoDB in production)
# ============================================

# Mock rooms database
ROOMS = [
    {
        'room_id': 'room-001',
        'name': 'Conference Room A',
        'capacity': 10,
        'location': 'Floor 1',
        'amenities': ['projector', 'whiteboard', 'video-conferencing']
    },
    {
        'room_id': 'room-002',
        'name': 'Meeting Room B',
        'capacity': 6,
        'location': 'Floor 2',
        'amenities': ['whiteboard', 'phone']
    },
    {
        'room_id': 'room-003',
        'name': 'Executive Suite',
        'capacity': 20,
        'location': 'Floor 3',
        'amenities': ['projector', 'whiteboard', 'video-conferencing', 'phone']
    }
]

# Mock bookings database
BOOKINGS = []


# ============================================
# BASIC ROUTES
# ============================================

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Conference Room Booking API is running',
        'version': '1.0.0',
        'endpoints': {
            'rooms': '/api/rooms',
            'bookings': '/api/bookings',
            'auth': '/api/auth/*'
        }
    }), 200


@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """US-01: Get all available rooms"""
    return jsonify({
        'status': 'success',
        'rooms': ROOMS,
        'count': len(ROOMS)
    }), 200


@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """US-02: Create a new booking"""
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

        # Create booking
        booking = {
            'booking_id': str(uuid.uuid4()),
            'room_id': data['room_id'],
            'user_email': data['user_email'],
            'user_id': data.get('user_id', 'guest'),
            'date': data['date'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'status': 'confirmed',
            'created_at': datetime.utcnow().isoformat()
        }

        BOOKINGS.append(booking)

        return jsonify({
            'status': 'success',
            'message': 'Booking created successfully',
            'booking_id': booking['booking_id'],
            'booking': booking
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to create booking: {str(e)}'
        }), 500


@app.route('/api/bookings/user/<email>', methods=['GET'])
def get_user_bookings(email):
    """US-05: Get all bookings for a user"""
    user_bookings = [b for b in BOOKINGS if b['user_email'] == email]

    return jsonify({
        'status': 'success',
        'bookings': user_bookings,
        'count': len(user_bookings)
    }), 200


# ============================================
# US-06: AUTHENTICATION ROUTES
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """US-06: User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)

        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400

        user = get_user_by_email(email)

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401

        password_hash = hash_password(password)
        if password_hash != user['password_hash']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401

        token = generate_token(user, remember_me)

        user_data = {
            'user_id': user['user_id'],
            'email': user['email'],
            'name': user['name'],
            'role': user.get('role', 'employee'),
            'department': user.get('department', 'N/A')
        }

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'user': user_data,
            'session_timeout': SESSION_TIMEOUT
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """US-06: User logout endpoint"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'Logout successful'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Logout failed: {str(e)}'
        }), 500


@app.route('/api/auth/verify', methods=['GET'])
def verify_session():
    """US-06: Verify current session token"""
    try:
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'status': 'error',
                'message': 'No token provided'
            }), 401

        token = auth_header.split(' ')[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401

        return jsonify({
            'status': 'success',
            'message': 'Token is valid',
            'user': {
                'user_id': user_data['user_id'],
                'email': user_data['email'],
                'role': user_data['role']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Verification failed: {str(e)}'
        }), 500


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """US-06: Password reset request"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()

        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Email is required'
            }), 400

        user = get_user_by_email(email)

        if user:
            reset_token = secrets.token_urlsafe(32)
            print(f"Password reset requested for {email}")
            print(f"Reset token: {reset_token}")

        return jsonify({
            'status': 'success',
            'message': 'If an account exists with that email, a reset link has been sent'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Password reset failed: {str(e)}'
        }), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """US-06: Refresh authentication token"""
    try:
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'status': 'error',
                'message': 'No token provided'
            }), 401

        token = auth_header.split(' ')[1]
        user_data = verify_token(token)

        if not user_data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401

        new_token = generate_token({
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'role': user_data['role']
        })

        return jsonify({
            'status': 'success',
            'message': 'Token refreshed',
            'token': new_token
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Token refresh failed: {str(e)}'
        }), 500


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("Conference Room Booking System - Backend API")
    print("=" * 60)
    print("\n📍 Available Endpoints:")
    print("   GET  /                     - Health check")
    print("   GET  /api/rooms            - List all rooms")
    print("   POST /api/bookings         - Create booking")
    print("   GET  /api/bookings/user/<email> - Get user bookings")
    print("   POST /api/auth/login       - User login")
    print("   POST /api/auth/logout      - User logout")
    print("   GET  /api/auth/verify      - Verify token")
    print("   POST /api/auth/reset-password - Reset password")
    print("   POST /api/auth/refresh     - Refresh token")
    print("\n🔐 Demo Credentials:")
    print("   Email: demo@company.com")
    print("   Password: demo123")
    print("\n🚀 Server starting...")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)