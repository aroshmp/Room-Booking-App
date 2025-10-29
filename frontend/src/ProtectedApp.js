// ProtectedApp.js - Authentication wrapper for the app
import React, { useState, useEffect, useCallback } from 'react';
import App from './App';
import Login from './components/Login';

const ProtectedApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  // Check authentication status
  const checkAuth = useCallback(() => {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('user');

    if (token && userData) {
      // Verify token is still valid
      fetch('http://localhost:5000/api/auth/verify', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setIsAuthenticated(true);
          setUser(JSON.parse(userData));
        } else {
          handleLogout();
        }
      })
      .catch(() => {
        handleLogout();
      })
      .finally(() => {
        setIsLoading(false);
      });
    } else {
      setIsLoading(false);
    }
  }, []); // No dependencies needed

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Session timeout monitoring
  const setupSessionMonitoring = useCallback(() => {
    const sessionTimeout = localStorage.getItem('sessionTimeout') || 7200; // 2 hours default
    const loginTime = localStorage.getItem('loginTime');

    if (loginTime) {
      const elapsed = Math.floor((Date.now() - parseInt(loginTime)) / 1000);
      const remaining = sessionTimeout - elapsed;

      if (remaining <= 0) {
        handleLogout();
      } else {
        // Check session every minute
        const interval = setInterval(() => {
          const elapsed = Math.floor((Date.now() - parseInt(loginTime)) / 1000);
          if (elapsed >= sessionTimeout) {
            handleLogout();
            clearInterval(interval);
          }
        }, 60000); // Check every minute

        return () => clearInterval(interval);
      }
    }
  }, []); // No dependencies needed

  useEffect(() => {
    if (isAuthenticated) {
      const cleanup = setupSessionMonitoring();
      return cleanup;
    }
  }, [isAuthenticated, setupSessionMonitoring]);

  const handleLogin = (token, userData, sessionTimeout) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('sessionTimeout', sessionTimeout);
    localStorage.setItem('loginTime', Date.now().toString());
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    localStorage.removeItem('sessionTimeout');
    localStorage.removeItem('loginTime');
    setIsAuthenticated(false);
    setUser(null);
  };

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '20px',
        color: '#666'
      }}>
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return <App user={user} onLogout={handleLogout} />;
};

export default ProtectedApp;