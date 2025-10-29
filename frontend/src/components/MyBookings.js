// MyBookings.js - Display all bookings for the logged-in user
import React, { useState, useEffect } from 'react';
import './MyBookings.css';

const MyBookings = ({ user }) => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch bookings when component loads
  useEffect(() => {
    const fetchBookings = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use the logged-in user's email
        const userEmail = user?.email || 'demo@company.com';
        console.log('Fetching bookings for:', userEmail);

        const response = await fetch(`http://localhost:5000/api/bookings/user/${userEmail}`);
        const data = await response.json();

        console.log('Bookings response:', data);

        if (data.status === 'success') {
          setBookings(data.bookings || []);
        } else {
          setError('Failed to load bookings');
        }
      } catch (err) {
        console.error('Error fetching bookings:', err);
        setError('Failed to connect to server. Make sure backend is running on port 5000.');
      } finally {
        setLoading(false);
      }
    };

    fetchBookings();
  }, [user]);

  const cancelBooking = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return;
    }

    try {
      // Remove from local state (in production, call DELETE endpoint)
      setBookings(bookings.filter(b => b.booking_id !== bookingId));
      alert('Booking cancelled successfully!');
    } catch (err) {
      console.error('Error canceling booking:', err);
      alert('Failed to cancel booking');
    }
  };

  const getRoomName = (roomId) => {
    const roomNames = {
      'room-001': 'Conference Room A',
      'room-002': 'Meeting Room B',
      'room-003': 'Executive Suite'
    };
    return roomNames[roomId] || roomId;
  };

  if (loading) {
    return (
      <div className="my-bookings-container">
        <h2>My Bookings</h2>
        <div className="loading-message">
          <div className="spinner"></div>
          <p>Loading your bookings...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-bookings-container">
        <h2>My Bookings</h2>
        <div className="error-message">
          <p>⚠️ {error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="my-bookings-container">
      <div className="bookings-header">
        <h2>My Bookings</h2>
        <p className="user-info">Showing bookings for: <strong>{user?.email}</strong></p>
      </div>

      {bookings.length === 0 ? (
        <div className="no-bookings">
          <div className="no-bookings-icon">📅</div>
          <h3>No Bookings Yet</h3>
          <p>You haven't made any conference room bookings yet.</p>
          <p>Go to the booking page to reserve a room!</p>

          <div className="test-booking-info">
            <p><strong>Want to test?</strong> Create a booking via backend:</p>
            <pre className="code-example">
{`curl -X POST http://localhost:5000/api/bookings \\
  -H "Content-Type: application/json" \\
  -d '{
    "room_id": "room-001",
    "user_email": "${user?.email || 'demo@company.com'}",
    "user_id": "${user?.user_id || 'user-demo-001'}",
    "date": "2025-11-15",
    "start_time": "14:00",
    "end_time": "15:00"
  }'`}
            </pre>
          </div>
        </div>
      ) : (
        <div className="bookings-grid">
          {bookings.map((booking) => (
            <div key={booking.booking_id} className="booking-card">
              <div className="booking-card-header">
                <h3>{getRoomName(booking.room_id)}</h3>
                <span className={`status-badge ${booking.status}`}>
                  {booking.status}
                </span>
              </div>

              <div className="booking-card-body">
                <div className="booking-detail">
                  <span className="detail-label">📅 Date:</span>
                  <span className="detail-value">{booking.date}</span>
                </div>

                <div className="booking-detail">
                  <span className="detail-label">🕐 Time:</span>
                  <span className="detail-value">
                    {booking.start_time} - {booking.end_time}
                  </span>
                </div>

                <div className="booking-detail">
                  <span className="detail-label">🏢 Room ID:</span>
                  <span className="detail-value">{booking.room_id}</span>
                </div>

                <div className="booking-detail">
                  <span className="detail-label">📝 Booking ID:</span>
                  <span className="detail-value booking-id">
                    {booking.booking_id.substring(0, 8)}...
                  </span>
                </div>

                <div className="booking-detail">
                  <span className="detail-label">⏰ Created:</span>
                  <span className="detail-value">
                    {new Date(booking.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="booking-card-footer">
                <button
                  onClick={() => cancelBooking(booking.booking_id)}
                  className="cancel-button"
                >
                  ❌ Cancel Booking
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="bookings-summary">
        <p>Total bookings: <strong>{bookings.length}</strong></p>
      </div>
    </div>
  );
};

export default MyBookings;