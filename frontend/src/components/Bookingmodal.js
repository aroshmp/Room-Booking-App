// src/components/BookingModal.js
import React, { useState } from 'react';
import { bookingAPI } from '../services/api';
import './BookingModal.css';

function BookingModal({ room, onClose, onBookingSuccess }) {
  const [formData, setFormData] = useState({
    date: '',
    startTime: '',
    endTime: '',
    userEmail: '',
    userId: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [bookingConfirmation, setBookingConfirmation] = useState(null);

  // Get today's date in YYYY-MM-DD format for min date validation
  const today = new Date().toISOString().split('T')[0];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null); // Clear errors when user types
  };

  const validateForm = () => {
    // Check all fields are filled
    if (!formData.date || !formData.startTime || !formData.endTime || !formData.userEmail || !formData.userId) {
      setError('All fields are required');
      return false;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.userEmail)) {
      setError('Please enter a valid email address');
      return false;
    }

    // Create datetime objects for comparison
    const startDateTime = new Date(`${formData.date}T${formData.startTime}`);
    const endDateTime = new Date(`${formData.date}T${formData.endTime}`);

    // Check end time is after start time
    if (endDateTime <= startDateTime) {
      setError('End time must be after start time');
      return false;
    }

    // Calculate duration in minutes
    const durationMinutes = (endDateTime - startDateTime) / (1000 * 60);

    // US-02 Acceptance Criteria: Minimum 30 minutes
    if (durationMinutes < 30) {
      setError('Minimum booking duration is 30 minutes');
      return false;
    }

    // US-02 Acceptance Criteria: Maximum 4 hours (240 minutes)
    if (durationMinutes > 240) {
      setError('Maximum booking duration is 4 hours');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Format data for backend
      const bookingData = {
        room_id: room.room_id,
        user_email: formData.userEmail,
        user_id: formData.userId,
        date: formData.date,
        start_time: `${formData.date}T${formData.startTime}:00`,
        end_time: `${formData.date}T${formData.endTime}:00`,
      };

      // US-02: Create booking with conflict detection
      const response = await bookingAPI.createBooking(bookingData);

      // US-02 Acceptance Criteria: Generate unique booking ID and show confirmation
      setBookingConfirmation(response.booking);
      setSuccess(true);

      // Call parent callback if provided
      if (onBookingSuccess) {
        onBookingSuccess(response.booking);
      }

      // Auto-close modal after 3 seconds on success
      setTimeout(() => {
        onClose();
      }, 3000);

    } catch (err) {
      // Handle conflict detection errors
      if (err.response?.status === 409) {
        setError('This room is already booked for the selected time. Please choose a different time slot.');
      } else if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else {
        setError('Failed to create booking. Please try again.');
      }
      console.error('Booking error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBackdropClick = (e) => {
    // Close modal when clicking outside the modal content -
    if (e.target.classList.contains('modal-backdrop')) {
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-content">
        {/* Modal Header */}
        <div className="modal-header">
          <h2>Book Conference Room</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        {/* Room Info */}
        <div className="room-info-box">
          <h3>{room.name}</h3>
          <div className="room-info-details">
            <span>📍 {room.location}</span>
            <span>👥 Capacity: {room.capacity}</span>
          </div>
        </div>

        {/* Success Message */}
        {success && bookingConfirmation && (
          <div className="success-message">
            <div className="success-icon">✓</div>
            <h3>Booking Confirmed!</h3>
            <p className="booking-id">Booking ID: <strong>{bookingConfirmation.booking_id}</strong></p>
            <div className="confirmation-details">
              <p>📅 {new Date(bookingConfirmation.date).toLocaleDateString()}</p>
              <p>🕐 {new Date(bookingConfirmation.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {new Date(bookingConfirmation.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
              <p>📧 Confirmation sent to {bookingConfirmation.user_email}</p>
            </div>
            <p className="success-note">This window will close automatically...</p>
          </div>
        )}

        {/* Booking Form */}
        {!success && (
          <form onSubmit={handleSubmit} className="booking-form">
            {/* Date Field */}
            <div className="form-group">
              <label htmlFor="date">Date *</label>
              <input
                type="date"
                id="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                min={today}
                required
                className="form-input"
              />
            </div>

            {/* Time Fields */}
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="startTime">Start Time *</label>
                <input
                  type="time"
                  id="startTime"
                  name="startTime"
                  value={formData.startTime}
                  onChange={handleChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="endTime">End Time *</label>
                <input
                  type="time"
                  id="endTime"
                  name="endTime"
                  value={formData.endTime}
                  onChange={handleChange}
                  required
                  className="form-input"
                />
              </div>
            </div>

            {/* User Information */}
            <div className="form-group">
              <label htmlFor="userEmail">Email Address *</label>
              <input
                type="email"
                id="userEmail"
                name="userEmail"
                value={formData.userEmail}
                onChange={handleChange}
                placeholder="your.email@company.com"
                required
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="userId">User ID *</label>
              <input
                type="text"
                id="userId"
                name="userId"
                value={formData.userId}
                onChange={handleChange}
                placeholder="e.g., user-001"
                required
                className="form-input"
              />
            </div>

            {/* Booking Rules Info */}
            <div className="booking-rules">
              <p className="rules-title">📋 Booking Rules:</p>
              <ul>
                <li>Minimum duration: 30 minutes</li>
                <li>Maximum duration: 4 hours</li>
                <li>Bookings must start in the future</li>
              </ul>
            </div>

            {/* Error Message */}
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠</span>
                {error}
              </div>
            )}

            {/* Form Actions */}
            <div className="form-actions">
              <button
                type="button"
                onClick={onClose}
                className="btn-cancel"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-submit"
                disabled={loading}
              >
                {loading ? 'Booking...' : 'Confirm Booking'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default BookingModal;