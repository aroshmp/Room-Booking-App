import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import ProtectedApp from './ProtectedApp';  // ← Changed from App
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ProtectedApp />
  </React.StrictMode>
);

reportWebVitals();