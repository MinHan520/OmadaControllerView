import React, { useState } from 'react';
import './Login.css';

const NGROK_URL = "https://5d7a523e24d2.ngrok-free.app";

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [base_url, setBaseUrl] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    try {
      const response = await fetch(`${NGROK_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({ username, password, base_url }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        setSuccess('Congratulations! Login successful.');
        setError('');
        setTimeout(() => {
          // Pass both tokens to the parent component
          onLogin(data.access_token, data.refresh_token, base_url, NGROK_URL);
        }, 1500);
      } else {
        throw new Error(data.error || 'Invalid credentials. Please login again.');
      }
    } catch (err) {
      setError(err.message);
      setSuccess('');
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <input
        type="text"
        placeholder="Base URL"
        value={base_url}
        onChange={(e) => setBaseUrl(e.target.value)}
      />
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <div className="password-container">
        <input
          type={showPassword ? 'text' : 'password'}
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <span 
          className="password-toggle-icon"
          onClick={() => setShowPassword(!showPassword)} 
        >
          {showPassword ? '👁️' : '👁️‍🗨️'}
        </span>
      </div>
      <br />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default Login;
