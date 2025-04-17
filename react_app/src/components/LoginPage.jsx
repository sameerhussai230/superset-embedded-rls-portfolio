// src/components/LoginPage.jsx
import React, { useState } from 'react';
import './LoginPage.css'; // Specific styles for login

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// List of known manufacturers (can still be used for datalist suggestion)
const MANUFACTURERS = [
  "Cipla Ltd",
  "Torrent Pharmaceuticals Ltd",
  "Sun Pharmaceutical Industries Ltd",
  "Intas Pharmaceuticals Ltd",
  "Lupin Ltd",
];

// Add admin username for clarity, though not strictly needed for datalist
const ADMIN_USERNAME = "admin";

function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState(''); // Generic username state
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Send generic username and password
        body: JSON.stringify({ username: username, password: password }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`Login successful for ${data.user_type}:`, data.user_identifier);
        // Pass back both type and identifier
        onLoginSuccess(data.user_type, data.user_identifier);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || `Login failed: ${response.statusText}`);
        console.error('Login failed:', errorData);
      }
    } catch (err) {
      setError('An error occurred during login. Is the backend running?');
      console.error('Login fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>Dashboard Login</h2>
        <div className="form-group">
          {/* Changed label and input properties */}
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading}
            placeholder="Enter Manufacturer or admin" // Updated placeholder
            list="username-suggestions" // Use datalist for suggestions
          />
          {/* Datalist suggests manufacturers but allows typing 'admin' */}
          <datalist id="username-suggestions">
            <option value={ADMIN_USERNAME} />
            {MANUFACTURERS.map(mfr => <option key={mfr} value={mfr} />)}
          </datalist>
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
            placeholder="Enter password"
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" disabled={isLoading || !username || !password}>
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}

export default LoginPage;