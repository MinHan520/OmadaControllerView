import React, { useState } from 'react';
import './App.css';
import Login from './Login';
import Dashboard from './Dashboard';

function App() {
  const [accessToken, setAccessToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [baseUrl, setBaseUrl] = useState(null);
  const [ngrokUrl, setNgrokUrl] = useState(null);

  const handleLogin = (newAccessToken, newRefreshToken, url, ngrok) => {
    setAccessToken(newAccessToken);
    setRefreshToken(newRefreshToken);
    setBaseUrl(url);
    setNgrokUrl(ngrok);
  };

  return (
    <div className="App">
      <header className="App-header">
        {accessToken ? 
          <Dashboard 
            token={accessToken} 
            setToken={setAccessToken} // Pass the setter function
            refreshToken={refreshToken} 
            ngrokUrl={ngrokUrl} 
            baseUrl={baseUrl} 
          /> : 
          <Login onLogin={handleLogin} />
        }
      </header>
    </div>
  );
}

export default App;
