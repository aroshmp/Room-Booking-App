// src/components/RoomList.js
import React, { useState, useEffect } from 'react';
import { roomsAPI } from '../services/api';
import './RoomList.css';

function RoomList({ onSelectRoom }) {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    capacity: '',
    amenities: '',
  });

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async (filterParams = {}) => {
    try {
      setLoading(true);
      const data = await roomsAPI.getAllRooms(filterParams);
      setRooms(data.rooms || []);
      setError(null);
    } catch (err) {
      setError('Failed to load rooms. Make sure Flask server is running on port 5000.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = () => {
    const filterParams = {};
    if (filters.capacity) filterParams.capacity = filters.capacity;
    if (filters.amenities) filterParams.amenities = filters.amenities;
    fetchRooms(filterParams);
  };

  const handleClearFilters = () => {
    setFilters({ capacity: '', amenities: '' });
    fetchRooms();
  };

  if (loading) return <div className="loading">Loading rooms...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="room-list-container">
      <h2>Available Conference Rooms</h2>

      {/* Filters */}
      <div className="filters">
        <div className="filter-group">
          <label>Min Capacity:</label>
          <input
            type="number"
            name="capacity"
            value={filters.capacity}
            onChange={handleFilterChange}
            placeholder="e.g., 10"
            min="1"
          />
        </div>

        <div className="filter-group">
          <label>Amenities:</label>
          <input
            type="text"
            name="amenities"
            value={filters.amenities}
            onChange={handleFilterChange}
            placeholder="e.g., projector"
          />
        </div>

        <button onClick={handleApplyFilters} className="btn-primary">
          Apply Filters
        </button>
        <button onClick={handleClearFilters} className="btn-secondary">
          Clear
        </button>
      </div>

      {/* Room Cards */}
      <div className="rooms-grid">
        {rooms.length === 0 ? (
          <p>No rooms found matching your criteria.</p>
        ) : (
          rooms.map((room) => (
            <div key={room.room_id} className="room-card">
              <div className="room-header">
                <h3>{room.name}</h3>
                <span className={`status ${room.status}`}>
                  {room.status === 'available' ? '✓ Available' : '✗ Unavailable'}
                </span>
              </div>

              <div className="room-details">
                <p><strong>Capacity:</strong> {room.capacity} people</p>
                <p><strong>Location:</strong> {room.location}</p>

                <div className="amenities">
                  <strong>Amenities:</strong>
                  <div className="amenity-tags">
                    {room.amenities?.map((amenity, idx) => (
                      <span key={idx} className="amenity-tag">
                        {amenity}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <button
                onClick={() => onSelectRoom(room)}
                className="btn-book"
                disabled={room.status !== 'available'}
              >
                Book This Room
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default RoomList;