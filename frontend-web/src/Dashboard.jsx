import React, { useState, useEffect } from 'react';
import {
    Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement, RadialLinearScale, ArcElement, Filler
} from 'chart.js';
import { Bar, Line, Radar, Scatter, Doughnut } from 'react-chartjs-2';
import api from './api';
import { motion } from 'framer-motion';
import {
    ArrowDownTrayIcon, ClockIcon, BeakerIcon, FireIcon, BoltIcon, ScaleIcon, ChartBarIcon, CpuChipIcon, ListBulletIcon, ArrowPathIcon, TrashIcon
} from '@heroicons/react/24/outline';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, RadialLinearScale, ArcElement, Filler);

/**
 * Dashboard component serving as the central hub for data visualization.
 * Integrates Chart.js for real-time and historical telemetry analysis.
 * 
 * @param {Object} props
 * @param {Object} props.uploadData - The currently active dataset object.
 * @param {Function} props.onReqUpload - Callback to switch back to the upload view.
 */
const Dashboard = ({ uploadData, onReqUpload }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [history, setHistory] = useState([]);
    const [realtimeData, setRealtimeData] = useState([]);
    const [isSimulating, setIsSimulating] = useState(true);

    useEffect(() => {
        fetchHistory();
    }, [uploadData]);

    const [playbackIndex, setPlaybackIndex] = useState(0);

    // Reset simulation when new data is uploaded
    useEffect(() => {
        if (uploadData) {
            setRealtimeData([]);
            setPlaybackIndex(0);
        }
    }, [uploadData]);

    // Real-time Simulation Effect (Playback Mode)
    useEffect(() => {
        if (activeTab === 'realtime' && isSimulating) {
            const interval = setInterval(() => {
                setRealtimeData(prev => {
                    const now = new Date();
                    let newPoint;

                    if (uploadData && uploadData.equipment_data && uploadData.equipment_data.length > 0) {
                        // Use uploaded data
                        const dataItem = uploadData.equipment_data[playbackIndex % uploadData.equipment_data.length];
                        newPoint = {
                            time: now.toLocaleTimeString(),
                            flow: dataItem.flowrate,
                            pressure: dataItem.pressure,
                            temp: dataItem.temperature,
                            name: dataItem.name // Optional: track which equipment
                        };
                        setPlaybackIndex(idx => idx + 1);
                    } else {
                        // Fallback Random Simulation
                        newPoint = {
                            time: now.toLocaleTimeString(),
                            flow: 45 + Math.random() * 10,
                            pressure: 8 + Math.random() * 4,
                            temp: 58 + Math.random() * 5
                        };
                    }

                    const newData = [...prev, newPoint];
                    if (newData.length > 20) newData.shift(); // Keep last 20 points
                    return newData;
                });
            }, 1000); // Update every second
            return () => clearInterval(interval);
        }
    }, [activeTab, isSimulating, uploadData, playbackIndex]);

    const fetchHistory = async () => {
        try {
            const res = await api.get('datasets/history/');
            setHistory(res.data);
        } catch (err) {
            console.error("Failed to fetch history");
        }
    };

    const handleDeleteDataset = async (id) => {
        if (!window.confirm(`Are you sure you want to delete dataset #${id}? This action cannot be undone.`)) {
            return;
        }
        try {
            await api.delete(`datasets/${id}/`);
            fetchHistory();
        } catch (err) {
            console.error("Failed to delete dataset", err);
            alert("Failed to delete dataset. Please try again.");
        }
    };

    const handleDownloadReport = async (id) => {
        try {
            const response = await api.get(`reports/${id}/pdf/`, {
                responseType: 'blob',
                headers: {
                    'Accept': 'application/pdf'
                }
            });

            // Check if it's actually an error message (small JSON blob instead of PDF)
            if (response.data.type === 'application/json' || response.data.size < 500) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errObj = JSON.parse(reader.result);
                        alert(`Report Error: ${errObj.error || "Generation failed on server."}`);
                    } catch (e) {
                        // If it's not JSON, it might just be a very small PDF or a different error
                        const url = window.URL.createObjectURL(response.data);
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', `Analysis_Report_#${id}.pdf`);
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        window.URL.revokeObjectURL(url);
                    }
                };
                reader.readAsText(response.data);
                return;
            }

            // Create a blob from the response data
            const url = window.URL.createObjectURL(response.data);

            // Create a temporary link element and click it
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Analysis_Report_#${id}.pdf`);
            document.body.appendChild(link);
            link.click();

            // Clean up with a small delay for older browsers
            setTimeout(() => {
                if (link.parentNode) document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            }, 200);
        } catch (err) {
            console.error("Failed to download PDF", err);
            let msg = "Failed to download report.";
            if (err.response) {
                msg += ` (Server Status: ${err.response.status})`;
            }
            alert(msg);
        }
    }

    if (!uploadData && activeTab !== 'history') {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6">
                <div className="bg-white p-6 rounded-full shadow-xl shadow-blue-100 ring-4 ring-blue-50/50">
                    <ClockIcon className="h-12 w-12 text-blue-600" />
                </div>
                <div>
                    <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">No Active Analysis</h3>
                    <p className="text-slate-500 mt-2 max-w-md">Select a recent upload from the history tab or upload new data to begin analysis.</p>
                </div>
                <div className="flex space-x-4">
                    <button onClick={onReqUpload} className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl shadow-lg shadow-blue-600/20 font-medium transition-all transform hover:-translate-y-1">
                        Upload New Data
                    </button>
                    <button onClick={() => setActiveTab('history')} className="bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-8 py-3 rounded-xl font-medium transition-all shadow-sm">
                        View History
                    </button>
                </div>
            </div>
        )
    }

    const renderContent = () => {
        switch (activeTab) {
            case 'overview':
                return <OverviewTab data={uploadData} onDownload={handleDownloadReport} />;
            case 'analytics':
                return <AnalyticsTab data={uploadData} />;
            case 'comparison':
                return <ComparisonTab history={history} />;
            case 'history':
                return <HistoryTab history={history} onDownload={handleDownloadReport} onDelete={handleDeleteDataset} />;
            default:
                return <OverviewTab data={uploadData} onDownload={handleDownloadReport} />;
        }
    };

    return (
        <div className="space-y-8">
            {/* Tabs */}
            <div className="flex justify-center">
                <div className="bg-white p-1 rounded-xl flex space-x-1 shadow-sm border border-slate-200">
                    {[
                        { id: 'overview', icon: ChartBarIcon, label: 'Overview' },
                        { id: 'analytics', icon: BeakerIcon, label: 'Analytics' },
                        { id: 'comparison', icon: ArrowPathIcon, label: 'Trends & Compare' },
                        { id: 'history', icon: ListBulletIcon, label: 'History' },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center space-x-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                                ? 'bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-200'
                                : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                                }`}
                        >
                            <tab.icon className="w-4 h-4" />
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </div>
            </div>

            <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
            >
                {renderContent()}
            </motion.div>
        </div>
    );
};

const OverviewTab = ({ data, onDownload }) => {
    if (!data) return null;
    const {
        equipment_data,
        total_equipment,
        avg_flowrate,
        avg_pressure,
        avg_health_score,
        equipment_type_distribution
    } = data;

    const [isDownloading, setIsDownloading] = useState(false);

    const handleDownloadClick = async () => {
        setIsDownloading(true);
        await onDownload(data.id);
        setIsDownloading(false);
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                <div>
                    <h2 className="text-xl font-bold text-slate-800">System Overview</h2>
                    <p className="text-slate-500 text-sm">Real-time analysis of uploaded telemetry data.</p>
                </div>
                <button
                    onClick={handleDownloadClick}
                    disabled={isDownloading}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg font-medium transition-colors shadow-md shadow-blue-600/20"
                >
                    {isDownloading ? (
                        <ArrowPathIcon className="h-5 w-5 animate-spin" />
                    ) : (
                        <ArrowDownTrayIcon className="h-5 w-5" />
                    )}
                    {isDownloading ? 'Generating Report...' : 'Download Detailed Report'}
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <StatsCard title="Equipment Count" value={total_equipment} icon={BeakerIcon} color="blue" />
                <StatsCard title="Avg Flowrate" value={avg_flowrate?.toFixed(1) || 0} unit="L/min" icon={BoltIcon} color="cyan" />
                <StatsCard title="Avg Pressure" value={avg_pressure?.toFixed(1) || 0} unit="Bar" icon={ScaleIcon} color="purple" />
                <StatsCard title="System Health" value={(avg_health_score || 85).toFixed(0) + '%'} icon={FireIcon} color={avg_health_score < 70 ? "red" : "emerald"} />

                <div className="col-span-1 lg:col-span-1 glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 text-slate-800">Equipment Types</h3>
                    <div className="h-80 flex justify-center relative">
                        <Doughnut
                            data={{
                                labels: Object.keys(equipment_type_distribution || {}),
                                datasets: [{
                                    data: Object.values(equipment_type_distribution || {}),
                                    backgroundColor: [
                                        'rgba(59, 130, 246, 0.8)',
                                        'rgba(168, 85, 247, 0.8)',
                                        'rgba(236, 72, 153, 0.8)',
                                        'rgba(34, 197, 94, 0.8)',
                                        'rgba(245, 158, 11, 0.8)',
                                        'rgba(99, 102, 241, 0.8)',
                                    ],
                                    borderWidth: 0,
                                }]
                            }}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                cutout: '75%',
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                        labels: {
                                            boxWidth: 8,
                                            usePointStyle: true,
                                            padding: 15,
                                            font: { size: 11 }
                                        }
                                    }
                                }
                            }}
                        />
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none mb-10">
                            <div className="text-center">
                                <span className="text-4xl font-bold text-slate-800 block">{total_equipment}</span>
                                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Units</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="col-span-1 lg:col-span-3 glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 text-slate-800">Critical Equipment Watchlist (Low Health)</h3>
                    <div className="h-64">
                        <Bar
                            data={{
                                labels: equipment_data
                                    .sort((a, b) => a.health_score - b.health_score)
                                    .slice(0, 5)
                                    .map(e => e.name),
                                datasets: [{
                                    label: 'Health Score',
                                    data: equipment_data
                                        .sort((a, b) => a.health_score - b.health_score)
                                        .slice(0, 5)
                                        .map(e => e.health_score),
                                    backgroundColor: equipment_data
                                        .sort((a, b) => a.health_score - b.health_score)
                                        .slice(0, 5)
                                        .map(e => e.health_score < 50 ? 'rgba(239, 68, 68, 0.7)' : 'rgba(245, 158, 11, 0.7)'),
                                    borderRadius: 4,
                                    barThickness: 20,
                                }]
                            }}
                            options={{
                                indexAxis: 'y',
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: {
                                    x: { min: 0, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
                                    y: { grid: { display: false } }
                                }
                            }}
                        />
                    </div>
                </div>

                <div className="col-span-1 lg:col-span-4 glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 text-slate-800">Pressure vs Flow Overview</h3>
                    <div className="h-64">
                        <Line
                            data={{
                                labels: equipment_data.slice(0, 20).map(e => e.name),
                                datasets: [
                                    {
                                        label: 'Pressure (Bar)',
                                        data: equipment_data.slice(0, 20).map(e => e.pressure),
                                        borderColor: 'rgb(168, 85, 247)',
                                        borderWidth: 2,
                                        tension: 0.4,
                                        pointRadius: 2,
                                        yAxisID: 'y'
                                    },
                                    {
                                        label: 'Flow (L/min)',
                                        data: equipment_data.slice(0, 20).map(e => e.flowrate),
                                        borderColor: 'rgb(6, 182, 212)',
                                        borderWidth: 2,
                                        tension: 0.4,
                                        pointRadius: 2,
                                        yAxisID: 'y1'
                                    }
                                ]
                            }}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                interaction: { mode: 'index', intersect: false },
                                scales: {
                                    y: { type: 'linear', display: true, position: 'left', grid: { color: 'rgba(0,0,0,0.05)' } },
                                    y1: { type: 'linear', display: true, position: 'right', grid: { display: false } },
                                    x: { grid: { display: false }, ticks: { maxRotation: 45, minRotation: 45 } }
                                }
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    )
}

const AnalyticsTab = ({ data }) => {
    if (!data) return null;
    const { equipment_data } = data;

    // Scatter data: Flowrate vs Pressure
    const scatterData = {
        datasets: [{
            label: 'Equipment Performance',
            data: equipment_data.map(e => ({ x: e.flowrate, y: e.pressure })),
            backgroundColor: 'rgba(6, 182, 212, 0.6)',
        }]
    };

    // Radar Data mock (taking avg of first 5 items)
    const radarData = {
        labels: ['Flowrate', 'Pressure', 'Temp', 'Health', 'Utilization', 'Efficiency'],
        datasets: [{
            label: 'System Average',
            data: [
                65, 59, 90, 81, 56, 55
            ],
            backgroundColor: 'rgba(168, 85, 247, 0.2)',
            borderColor: 'rgba(168, 85, 247, 1)',
            borderWidth: 2,
        }]
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6">
                <h3 className="text-lg font-bold mb-4 text-slate-800">Performance Correlation (Scatter)</h3>
                <div className="h-80">
                    <Scatter
                        data={scatterData}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                x: { title: { display: true, text: 'Flowrate' }, grid: { color: 'rgba(0,0,0,0.05)' } },
                                y: { title: { display: true, text: 'Pressure' }, grid: { color: 'rgba(0,0,0,0.05)' } }
                            }
                        }}
                    />
                </div>
            </div>
            <div className="glass-card p-6">
                <h3 className="text-lg font-bold mb-4 text-slate-800">System Health Metrics (Radar)</h3>
                <div className="h-80 flex justify-center">
                    <Radar
                        data={radarData}
                        options={{
                            scales: {
                                r: {
                                    angleLines: { color: 'rgba(0,0,0,0.1)' },
                                    grid: { color: 'rgba(0,0,0,0.05)' },
                                    pointLabels: { color: '#475569' }, // slate-600
                                    ticks: { backdropColor: 'transparent', color: 'transparent' }
                                }
                            }
                        }}
                    />
                </div>
            </div>
        </div>
    )
}

const ComparisonTab = ({ history }) => {
    if (!history || history.length === 0) return (
        <div className="glass-card p-8 text-center">
            <p className="text-slate-500">No history data available for comparison. Upload more datasets to see trends.</p>
        </div>
    );

    // Sort history by date ascending for charts
    const sortedHistory = [...history].sort((a, b) => new Date(a.uploaded_at) - new Date(b.uploaded_at));
    const labels = sortedHistory.map(h => new Date(h.uploaded_at).toLocaleDateString());

    return (
        <div className="space-y-6">
            <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm">
                <h3 className="text-xl font-bold text-slate-800">Historical Trends & Comparison</h3>
                <p className="text-slate-500 text-sm">Analyzing performance changes across {history.length} uploads.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 text-slate-800">Health Score Trend</h3>
                    <div className="h-72">
                        <Line
                            data={{
                                labels,
                                datasets: [{
                                    label: 'Avg Health Score (%)',
                                    data: sortedHistory.map(h => h.avg_health_score),
                                    borderColor: 'rgb(34, 197, 94)',
                                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                                    fill: true,
                                    tension: 0.4
                                }]
                            }}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: { min: 0, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
                                    x: { grid: { display: false } }
                                }
                            }}
                        />
                    </div>
                </div>

                <div className="glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 text-slate-800">Parameter Variance</h3>
                    <div className="h-72">
                        <Line
                            data={{
                                labels,
                                datasets: [
                                    {
                                        label: 'Avg Flow (L/min)',
                                        data: sortedHistory.map(h => h.avg_flowrate),
                                        borderColor: 'rgb(59, 130, 246)',
                                        tension: 0.4,
                                        yAxisID: 'y'
                                    },
                                    {
                                        label: 'Avg Pressure (Bar)',
                                        data: sortedHistory.map(h => h.avg_pressure),
                                        borderColor: 'rgb(168, 85, 247)',
                                        tension: 0.4,
                                        yAxisID: 'y1'
                                    }
                                ]
                            }}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                interaction: { mode: 'index', intersect: false },
                                scales: {
                                    y: { type: 'linear', display: true, position: 'left', grid: { color: 'rgba(0,0,0,0.05)' } },
                                    y1: { type: 'linear', display: true, position: 'right', grid: { display: false } },
                                    x: { grid: { display: false } }
                                }
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    )
}

const HistoryTab = ({ history, onDownload, onDelete }) => {
    return (
        <div className="glass-card overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
                <h3 className="font-bold text-slate-800">Upload History</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-500">
                    <thead className="bg-slate-50 uppercase font-medium text-xs text-slate-400">
                        <tr>
                            <th className="px-6 py-4">ID</th>
                            <th className="px-6 py-4">Date</th>
                            <th className="px-6 py-4">Items</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {history.map((h) => (
                            <tr key={h.id} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 font-mono text-slate-700">#{h.id}</td>
                                <td className="px-6 py-4">{new Date(h.uploaded_at).toLocaleString()}</td>
                                <td className="px-6 py-4">{h.total_equipment}</td>
                                <td className="px-6 py-4 text-right">
                                    <div className="flex items-center justify-end gap-3">
                                        <button onClick={() => onDownload(h.id)} className="text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium">
                                            <ArrowDownTrayIcon className="h-4 w-4" />
                                            <span>Report</span>
                                        </button>
                                        <button onClick={() => onDelete(h.id)} className="text-red-500 hover:text-red-700 flex items-center gap-1 font-medium">
                                            <TrashIcon className="h-4 w-4" />
                                            <span>Delete</span>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

const StatsCard = ({ title, value, unit, icon: Icon, color }) => {
    const colors = {
        blue: "text-blue-600 bg-blue-50",
        cyan: "text-cyan-600 bg-cyan-50",
        purple: "text-purple-600 bg-purple-50",
        emerald: "text-emerald-600 bg-emerald-50",
        red: "text-red-600 bg-red-50",
    }
    return (
        <div className="glass-card p-6 flex items-center space-x-4">
            <div className={`p-3 rounded-xl ${colors[color] || colors.blue}`}>
                <Icon className="h-6 w-6" />
            </div>
            <div>
                <p className="text-slate-500 text-sm font-medium">{title}</p>
                <div className="flex items-baseline space-x-1">
                    <p className="text-2xl font-bold text-slate-800">{value}</p>
                    {unit && <span className="text-xs text-slate-400 font-medium uppercase">{unit}</span>}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
