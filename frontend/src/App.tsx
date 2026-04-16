import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Performance from './pages/Performance';
import StudyPlan from './pages/StudyPlan';
import type { AgentState } from './types';
import { SparklesIcon } from '@heroicons/react/24/outline';

// Page Transition Wrapper
const PageWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const location = useLocation();
    return (
        <div key={location.pathname} className="min-h-[calc(100vh-40px)] w-full">
            {children}
        </div>
    );
};

// Layout with sidebar (for inner pages)
const AppLayout: React.FC<{ children: React.ReactNode; sessionState: AgentState | null }> = ({ children, sessionState }) => {
    return (
        <div className="flex bg-[#f8fafc] min-h-screen text-slate-800 selection:bg-emerald-500/30">
            {/* Navigation Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="flex-1 ml-64 p-8 min-h-screen relative">
                <div className="max-w-7xl mx-auto">
                    {/* Top Toolbar */}
                    <div className="flex justify-between items-center mb-10">
                        <div className="flex items-center gap-2">
                            <SparklesIcon className="w-5 h-5 text-emerald-500" />
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-[0.2em]">Alpha Access 1.0</span>
                        </div>
                        <div className="flex items-center gap-4">
                            {sessionState && (
                                <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-100/50 rounded-full px-4 py-1.5 shadow-sm">
                                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                    <span className="text-[10px] font-bold text-slate-500 tracking-wider">MASTERED: {Object.values(sessionState.mastery_levels).filter(m => m.status === 'mastered').length}</span>
                                    <div className="w-[1px] h-3 bg-emerald-200" />
                                    <span className="text-[10px] font-bold text-emerald-600 tracking-wider">GLOBAL: {(sessionState.global_mastery_score * 100).toFixed(0)}%</span>
                                </div>
                            )}
                            <button className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 border border-emerald-200 shadow-lg" />
                        </div>
                    </div>

                    {children}
                </div>
            </main>
        </div>
    );
};

const App: React.FC = () => {
    const [sessionState, setSessionState] = useState<AgentState | null>(null);
    const [isInitializing, setIsInitializing] = useState(true);

    // Initialize session or load from local storage
    useEffect(() => {
        const savedState = localStorage.getItem('copilot_session_state');
        if (savedState) {
            try {
                setSessionState(JSON.parse(savedState));
            } catch (e) {
                console.error('Failed to load session state', e);
            }
        }
        setIsInitializing(false);
    }, []);

    const handleStateUpdate = (newState: AgentState) => {
        setSessionState(newState);
        localStorage.setItem('copilot_session_state', JSON.stringify(newState));
    };

    if (isInitializing) {
        return (
            <div className="flex h-screen w-screen items-center justify-center bg-[#f8fafc]">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
                    <p className="text-emerald-800/60 text-xs font-medium uppercase tracking-widest animate-pulse">Initializing EduSaathi...</p>
                </div>
            </div>
        );
    }

    return (
        <Router>
            <Routes>
                {/* Landing page — full width, no sidebar */}
                <Route
                    path="/"
                    element={
                        <PageWrapper>
                            <Landing />
                        </PageWrapper>
                    }
                />

                {/* Inner pages — with sidebar layout */}
                <Route
                    path="/dashboard"
                    element={
                        <AppLayout sessionState={sessionState}>
                            <PageWrapper>
                                <Dashboard state={sessionState} />
                            </PageWrapper>
                        </AppLayout>
                    }
                />
                <Route
                    path="/chat"
                    element={
                        <AppLayout sessionState={sessionState}>
                            <PageWrapper>
                                <Chat onStateUpdate={handleStateUpdate} />
                            </PageWrapper>
                        </AppLayout>
                    }
                />
                <Route
                    path="/analytics"
                    element={
                        <AppLayout sessionState={sessionState}>
                            <PageWrapper>
                                <Performance state={sessionState} />
                            </PageWrapper>
                        </AppLayout>
                    }
                />
                <Route
                    path="/plan"
                    element={
                        <AppLayout sessionState={sessionState}>
                            <PageWrapper>
                                <StudyPlan state={sessionState} />
                            </PageWrapper>
                        </AppLayout>
                    }
                />
            </Routes>
        </Router>
    );
};

export default App;
