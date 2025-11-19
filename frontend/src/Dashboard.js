import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const StatCard = ({ title, value, icon }) => (
    <div className="info-card">
        {icon}
        <h3>{title}</h3>
        <p>{value}</p>
    </div>
);

const SiteDashboard = ({ site, ngrokUrl, token }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (site && site.siteId) {
        setLoading(true);
        fetch(`${ngrokUrl}/sites/${site.siteId}/dashboard`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ base_url: site.base_url, access_token: token }),
        })
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            setData(data);
            setLoading(false);
        })
        .catch(error => {
            console.error("API Error fetching dashboard:", error);
            setData(null);
            setLoading(false);
        });
    }
}, [site, ngrokUrl, token]);

  return (
    <div className="info-card-grid">
        {loading ? <p>Loading...</p> : 
            data ? (
                <>
                    <StatCard title="Total Gateways" value={data.totalGatewayNum} />
                    <StatCard title="Connected Gateways" value={data.connectedGatewayNum} />
                    <StatCard title="Total Switches" value={data.totalSwitchNum} />
                    <StatCard title="Total APs" value={data.totalApNum} />
                    <StatCard title="Connected APs" value={data.connectedApNum} />
                    <StatCard title="Total Clients" value={data.totalClientNum} />
                </>
            ) : <p>No information to display.</p>
        }
    </div>
  );
};

