import React, { useState } from 'react';
import Login from './Login';
import Dashboard from './Dashboard';
import Chatbot from './Chatbot';
import './App.css';

function App() {
    const [accessToken, setAccessToken] = useState('');
    const [refreshToken, setRefreshToken] = useState('');
    const [baseUrl, setBaseUrl] = useState('');
    const [ngrokUrl, setNgrokUrl] = useState('');

    const handleLogin = (access, refresh, base, ngrok) => {
        setAccessToken(access);
        setRefreshToken(refresh);
        setBaseUrl(base);
        setNgrokUrl(ngrok);
    };

    return (
        <div className="App">
            {!accessToken ? (
                <Login onLogin={handleLogin} />
            ) : (
                <>
                    <Dashboard accessToken={accessToken} refreshToken={refreshToken} baseUrl={baseUrl} ngrokUrl={ngrokUrl} />
                    <Chatbot accessToken={accessToken} baseUrl={baseUrl} apiUrl={ngrokUrl} />
                </>
            )}
        </div>
    );
}

export default App;
