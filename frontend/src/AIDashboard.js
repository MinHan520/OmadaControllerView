import React, { useState, useEffect } from 'react';
import { XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, CartesianGrid } from 'recharts';
import './Dashboard.css'; // Re-use existing styles, but we might add inline styles for specific AI look

const AIDashboard = ({ site, ngrokUrl, token }) => {
    const [healthData, setHealthData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (site && site.siteId && ngrokUrl && token) {
            setLoading(true);
            // Fetch from our new backend endpoint
            fetch(`${ngrokUrl}/sites/${site.siteId}/ai_dashboard`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_url: site.base_url, access_token: token }),
            })
                .then(res => res.json())
                .then(data => {
                    setHealthData(data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("Error fetching AI data:", err);
                    setError("Failed to load AI insights.");
                    setLoading(false);
                });
        }
    }, [site, ngrokUrl, token]);

    if (loading) return <div className="info-card"><p>Analyzing Network Health...</p></div>;
    if (error) return <div className="info-card"><p style={{ color: 'red' }}>{error}</p></div>;
    if (!healthData) return null;

    const { healthScore, healthScoreExplanation, anomalies, predictions, insights } = healthData;

    // Determine color based on score
    const scoreColor = healthScore > 80 ? '#00C853' : healthScore > 50 ? '#FFD600' : '#D50000';

    return (
        <div className="ai-dashboard">
            {/* Top Row: Health Score & Summary */}
            <div className="ai-grid-row">
                <div className="info-card ai-card health-score-card">
                    <h3>Network Health Score</h3>
                    <div className="score-circle" style={{ borderColor: scoreColor, color: scoreColor }}>
                        {healthScore}
                    </div>
                    {/* Floating Chat Container for Explanation */}
                    <div className="score-explanation-tooltip">
                        <div className="tooltip-arrow"></div>
                        <p><strong>Why this score?</strong></p>
                        <p>{healthScoreExplanation || "AI is analyzing the factors..."}</p>
                    </div>
                    <p className="score-label">{healthScore > 80 ? 'Excellent' : healthScore > 50 ? 'Fair' : 'Critical'}</p>
                </div>

                <div className="info-card ai-card insights-card">
                    <h3>AI Insights</h3>
                    <ul>
                        {insights && insights.length > 0 ? (
                            insights.map((insight, idx) => <li key={idx}>{insight}</li>)
                        ) : (
                            <li>No specific insights at this time.</li>
                        )}
                    </ul>
                </div>
            </div>

            {/* Middle Row: Predictive Chart */}
            <div className="info-card ai-card">
                <h3>Predictive Network Load (Next 24h)</h3>
                <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                        <AreaChart data={predictions}>
                            <defs>
                                <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                            <XAxis dataKey="time" stroke="#ccc" />
                            <YAxis stroke="#ccc" />
                            <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none', color: '#fff' }} />
                            <Legend />
                            <Area type="monotone" dataKey="predictedLoad" stroke="#8884d8" fillOpacity={1} fill="url(#colorLoad)" name="Predicted Load (%)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Bottom Row: Anomalies */}
            <div className="info-card ai-card">
                <h3>Detected Anomalies</h3>
                {anomalies && anomalies.length > 0 ? (
                    <table className="devices-table">
                        <thead>
                            <tr>
                                <th>Severity</th>
                                <th>Device/Entity</th>
                                <th>Issue</th>
                                <th>Recommendation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {anomalies.map((anomaly, idx) => (
                                <tr key={idx}>
                                    <td>
                                        <span className={`status-pill ${anomaly.severity === 'High' ? 'status-disconnected' : 'status-pending'}`}>
                                            {anomaly.severity}
                                        </span>
                                    </td>
                                    <td>{anomaly.entity}</td>
                                    <td>{anomaly.issue}</td>
                                    <td>{anomaly.recommendation}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No anomalies detected.</p>
                )}
            </div>

            {/* New Row: Priority Tasks */}
            <div className="info-card ai-card">
                <h3>Recommended Priority Tasks</h3>
                {healthData.priorityTasks && healthData.priorityTasks.length > 0 ? (
                    <div className="priority-tasks-grid">
                        {healthData.priorityTasks.map((task, idx) => (
                            <div key={idx} className="task-card">
                                <div className="task-header">
                                    <span className={`priority-badge ${task.priority.toLowerCase()}`}>{task.priority} Priority</span>
                                    <span className="task-subject">{task.subject}</span>
                                </div>
                                <p className="task-description">{task.task}</p>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p>No immediate priority tasks identified.</p>
                )}
            </div>

            <style>{`
                .priority-tasks-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                    margin-top: 15px;
                }
                .task-card {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 15px;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .task-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .priority-badge {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.8em;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                .priority-badge.high {
                    background-color: rgba(213, 0, 0, 0.2);
                    color: #ff5252;
                    border: 1px solid #ff5252;
                }
                .priority-badge.medium {
                    background-color: rgba(255, 214, 0, 0.2);
                    color: #ffd600;
                    border: 1px solid #ffd600;
                }
                .priority-badge.low {
                    background-color: rgba(0, 200, 83, 0.2);
                    color: #69f0ae;
                    border: 1px solid #69f0ae;
                }
                .task-subject {
                    font-size: 0.8em;
                    opacity: 0.8;
                    font-weight: 500;
                }
                .task-description {
                    font-size: 0.85em;
                    line-height: 1.4;
                }
            `}</style>

            <style>{`
                .ai-dashboard {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                .ai-grid-row {
                    display: grid;
                    grid-template-columns: 1fr 2fr;
                    gap: 20px;
                }
                .ai-card {
                    background: rgba(255, 255, 255, 0.05); /* Glassmorphism attempt if bg is dark */
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .health-score-card {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }
                .score-circle {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    border: 8px solid #00C853;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 3em;
                    font-weight: bold;
                    margin: 20px 0;
                    position: relative; /* For tooltip positioning context if needed, though card has it */
                    cursor: help;
                }
                .health-score-card {
                    position: relative; /* Ensure tooltip is positioned relative to card */
                    overflow: visible; /* Allow tooltip to go outside */
                }
                .score-explanation-tooltip {
                    visibility: hidden;
                    opacity: 0;
                    position: absolute;
                    top: 10px; /* Position near the top-right of the circle or card */
                    right: -220px; /* Push it to the right side */
                    width: 180px; /* Smaller width */
                    background-color: #fff;
                    color: #333;
                    padding: 10px; /* Compact padding */
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                    font-size: 0.8rem; /* Small font size */
                    line-height: 1.3;
                    text-align: left;
                    transition: opacity 0.3s, visibility 0.3s, transform 0.3s;
                    transform: translateY(10px);
                    z-index: 1000; /* Keep on top */
                    pointer-events: none;
                }
                .score-explanation-tooltip::before {
                    content: '';
                    position: absolute;
                    top: 20px;
                    left: -10px;
                    border-width: 10px 10px 10px 0;
                    border-style: solid;
                    border-color: transparent #fff transparent transparent;
                }
                /* Show tooltip on hover over the circle OR the card */
                .health-score-card:hover .score-explanation-tooltip {
                    visibility: visible;
                    opacity: 1;
                    transform: translateY(0);
                }
                /* Dark mode support for tooltip */
                @media (prefers-color-scheme: dark) {
                    .score-explanation-tooltip {
                        background-color: #2c3e50;
                        color: #ecf0f1;
                        border: 1px solid #444;
                    }
                    .score-explanation-tooltip::before {
                        border-color: transparent #2c3e50 transparent transparent;
                    }
                }
                .score-label {
                    font-size: 1.2em;
                    font-weight: 500;
                }
                .insights-card ul {
                    list-style-type: none;
                    padding: 0;
                }
                .insights-card li {
                    background: rgba(0,0,0,0.05);
                    margin-bottom: 10px;
                    padding: 10px;
                    border-left: 4px solid #2196F3;
                    border-radius: 4px;
                }
                /* Dark mode adjustments if parent is dark */
                @media (prefers-color-scheme: dark) {
                    .insights-card li {
                        background: rgba(255,255,255,0.05);
                    }
                }
            `}</style>
        </div>
    );
};

export default AIDashboard;
