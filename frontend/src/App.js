// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RoomList from './components/RoomList';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Navigation Bar */}
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              🏢 Room Booking System
            </Link>
            <ul className="nav-menu">
              <li className="nav-item">
                <Link to="/" className="nav-link">
                  Browse Rooms
                </Link>
              </li>
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<RoomList />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="footer">
          <p>&copy; 2025 Conference Room Booking System</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;