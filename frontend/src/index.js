import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import ProtectedApp from './ProtectedApp';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ProtectedApp />
  </React.StrictMode>
);

// Optional: log metrics to console for development
reportWebVitals(console.log);

// Or, just call without argument in production
// reportWebVitals();
