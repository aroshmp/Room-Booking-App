// MyBookings.js - US-05: Cancel or Modify Booking (PRIORITY 5)
import React, { useState, useEffect } from 'react';
import './MyBookings.css';

const MyBookings = ({ userEmail }) => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCancelled, setShowCancelled] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [showModifyModal, setShowModifyModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);

  // Modify form state
  const [modifyForm, setModifyForm] = useState({
    date: '',
    start_time: '',
    end_time: ''
  });

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Fetch user bookings
  useEffect(() => {
    fetchBookings();
  }, [userEmail, showCancelled]);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_URL}/api/bookings/user/${userEmail}?show_cancelled=${showCancelled}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch bookings');
      }

      const data = await response.json();
      setBookings(data.bookings || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Check if booking can be cancelled/modified (at least 1 hour before)
  const canModifyBooking = (startTime) => {
    const bookingStart = new Date(startTime);
    const now = new Date();
    const timeUntilBooking = (bookingStart - now) / 1000 / 60; // minutes
    return timeUntilBooking >= 60;
  };

  // Format date and time for display
  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Calculate time until booking
  const getTimeUntilBooking = (startTime) => {
    const bookingStart = new Date(startTime);
    const now = new Date();
    const diffMinutes = Math.floor((bookingStart - now) / 1000 / 60);

    if (diffMinutes < 0) return 'Past booking';
    if (diffMinutes < 60) return `${diffMinutes} minutes away`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)} hours away`;
    return `${Math.floor(diffMinutes / 1440)} days away`;
  };

  // Handle cancel booking
  const handleCancelClick = (booking) => {
    setSelectedBooking(booking);
    setShowCancelModal(true);
  };

  const confirmCancel = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/bookings/${selectedBooking.booking_id}`,
        {
          method: 'DELETE'
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Failed to cancel booking');
      }

      alert('Booking cancelled successfully! Cancellation email sent.');
      setShowCancelModal(false);
      setSelectedBooking(null);
      fetchBookings(); // Refresh the list
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  // Handle modify booking
  const handleModifyClick = (booking) => {
    setSelectedBooking(booking);
    setModifyForm({
      date: booking.date,
      start_time: booking.start_time.split('T')[1].substring(0, 5),
      end_time: booking.end_time.split('T')[1].substring(0, 5)
    });
    setShowModifyModal(true);
  };

  const handleModifySubmit = async (e) => {
    e.preventDefault();

    try {
      const newStartTime = `${modifyForm.date}T${modifyForm.start_time}:00`;
      const newEndTime = `${modifyForm.date}T${modifyForm.end_time}:00`;

      const response = await fetch(
        `${API_URL}/api/bookings/${selectedBooking.booking_id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            date: modifyForm.date,
            start_time: newStartTime,
            end_time: newEndTime
          })
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Failed to modify booking');
      }

      alert('Booking modified successfully!');
      setShowModifyModal(false);
      setSelectedBooking(null);
      fetchBookings(); // Refresh the list
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  // Get status badge class
  const getStatusClass = (status) => {
    switch (status) {
      case 'active':
        return 'status-active';
      case 'cancelled':
        return 'status-cancelled';
      case 'completed':
        return 'status-completed';
      default:
        return 'status-default';
    }
  };

  if (loading) {
    return <div className="my-bookings-loading">Loading your bookings...</div>;
  }

  if (error) {
    return (
      <div className="my-bookings-error">
        <p>Error: {error}</p>
        <button onClick={fetchBookings}>Retry</button>
      </div>
    );
  }

  return (
    <div className="my-bookings-container">
      <div className="my-bookings-header">
        <h2>My Bookings</h2>
        <div className="bookings-controls">
          <label className="show-cancelled-toggle">
            <input
              type="checkbox"
              checked={showCancelled}
              onChange={(e) => setShowCancelled(e.target.checked)}
            />
            Show cancelled bookings
          </label>
          <button className="refresh-btn" onClick={fetchBookings}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {bookings.length === 0 ? (
        <div className="no-bookings">
          <p>No bookings found.</p>
          <p className="no-bookings-hint">
            {showCancelled
              ? 'You have no cancelled bookings.'
              : 'Start by booking a conference room!'}
          </p>
        </div>
      ) : (
        <div className="bookings-list">
          {bookings.map((booking) => (
            <div key={booking.booking_id} className="booking-card">
              <div className="booking-card-header">
                <h3>{booking.room_name || `Room ${booking.room_id}`}</h3>
                <span className={`booking-status ${getStatusClass(booking.status)}`}>
                  {booking.status || 'active'}
                </span>
              </div>

              <div className="booking-details">
                <div className="booking-detail-row">
                  <span className="detail-label">📅 Date:</span>
                  <span className="detail-value">{booking.date}</span>
                </div>

                <div className="booking-detail-row">
                  <span className="detail-label">🕐 Time:</span>
                  <span className="detail-value">
                    {formatDateTime(booking.start_time)} - {formatDateTime(booking.end_time)}
                  </span>
                </div>

                <div className="booking-detail-row">
                  <span className="detail-label">⏱️ Status:</span>
                  <span className="detail-value">
                    {getTimeUntilBooking(booking.start_time)}
                  </span>
                </div>

                <div className="booking-detail-row">
                  <span className="detail-label">🆔 Booking ID:</span>
                  <span className="detail-value booking-id">{booking.booking_id}</span>
                </div>

                {booking.location && (
                  <div className="booking-detail-row">
                    <span className="detail-label">📍 Location:</span>
                    <span className="detail-value">{booking.location}</span>
                  </div>
                )}
              </div>

              {booking.status === 'active' && canModifyBooking(booking.start_time) && (
                <div className="booking-actions">
                  <button
                    className="modify-btn"
                    onClick={() => handleModifyClick(booking)}
                  >
                    ✏️ Modify
                  </button>
                  <button
                    className="cancel-btn"
                    onClick={() => handleCancelClick(booking)}
                  >
                    ❌ Cancel
                  </button>
                </div>
              )}

              {booking.status === 'active' && !canModifyBooking(booking.start_time) && (
                <div className="booking-locked">
                  ⚠️ Cannot modify/cancel (less than 1 hour until start time)
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Cancel Confirmation Modal */}
      {showCancelModal && (
        <div className="modal-overlay" onClick={() => setShowCancelModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Cancel Booking?</h3>
            <p>Are you sure you want to cancel this booking?</p>
            <div className="modal-booking-details">
              <p><strong>Room:</strong> {selectedBooking.room_name || selectedBooking.room_id}</p>
              <p><strong>Date:</strong> {selectedBooking.date}</p>
              <p><strong>Time:</strong> {formatDateTime(selectedBooking.start_time)}</p>
            </div>
            <p className="cancel-warning">
              ⚠️ This action cannot be undone. A cancellation email will be sent.
            </p>
            <div className="modal-actions">
              <button className="modal-cancel-btn" onClick={() => setShowCancelModal(false)}>
                No, Keep Booking
              </button>
              <button className="modal-confirm-btn" onClick={confirmCancel}>
                Yes, Cancel Booking
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modify Booking Modal */}
      {showModifyModal && (
        <div className="modal-overlay" onClick={() => setShowModifyModal(false)}>
          <div className="modal-content modify-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Modify Booking</h3>
            <p className="modify-info">
              Changing time or date for: <strong>{selectedBooking.room_name || selectedBooking.room_id}</strong>
            </p>

            <form onSubmit={handleModifySubmit}>
              <div className="form-group">
                <label>New Date:</label>
                <input
                  type="date"
                  value={modifyForm.date}
                  onChange={(e) => setModifyForm({ ...modifyForm, date: e.target.value })}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Start Time:</label>
                  <input
                    type="time"
                    value={modifyForm.start_time}
                    onChange={(e) => setModifyForm({ ...modifyForm, start_time: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>End Time:</label>
                  <input
                    type="time"
                    value={modifyForm.end_time}
                    onChange={(e) => setModifyForm({ ...modifyForm, end_time: e.target.value })}
                    required
                  />
                </div>
              </div>

              <p className="modify-note">
                ℹ️ The system will check if the room is available for the new time slot.
              </p>

              <div className="modal-actions">
                <button
                  type="button"
                  className="modal-cancel-btn"
                  onClick={() => setShowModifyModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="modal-confirm-btn">
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyBookings;