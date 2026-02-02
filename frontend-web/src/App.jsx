import React, { useState, useEffect } from 'react';
import Upload from './Upload';
import Dashboard from './Dashboard';
import api, { setAuthToken } from './api';
import { motion, AnimatePresence } from 'framer-motion';
import { BeakerIcon } from '@heroicons/react/24/outline';

/**
 * Root Application component for FlowDrishti Pro.
 * 
 * Manages:
 * - Authentication state and session persistence via localStorage.
 * - Navigation between Dashboard and Upload views.
 * - Global dataset state for real-time visualization.
 */
function App() {
    const [user, setUser] = useState(null);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [activeTab, setActiveTab] = useState('dashboard');
    const [currentUpload, setCurrentUpload] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Persistence: Restore session on mount
    useEffect(() => {
        const savedUser = localStorage.getItem('flowdrishti_user');
        const savedToken = localStorage.getItem('flowdrishti_token');
        if (savedUser && savedToken) {
            setUser(savedUser);
            // api.js handles setting the default header on import if token exists in localStorage
        }
    }, []);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Attempt real login
            const response = await api.post('auth/login/', { username, password });
            const { token, user } = response.data;

            setAuthToken(token); // Set token header and save to localStorage
            setUser(user.username);
            localStorage.setItem('flowdrishti_user', user.username);
            setActiveTab('dashboard');
        } catch (err) {
            console.error("Login failed", err);
            setError("Invalid username or password");
        } finally {
            setLoading(false);
        }
    };

    const onUploadSuccess = (data) => {
        setCurrentUpload(data);
        setActiveTab('dashboard');
    };

    const handleLogout = () => {
        setUser(null);
        setCurrentUpload(null);
        setAuthToken(null); // Clears header and localStorage
        localStorage.removeItem('flowdrishti_user');
        setActiveTab('dashboard');
    };

    if (!user) {
        return (
            <div className="min-h-screen flex bg-slate-50 text-slate-900 overflow-hidden">
                {/* Left Side - Visual */}
                <div className="hidden lg:flex w-1/2 relative overflow-hidden bg-white">
                    <div className="absolute inset-0 z-10 bg-gradient-to-br from-blue-600/10 to-purple-600/10 mix-blend-multiply" />
                    <motion.div
                        animate={{ scale: [1, 1.05, 1], rotate: [0, 1, -1, 0] }}
                        transition={{ duration: 20, repeat: Infinity }}
                        className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1532094349884-543bc11b234d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80')] bg-cover bg-center opacity-80"
                    />
                    <div className="relative z-20 flex flex-col justify-end p-16 pb-32 w-full bg-gradient-to-t from-white via-white/80 to-transparent">
                        <motion.h1
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="text-6xl font-black font-sans mb-4 tracking-tight text-slate-900"
                        >
                            Future of <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                                Chemical Analytics
                            </span>
                        </motion.h1>
                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 }}
                            className="text-xl text-slate-600 max-w-lg"
                        >
                            Advanced visualization, real-time simulation, and predictive health monitoring for industrial equipment.
                        </motion.p>
                    </div>
                </div>

                {/* Right Side - Login */}
                <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
                    <div className="absolute inset-0 overflow-hidden pointer-events-none">
                        <div className="absolute -top-[20%] -right-[10%] w-[600px] h-[600px] bg-blue-100 rounded-full blur-[120px]" />
                        <div className="absolute top-[40%] left-[10%] w-[400px] h-[400px] bg-purple-100 rounded-full blur-[100px]" />
                    </div>

                    <div className="w-full max-w-md relative z-10">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex items-center space-x-3 mb-12"
                        >
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-xl shadow-blue-500/20">
                                <BeakerIcon className="w-7 h-7 text-white" />
                            </div>
                            <span className="text-2xl font-bold tracking-tight text-slate-900">FlowDrishti Pro</span>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                        >
                            <h2 className="text-3xl font-bold mb-2 text-slate-900">Welcome Back</h2>
                            <p className="text-slate-500 mb-8">Enter your credentials to access the command center.</p>

                            <form onSubmit={handleLogin} className="space-y-5">
                                <div className="space-y-1">
                                    <label className="text-sm font-medium text-slate-700 ml-1">Username</label>
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={e => setUsername(e.target.value)}
                                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
                                        placeholder="admin"
                                    />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-sm font-medium text-slate-700 ml-1">Password</label>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={e => setPassword(e.target.value)}
                                        className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
                                        placeholder="••••••••"
                                    />
                                </div>

                                <button
                                    disabled={loading}
                                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-600/20 transform transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed mt-4"
                                >
                                    {loading ? (
                                        <div className="flex items-center justify-center space-x-2">
                                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            <span>Authenticating...</span>
                                        </div>
                                    ) : "Sign In to Dashboard"}
                                </button>
                            </form>
                        </motion.div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden font-sans">
            {/* Main Layout passing props */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                <nav className="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-8 shrink-0 z-50 sticky top-0">
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20">
                            <BeakerIcon className="w-5 h-5 text-white" />
                        </div>
                        <span className="font-bold text-lg tracking-tight text-slate-900">FlowDrishti <span className="text-blue-600 font-light">Pro</span></span>
                    </div>
                    <div className="flex items-center space-x-6">
                        <div className="text-sm text-slate-500">
                            Logged in as <span className="text-slate-900 font-semibold">{user}</span>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors"
                        >
                            Sign Out
                        </button>
                    </div>
                </nav>

                <main className="flex-1 overflow-hidden relative bg-slate-50">
                    <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute top-0 left-1/4 w-[1000px] h-[500px] bg-blue-100/50 rounded-full blur-[120px]" />
                    </div>

                    <div className="h-full overflow-y-auto scrollbar-hide relative z-10">
                        <div className="max-w-7xl mx-auto p-8 pb-32">
                            <AnimatePresence mode="wait">
                                {activeTab === 'dashboard' ? (
                                    <Dashboard
                                        key="dashboard"
                                        uploadData={currentUpload}
                                        onReqUpload={() => setActiveTab('upload')}
                                    />
                                ) : (
                                    <motion.div
                                        key="upload"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -20 }}
                                    >
                                        <div className='flex justify-between items-center mb-8'>
                                            <h2 className="text-3xl font-bold text-slate-900">Upload Data</h2>
                                            <button
                                                onClick={() => setActiveTab('dashboard')}
                                                className="text-sm text-slate-500 hover:text-blue-600"
                                            >
                                                &larr; Back to Dashboard
                                            </button>
                                        </div>
                                        <Upload onUploadSuccess={onUploadSuccess} />
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

export default App;
