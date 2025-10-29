// Login.js - User Authentication Component
import React, { useState } from 'react';
import './Login.css';

const Login = ({ onLogin }) => {  // ✅ Prop is named "onLogin"
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          remember_me: rememberMe
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        // Call the onLogin prop (not onLoginSuccess!)
        onLogin(data.token, data.user, data.session_timeout);
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure the backend is running.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('demo@company.com');
    setPassword('demo123');
    // Trigger the login automatically
    setTimeout(() => {
      document.getElementById('login-form').requestSubmit();
    }, 100);
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>🏢 Conference Room Booking</h1>
          <p>Sign in to manage your bookings</p>
        </div>

        <form id="login-form" onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading}
              />
              Remember me for 30 days
            </label>
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="demo-section">
          <p className="demo-text">Demo Account</p>
          <button
            onClick={handleDemoLogin}
            className="demo-button"
            disabled={loading}
          >
            🎭 Use Demo Account
          </button>
          <p className="demo-credentials">
            Email: demo@company.com<br />
            Password: demo123
          </p>
        </div>

        <div className="login-footer">
          <a href="#forgot-password">Forgot Password?</a>
        </div>
      </div>
    </div>
  );
};

export default Login;