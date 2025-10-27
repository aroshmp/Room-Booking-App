// src/services/api.js
// API Configuration - Connect React Frontend to Flask Backend

import axios from 'axios';

// API Base URL - reads from environment variable
// In development: http://localhost:5000/api
// In production (Vercel): https://room-booking-api.onrender.com/api
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds (Render free tier can be slow on cold start)
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================
// ROOM API METHODS (US-01, US-04)
// ============================================

export const roomAPI = {
  // US-01: Get all rooms
  getAllRooms: async (params = {}) => {
    try {
      const response = await api.get('/rooms', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get specific room by ID
  getRoomById: async (roomId) => {
    try {
      const response = await api.get(`/rooms/${roomId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // US-04: Filter rooms by criteria
  filterRooms: async (filters) => {
    try {
      const params = {};
      if (filters.capacity) params.capacity = filters.capacity;
      if (filters.amenities) params.amenities = filters.amenities;
      if (filters.location) params.location = filters.location;
      if (filters.date) params.date = filters.date;
      if (filters.start_time) params.start_time = filters.start_time;
      if (filters.end_time) params.end_time = filters.end_time;

      const response = await api.get('/rooms', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Check room availability
  checkAvailability: async (roomId, date, startTime, endTime) => {
    try {
      const response = await api.get('/availability', {
        params: {
          room_id: roomId,
          date,
          start_time: startTime,
          end_time: endTime
        }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get bookings for a specific room
  getRoomBookings: async (roomId, date = null) => {
    try {
      const params = date ? { date } : {};
      const response = await api.get(`/rooms/${roomId}/bookings`, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

// ============================================
// BOOKING API METHODS (US-02, US-05)
// ============================================

export const bookingAPI = {
  // US-02: Create new booking
  createBooking: async (bookingData) => {
    try {
      const response = await api.post('/bookings', bookingData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get specific booking by ID
  getBookingById: async (bookingId) => {
    try {
      const response = await api.get(`/bookings/${bookingId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all bookings for a user
  getUserBookings: async (userEmail, showCancelled = false) => {
    try {
      const params = { show_cancelled: showCancelled };
      const response = await api.get(`/bookings/user/${userEmail}`, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // US-05: Modify booking
  modifyBooking: async (bookingId, updates) => {
    try {
      const response = await api.put(`/bookings/${bookingId}`, updates);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // US-05: Cancel booking
  cancelBooking: async (bookingId) => {
    try {
      const response = await api.delete(`/bookings/${bookingId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

// Export the base API instance if needed
export default api;