const SiteDevices = ({ site, ngrokUrl, token }) => {
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedDevice, setSelectedDevice] = useState(null);

    useEffect(() => {
        if (site && site.siteId) {
            setLoading(true);
            fetch(`${ngrokUrl}/sites/${site.siteId}/devices`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_url: site.base_url, access_token: token }),
            })
            .then(res => res.json())
            .then(data => {
                setDevices(data);
                setLoading(false);
            })
            .catch(error => {
                console.error("API Error fetching devices:", error);
                setDevices([]);
                setLoading(false);
            });
        }
    }, [site, ngrokUrl, token]);

    const handleDeviceClick = (mac) => {
        fetch(`${ngrokUrl}/sites/${site.siteId}/devices/${mac}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ base_url: site.base_url, access_token: token }),
        })
        .then(res => res.json())
        .then(data => {
            setSelectedDevice(data);
        })
        .catch(error => {
            console.error("API Error fetching device details:", error);
        });
    };

    const getStatusInfo = (status) => {
        switch (status) {
            case 0: return { text: 'Disconnected', className: 'status-disconnected' };
            case 1: return { text: 'Connected', className: 'status-connected' };
            case 2: return { text: 'Pending', className: 'status-pending' };
            case 3: return { text: 'Heartbeat Missed', className: 'status-heartbeat-missed' };
            case 4: return { text: 'Isolated', className: 'status-isolated' };
            default: return { text: 'Unknown', className: 'status-unknown' };
        }
    };

    const getDetailStatusInfo = (detailStatus) => {
        const green = [14, 15, 16, 17];
        const red = [1, 24, 25, 26, 27, 30, 31, 32, 33, 40, 41];
        const yellow = [10, 11, 12, 13, 20, 21, 22, 23];
        if (green.includes(detailStatus)) return { className: 'status-connected' };
        if (red.includes(detailStatus)) return { className: 'status-disconnected' };
        if (yellow.includes(detailStatus)) return { className: 'status-pending' };
        return { className: 'status-unknown' };
    };

    return (
        <div className="info-card">
            <h3>Devices for {site.name}</h3>
            {loading ? <p>Loading devices...</p> : (
                <table className="devices-table">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Name</th>
                            <th>IP Address</th>
                            <th>Status</th>
                            <th>Detail Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices.map(device => {
                            const statusInfo = getStatusInfo(device.status);
                            const detailStatusInfo = getDetailStatusInfo(device.detailStatus);
                            return (
                                <tr key={device.mac} onClick={() => handleDeviceClick(device.mac)}>
                                    <td>{device.modelDisplayName}</td>
                                    <td>{device.name}</td>
                                    <td>{device.ip}</td>
                                    <td><span className={`status-pill ${statusInfo.className}`}>{statusInfo.text}</span></td>
                                    <td><span className={`status-pill ${detailStatusInfo.className}`}>{device.detailStatus}</span></td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            )}
            {selectedDevice && (
                <div className="device-details">
                    <h3>Device Details</h3>
                    <pre>{JSON.stringify(selectedDevice, null, 2)}</pre>
                    <button onClick={() => setSelectedDevice(null)}>Close</button>
                </div>
            )}
        </div>
    );
};

const SiteAuditLog = ({ site, ngrokUrl, token }) => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('All');

    useEffect(() => {
        if (site && site.siteId) {
            setLoading(true);
            fetch(`${ngrokUrl}/sites/${site.siteId}/audit_logs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_url: site.base_url, access_token: token }),
            })
            .then(res => res.json())
            .then(data => {
                setLogs(data);
                setLoading(false);
            })
            .catch(error => {
                console.error("API Error fetching audit logs:", error);
                setLogs([]);
                setLoading(false);
            });
        }
    }, [site, ngrokUrl, token]);

    const filteredLogs = logs.filter(log => {
        if (filter === 'All') return true;
        if (filter === 'Error' && log.status === 1) return true;
        if (filter === 'Warning' && log.status === 2) return true;
        if (filter === 'Info' && log.status === 0) return true;
        return false;
    });

    return (
        <div className="info-card">
            <h3>Audit Log for {site.name}</h3>
            <div className="log-filters">
                <button onClick={() => setFilter('All')} className={filter === 'All' ? 'active' : ''}>All</button>
                <button onClick={() => setFilter('Error')} className={filter === 'Error' ? 'active' : ''}>Error</button>
                <button onClick={() => setFilter('Warning')} className={filter === 'Warning' ? 'active' : ''}>Warning</button>
                <button onClick={() => setFilter('Info')} className={filter === 'Info' ? 'active' : ''}>Info</button>
            </div>
            {loading ? <p>Loading audit logs...</p> : (
                <table className="devices-table">
                    <thead>
                        <tr>
                            <th>TIME</th>
                            <th>OPERATOR</th>
                            <th>CATEGORY</th>
                            <th>STATUS</th>
                            <th>OPERATION</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredLogs.map(log => (
                            <tr key={log.id}>
                                <td>{new Date(log.timestamp).toLocaleString()}</td>
                                <td>{log.operator}</td>
                                <td>{log.category}</td>
                                <td>{log.status === 0 ? 'Info' : log.status === 1 ? 'Error' : 'Warning'}</td>
                                <td>{log.operation}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

const GlobalAuditLog = () => <div className="info-card"><h3>Global Audit Log</h3><p>Global audit log will be shown here.</p></div>;

const Chatbot = () => {
    return (
        <div className="chatbot-popup">
            {/* Header */}
            <div style={{ padding: '15px', backgroundColor: '#00A870', color: 'white', borderRadius: '8px 8px 0 0' }}>
                <h4>Chatbot</h4>
            </div>
            {/* Messages */}
            <div style={{ flexGrow: 1, padding: '15px', overflowY: 'auto' }}>
                <p>Hello! How can I help you?</p>
            </div>
            {/* Input */}
            <div style={{ padding: '15px', borderTop: '1px solid #ddd' }}>
                <input type="text" placeholder="Type a message..." style={{ width: '100%', padding: '8px' }} />
            </div>
        </div>
    );
};


// --- Main Dashboard Component ---

function Dashboard({ token, ngrokUrl, baseUrl }) {
  const [sites, setSites] = useState([]);
  const [selectedSite, setSelectedSite] = useState(null);
  const [activeView, setActiveView] = useState('dashboard');
  const [isChatbotOpen, setChatbotOpen] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);

  // Fetch sites on component mount
  useEffect(() => {
    if (token && ngrokUrl && baseUrl) {
        fetch(`${ngrokUrl}/sites`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ base_url: baseUrl, access_token: token }),
        })
        .then(res => res.json())
        .then(data => {
            if(data && data.result && Array.isArray(data.result.data)) {
                const sites = data.result.data;
                setSites(sites);
                if(sites.length > 0) {
                    // Automatically add the base_url to each site object for later use
                    const siteWithBaseUrl = { ...sites[0], base_url: baseUrl };
                    setSelectedSite(siteWithBaseUrl);
                }
            }
        });
    }

    const handleResize = () => {
        if (window.innerWidth > 768) {
            setSidebarOpen(true);
        } else {
            setSidebarOpen(false);
        }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [token, ngrokUrl, baseUrl]);

  const handleSiteChange = (e) => {
    const siteId = e.target.value;
    const site = sites.find(s => s.siteId === siteId);
    // Add base_url to the selected site object
    const siteWithBaseUrl = { ...site, base_url: baseUrl };
    setSelectedSite(siteWithBaseUrl);
  };

  const renderActiveView = () => {
    if (!selectedSite && activeView !== 'global_audit_log') {
      return <div className="info-card"><p>Please select a site to view its details.</p></div>;
    }
    
    switch (activeView) {
      case 'dashboard':
        return <SiteDashboard site={selectedSite} ngrokUrl={ngrokUrl} token={token} />;
      case 'devices':
        return <SiteDevices site={selectedSite} ngrokUrl={ngrokUrl} token={token} />;
      case 'site_audit_log':
        return <SiteAuditLog site={selectedSite} ngrokUrl={ngrokUrl} token={token} />;
      case 'global_audit_log':
        return <GlobalAuditLog />;
      default:
        return <SiteDashboard site={selectedSite} ngrokUrl={ngrokUrl} token={token} />;
    }
  };

  return (
    <div className="dashboard-container">
        <button className="hamburger" onClick={() => setSidebarOpen(!isSidebarOpen)}>
            <span></span>
            <span></span>
            <span></span>
        </button>

      {isSidebarOpen && (
          <aside className="sidebar">
            <h3>Omada Controller</h3>
            
            {/* Sites Dropdown */}
            <div className="sites-dropdown">
                <label htmlFor="site-select">Your Sites</label>
                <select id="site-select" onChange={handleSiteChange} value={selectedSite?.siteId || ''}>
                    {sites.map(site => (
                        <option key={site.siteId} value={site.siteId}>{site.name}</option>
                    ))}
                </select>
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
              <ul>
                <li className={activeView === 'dashboard' ? 'active' : ''} onClick={() => setActiveView('dashboard')}>Dashboard</li>
                <li className={activeView === 'devices' ? 'active' : ''} onClick={() => setActiveView('devices')}>Devices</li>
                <li className={activeView === 'site_audit_log' ? 'active' : ''} onClick={() => setActiveView('site_audit_log')}>Site Audit Log</li>
                <li className={activeView === 'global_audit_log' ? 'active' : ''} onClick={() => setActiveView('global_audit_log')}>Global Audit Log</li>
              </ul>
            </nav>
          </aside>
      )}

      <main className={`main-content ${isSidebarOpen ? '' : 'full-width'}`}>
        <div className="dashboard-header">
          <h2>{activeView.replace('_', ' ').toUpperCase()}</h2>
        </div>
        {renderActiveView()}
      </main>

      {/* Chatbot Icon and Popup */}
      {!isChatbotOpen && (
        <div className="chatbot-icon" onClick={() => setChatbotOpen(true)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </div>
      )}

      {isChatbotOpen && <Chatbot />}
       {isChatbotOpen && <button onClick={() => setChatbotOpen(false)} style={{position: 'fixed', bottom: '570px', right: '40px', zIndex: 1001, background: 'transparent', border: 'none', fontSize: '20px', color: '#2c3e50'}}>X</button>} 

    </div>
  );
}

export default Dashboard;
