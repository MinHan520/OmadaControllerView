import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';
import AIDashboard from './AIDashboard';
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

const DeviceDetails = ({ device, site, ngrokUrl, token, onBack }) => {
    const [details, setDetails] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (device && site && ngrokUrl && token) {
            setLoading(true);
            fetch(`${ngrokUrl}/sites/${site.siteId}/devices/${device.mac}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_url: site.base_url, access_token: token }),
            })
                .then(res => res.json())
                .then(data => {
                    if (data && !data.error) {
                        setDetails(data);
                    } else {
                        console.warn("Failed to fetch details, falling back to basic info:", data);
                    }
                    setLoading(false);
                })
                .catch(error => {
                    console.error("API Error fetching device details:", error);
                    setLoading(false);
                });
        }
    }, [device, site, ngrokUrl, token]);

    if (!device) return null;

    const displayDevice = details || device;

    return (
        <div className="device-details-container">
            <button className="back-button" onClick={onBack}>&larr; Back to Devices</button>
            <div className="info-card">
                <h3>Device Details: {displayDevice.name}</h3>
                {loading ? <p>Loading details...</p> : (
                    <>
                        <div className="details-grid">
                            <div className="detail-item"><strong>Name:</strong> {displayDevice.name}</div>
                            <div className="detail-item"><strong>Model:</strong> {displayDevice.model} {displayDevice.modelDisplayName}</div>
                            <div className="detail-item"><strong>MAC Address:</strong> {displayDevice.mac}</div>
                            <div className="detail-item"><strong>IP Address:</strong> {displayDevice.ip}</div>
                            <div className="detail-item"><strong>Status:</strong> {displayDevice.status === 1 ? 'Connected' : 'Disconnected'}</div>
                            <div className="detail-item"><strong>Uptime:</strong> {displayDevice.uptime}</div>
                            <div className="detail-item"><strong>CPU Usage:</strong> {displayDevice.cpuUtil}%</div>
                            <div className="detail-item"><strong>Memory Usage:</strong> {displayDevice.memUtil}%</div>
                        </div>
                        <div className="raw-data">
                            <h4>Raw Data</h4>
                            <pre>{JSON.stringify(displayDevice, null, 2)}</pre>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

const SiteDevices = ({ site, ngrokUrl, token, onDeviceSelect }) => {
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(true);

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
                    if (Array.isArray(data)) {
                        setDevices(data);
                    } else {
                        setDevices([]);
                    }
                    setLoading(false);
                })
                .catch(error => {
                    console.error("API Error fetching devices:", error);
                    setDevices([]);
                    setLoading(false);
                });
        }
    }, [site, ngrokUrl, token]);

    const getStatusInfo = (status) => {
        // 0: Disconnected, 1: Connected, 2: Pending, 3: Heartbeat Missed, 4: Isolated, 5: Provisioning
        switch (status) {
            case 0: return { text: 'DISCONNECTED', className: 'status-disconnected' };
            case 1: return { text: 'CONNECTED', className: 'status-connected' };
            case 2: return { text: 'PENDING', className: 'status-pending' }; // Adopting/Pending
            case 3: return { text: 'HEARTBEAT MISSED', className: 'status-disconnected' };
            case 4: return { text: 'ISOLATED', className: 'status-disconnected' };
            case 5: return { text: 'PROVISIONING', className: 'status-provisioning' };
            default: return { text: 'UNKNOWN', className: 'status-unknown' };
        }
    };

    return (
        <div className="info-card">
            <h3>Devices for {site.name}</h3>
            {loading ? <p>Loading devices...</p> : (
                <table className="devices-table">
                    <thead>
                        <tr>
                            <th>DEVICE NAME</th>
                            <th>IP ADDRESS</th>
                            <th>STATUS</th>
                            <th>MODEL</th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices.map(device => {
                            const statusInfo = getStatusInfo(device.status);
                            return (
                                <tr key={device.mac} onClick={() => onDeviceSelect(device)}>
                                    <td>
                                        <div className="device-name-cell">
                                            {/* Placeholder icon if needed */}
                                            <span className="device-icon"></span>
                                            {device.name}
                                        </div>
                                    </td>
                                    <td>{device.ip}</td>
                                    <td><span className={`status-pill ${statusInfo.className}`}>{statusInfo.text}</span></td>
                                    <td>{device.modelDisplayName || device.model}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            )}
        </div>
    );
};

const SiteAuditLog = ({ site, ngrokUrl, token }) => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('All');

    useEffect(() => {
        if (site && site.siteId && ngrokUrl && token) {
            setLoading(true);
            fetch(`${ngrokUrl}/sites/${site.siteId}/audit_logs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_url: site.base_url, access_token: token }),
            })
                .then(res => res.json())
                .then(data => {
                    if (data && data.result && Array.isArray(data.result.data)) {
                        setLogs(data.result.data);
                    } else {
                        setLogs([]);
                    }
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
        // Check status code OR level string (e.g. "Error", "Warning", "Info")
        const levelStr = (log.level || '').toString().toLowerCase();
        if (filter === 'Error' && (log.status === 1 || levelStr.includes('error') || levelStr.includes('fail'))) return true;
        if (filter === 'Warning' && (log.status === 2 || levelStr.includes('warn'))) return true;
        if (filter === 'Info' && (log.status === 0 || levelStr.includes('info') || levelStr.includes('success'))) return true;
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
                            <th>TYPE</th>
                            <th>LEVEL</th>
                            <th>CONTENT</th>
                            <th>TIME</th>
                            <th>RESULT</th>
                            <th>ACTION</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredLogs.map(log => (
                            <tr key={log.id}>
                                <td>{log.auditType}</td>
                                <td>{log.level}</td>
                                <td>{log.content}</td>
                                <td>{new Date(log.time).toLocaleString()}</td>
                                <td>{log.result}</td>
                                <td>
                                    <button className="action-btn resolve-btn" title="Resolve" onClick={() => console.log("Resolve clicked", log.id)}>
                                        ✓
                                    </button>
                                    <button className="action-btn remove-btn" title="Remove" onClick={() => console.log("Remove clicked", log.id)}>
                                        🗑
                                    </button>
                                </td>
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
    // unchanged

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

function Dashboard({ accessToken, ngrokUrl, baseUrl }) {
    const [sites, setSites] = useState([]);
    const [selectedSite, setSelectedSite] = useState(null);
    const [activeView, setActiveView] = useState('dashboard');
    const [isChatbotOpen, setChatbotOpen] = useState(false);
    const [isSidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);
    const [selectedDevice, setSelectedDevice] = useState(null);

    // Fetch sites on component mount
    useEffect(() => {
        console.log("Dashboard useEffect triggered. Params:", { accessToken, ngrokUrl, baseUrl });
        if (accessToken && ngrokUrl && baseUrl) {
            console.log("Fetching sites from:", `${ngrokUrl}/sites`);
            fetch(`${ngrokUrl}/sites`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_url: baseUrl, access_token: accessToken }),
            })
                .then(res => {
                    console.log("Sites API Response Status:", res.status);
                    if (!res.ok) {
                        throw new Error(`HTTP error! status: ${res.status}`);
                    }
                    return res.json();
                })
                .then(data => {
                    console.log("Sites API Data:", data);
                    if (data && data.result && Array.isArray(data.result.data)) {
                        const sites = data.result.data;
                        setSites(sites);
                        if (sites.length > 0) {
                            // Automatically add the base_url to each site object for later use
                            const siteWithBaseUrl = { ...sites[0], base_url: baseUrl };
                            setSelectedSite(siteWithBaseUrl);
                        }
                    } else {
                        console.warn("Unexpected sites data structure:", data);
                    }
                })
                .catch(err => {
                    console.error("Error fetching sites:", err);
                });
        } else {
            console.warn("Missing required params for fetching sites.");
        }
    }, [accessToken, ngrokUrl, baseUrl]);

    const handleSiteChange = (e) => {
        const siteId = e.target.value;
        const site = sites.find(s => s.siteId === siteId);
        // Add base_url to the selected site object
        const siteWithBaseUrl = { ...site, base_url: baseUrl };
        setSelectedSite(siteWithBaseUrl);
    };

    const handleDeviceSelect = (device) => {
        setSelectedDevice(device);
        setActiveView('device_details');
    };

    const handleBackToDevices = () => {
        setSelectedDevice(null);
        setActiveView('devices');
    };

    const renderActiveView = () => {
        if (!selectedSite && activeView !== 'global_audit_log') {
            return <div className="info-card"><p>Please select a site to view its details.</p></div>;
        }

        switch (activeView) {
            case 'dashboard':
                return <SiteDashboard site={selectedSite} ngrokUrl={ngrokUrl} token={accessToken} />;
            case 'devices':
                return <SiteDevices site={selectedSite} ngrokUrl={ngrokUrl} token={accessToken} onDeviceSelect={handleDeviceSelect} />;
            case 'device_details':
                return <DeviceDetails device={selectedDevice} site={selectedSite} ngrokUrl={ngrokUrl} token={accessToken} onBack={handleBackToDevices} />;
            case 'site_audit_log':
                return <SiteAuditLog site={selectedSite} ngrokUrl={ngrokUrl} token={accessToken} />;
            case 'global_audit_log':
                return <GlobalAuditLog />;
            case 'traffic':
                return <TrafficDashboard site={selectedSite} ngrokUrl={ngrokUrl} token={accessToken} />;
            case 'ai_dashboard':
                return <AIDashboard site={selectedSite} ngrokUrl={ngrokUrl} token={accessToken} />;
            default:
                return <SiteDashboard site={selectedSite} ngrokUrl={ngrokUrl} token={accessToken} />;
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
                            <li className={activeView === 'devices' || activeView === 'device_details' ? 'active' : ''} onClick={() => setActiveView('devices')}>Devices</li>
                            <li className={activeView === 'site_audit_log' ? 'active' : ''} onClick={() => setActiveView('site_audit_log')}>Site Audit Log</li>
                            <li className={activeView === 'traffic' ? 'active' : ''} onClick={() => setActiveView('traffic')}>Traffic</li>
                            <li className={activeView === 'ai_dashboard' ? 'active' : ''} onClick={() => setActiveView('ai_dashboard')}>AI Dashboard</li>
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
            {isChatbotOpen && <button onClick={() => setChatbotOpen(false)} style={{ position: 'fixed', bottom: '570px', right: '40px', zIndex: 1001, background: 'transparent', border: 'none', fontSize: '20px', color: '#2c3e50' }}>X</button>}

        </div>
    );
}

// TrafficDashboard Component
const TrafficDashboard = ({ site, ngrokUrl, token }) => {
    const [trafficData, setTrafficData] = useState({ ap: [], switch: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [devices, setDevices] = useState([]);
    const [selectedAP, setSelectedAP] = useState('');
    const [selectedSwitch, setSelectedSwitch] = useState('');

    // Fetch devices for dropdowns
    useEffect(() => {
        if (site && site.siteId) {
            fetch(`${ngrokUrl}/sites/${site.siteId}/devices`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_url: site.base_url, access_token: token }),
            })
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) {
                        setDevices(data);
                    } else {
                        setDevices([]);
                    }
                })
                .catch(err => console.error("Error fetching devices for dropdown:", err));
        }
    }, [site, ngrokUrl, token]);

    // Fetch traffic data
    useEffect(() => {
        if (site && site.siteId) {
            setLoading(true);
            // default to last hour
            const now = Math.floor(Date.now() / 1000);
            const oneHourAgo = now - 3600;

            const payload = {
                base_url: site.base_url,
                access_token: token,
                start: oneHourAgo,
                end: now
            };
            if (selectedAP) payload.ap_mac = selectedAP;
            if (selectedSwitch) payload.switch_mac = selectedSwitch;

            fetch(`${ngrokUrl}/sites/${site.siteId}/traffic_activities`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
                .then(res => res.json())
                .then(data => {
                    if (data && data.result) {
                        setTrafficData({
                            ap: data.result.apTrafficActivities || [],
                            switch: data.result.switchTrafficActivities || []
                        });
                    } else {
                        setTrafficData({ ap: [], switch: [] });
                    }
                    setLoading(false);
                })
                .catch(err => {
                    console.error('Error fetching traffic:', err);
                    setError('Failed to load traffic data');
                    setLoading(false);
                });
        }
    }, [site, ngrokUrl, token, selectedAP, selectedSwitch]);

    const formatTime = (ts) => new Date(ts * 1000).toLocaleTimeString();

    // Filter devices for dropdowns
    const apDevices = devices.filter(d => d.type === 'ap'); // Assuming 'type' field exists and is 'ap'
    const switchDevices = devices.filter(d => d.type === 'switch'); // Assuming 'type' field exists and is 'switch'

    // Fallback if type is not explicit or different (adjust based on actual device object structure)
    // If 'type' is not available, we might need to rely on other properties or just show all devices
    const aps = apDevices.length > 0 ? apDevices : devices;
    const switches = switchDevices.length > 0 ? switchDevices : devices;

    return (
        <div className="info-card">
            <h3>Traffic for {site?.name}</h3>
            {loading && <p>Loading traffic data...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}

            <div className="traffic-filters" style={{ marginBottom: '15px' }}>
                <label style={{ marginRight: '10px' }}>
                    AP Device:
                    <select value={selectedAP} onChange={e => setSelectedAP(e.target.value)} style={{ marginLeft: '5px' }}>
                        <option value="">All APs</option>
                        {aps.map(d => (
                            <option key={d.mac} value={d.mac}>
                                {d.name || d.mac}
                            </option>
                        ))}
                    </select>
                </label>
                <label>
                    Switch Device:
                    <select value={selectedSwitch} onChange={e => setSelectedSwitch(e.target.value)} style={{ marginLeft: '5px' }}>
                        <option value="">All Switches</option>
                        {switches.map(d => (
                            <option key={d.mac} value={d.mac}>
                                {d.name || d.mac}
                            </option>
                        ))}
                    </select>
                </label>
            </div>

            {!loading && !error && (
                <>
                    <h4>AP Traffic</h4>
                    <LineChart width={600} height={300} data={trafficData.ap.map(item => ({ ...item, timeStr: formatTime(item.time) }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timeStr" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="txData" stroke="#8884d8" name="TX (MB)" />
                        <Line type="monotone" dataKey="rxData" stroke="#82ca9d" name="RX (MB)" />
                    </LineChart>

                    <h4>Switch Traffic</h4>
                    <LineChart width={600} height={300} data={trafficData.switch.map(item => ({ ...item, timeStr: formatTime(item.time) }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timeStr" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="txData" stroke="#ff7300" name="TX (MB)" />
                        <Line type="monotone" dataKey="rxData" stroke="#387908" name="RX (MB)" />
                    </LineChart>

                    <h4>Traffic Data Table</h4>
                    <div className="card">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Device</th>
                                    <th>Time</th>
                                    <th>TX (MB)</th>
                                    <th>RX (MB)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    ...trafficData.ap.map(item => ({ ...item, type: 'AP' })),
                                    ...trafficData.switch.map(item => ({ ...item, type: 'Switch' }))
                                ]
                                    .sort((a, b) => b.time - a.time)
                                    .map((item, index) => (
                                        <tr key={index}>
                                            <td><span className={`status-pill ${item.type === 'AP' ? 'status-active' : 'status-pending'}`}>{item.type}</span></td>
                                            <td>{item.deviceId || item.mac || 'N/A'}</td>
                                            <td>{formatTime(item.time)}</td>
                                            <td>{item.txData}</td>
                                            <td>{item.rxData}</td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>

                    <div style={{ marginTop: '20px' }}>
                        <h5>Raw JSON Response</h5>
                        <pre style={{ background: '#f4f4f4', padding: '10px', borderRadius: '5px', maxHeight: '200px', overflow: 'auto' }}>
                            {JSON.stringify(trafficData, null, 2)}
                        </pre>
                    </div>
                </>
            )}
        </div>
    );
};

export default Dashboard;
