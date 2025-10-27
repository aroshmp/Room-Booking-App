// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Rooms API
export const roomsAPI = {
  // Get all rooms
  getAllRooms: async (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`/rooms${params ? '?' + params : ''}`);
    return response.data;
  },

  // Get specific room
  getRoom: async (roomId) => {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
  },

  // Get room's bookings
  getRoomBookings: async (roomId) => {
    const response = await api.get(`/rooms/${roomId}/bookings`);
    return response.data;
  },
};

// Bookings API
export const bookingsAPI = {
  // Create booking
  createBooking: async (bookingData) => {
    const response = await api.post('/bookings', bookingData);
    return response.data;
  },

  // Get booking
  getBooking: async (bookingId) => {
    const response = await api.get(`/bookings/${bookingId}`);
    return response.data;
  },

  // Get user's bookings
  getUserBookings: async (userEmail) => {
    const response = await api.get(`/bookings/user/${userEmail}`);
    return response.data;
  },

  // Modify booking
  modifyBooking: async (bookingId, updates) => {
    const response = await api.put(`/bookings/${bookingId}`, updates);
    return response.data;
  },

  // Cancel booking
  cancelBooking: async (bookingId) => {
    const response = await api.delete(`/bookings/${bookingId}`);
    return response.data;
  },

  // Check availability
  checkAvailability: async (params) => {
    const queryParams = new URLSearchParams(params).toString();
    const response = await api.get(`/availability?${queryParams}`);
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await axios.get('http://localhost:5000/');
  return response.data;
};

export default api;