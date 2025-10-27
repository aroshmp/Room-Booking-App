// src/App.js - US-01: View Available Rooms Only
import React, { useEffect, useState } from 'react';
import RoomList from './components/RoomList';
import { healthCheck } from './services/api';
import './App.css';

function App() {
  const [isServerOnline, setIsServerOnline] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkServerStatus();
  }, []);

  const checkServerStatus = async () => {
    try {
      await healthCheck();
      setIsServerOnline(true);
    } catch (err) {
      setIsServerOnline(false);
    } finally {
      setChecking(false);
    }
  };

  if (checking) {
    return <div className="loading-screen">Checking server connection...</div>;
  }

  if (!isServerOnline) {
    return (
      <div className="error-screen">
        <h1>⚠️ Server Offline</h1>
        <p>Cannot connect to Flask backend at http://localhost:5000</p>
        <p>Please make sure the Flask server is running:</p>
        <code>python app_enhanced.py</code>
        <button onClick={checkServerStatus} className="btn-primary">
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="container">
          <h1>🏢 Conference Room Booking System</h1>
          {/*<p>US-01: View Available Rooms</p>*/}
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className="container">
          <RoomList onSelectRoom={(room) => alert(`Selected: ${room.name}`)} />
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="container">
          <p>
            Conference Room Booking System v1.0 (US-01) |
            Backend: <span className="status-indicator online"></span> Online
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;