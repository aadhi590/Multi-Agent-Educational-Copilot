import React from 'react';
import type { AgentState } from '../types';
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area,
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    BarChart,
    Bar,
    Cell,
} from 'recharts';
import {
    BeakerIcon,
    FireIcon,
    ArrowTrendingUpIcon,
    ShieldCheckIcon,
    AcademicCapIcon,
    SparklesIcon,
} from '@heroicons/react/24/outline';

interface PerformanceProps {
    state: AgentState | null;
}

// ─── Demo data ───
const DEMO_STATE: AgentState = {
    frustration_level: 0.15,
    engagement_score: 0.87,
    sentiment: 'positive',
    global_mastery_score: 0.68,
    mastery_levels: {
        'Binary Search Trees': { score: 0.85, elo_score: 1420, bkt_score: 0.82, attempts: 8, status: 'mastered', learning_velocity: 0.12, learning_objectives_met: ['Insertion', 'Traversal', 'Deletion'] },
        'Sorting Algorithms': { score: 0.72, elo_score: 1350, bkt_score: 0.70, attempts: 6, status: 'in_progress', learning_velocity: 0.08, learning_objectives_met: ['Bubble Sort', 'Quick Sort'] },
        'Graph Traversal': { score: 0.55, elo_score: 1280, bkt_score: 0.50, attempts: 4, status: 'in_progress', learning_velocity: 0.05, learning_objectives_met: ['BFS'] },
        'Dynamic Programming': { score: 0.30, elo_score: 1200, bkt_score: 0.28, attempts: 2, status: 'in_progress', learning_velocity: -0.02, learning_objectives_met: [] },
        'Recursion': { score: 0.90, elo_score: 1480, bkt_score: 0.88, attempts: 10, status: 'mastered', learning_velocity: 0.15, learning_objectives_met: ['Base Case', 'Recursive Case', 'Stack Frames'] },
    },
    current_topic: 'Graph Traversal',
    session_id: 'demo-session',
    remaining_objectives: ['DFS', 'Dijkstra', 'Topological Sort'],
    learning_objectives: ['BFS', 'DFS', 'Dijkstra', 'Topological Sort', 'MST'],
    syllabus: [],
    evaluation_history: [
        { score: 4, passed: false, topic: 'Recursion', feedback_summary: 'Early attempt — struggling with base cases.', misconceptions: ['Infinite recursion'], tool_verified: true },
        { score: 6, passed: true, topic: 'Recursion', feedback_summary: 'Improving! Base case identified correctly.', misconceptions: [], tool_verified: true },
        { score: 7, passed: true, topic: 'Binary Search Trees', feedback_summary: 'Good BST insertion understanding.', misconceptions: ['Left vs right child'], tool_verified: true },
        { score: 8, passed: true, topic: 'Sorting Algorithms', feedback_summary: 'Strong comparison sort knowledge.', misconceptions: [], tool_verified: true },
        { score: 5, passed: false, topic: 'Dynamic Programming', feedback_summary: 'Memoization concept needs work.', misconceptions: ['Overlapping subproblems'], tool_verified: true },
        { score: 9, passed: true, topic: 'Recursion', feedback_summary: 'Excellent recursive thinking!', misconceptions: [], tool_verified: true },
        { score: 6, passed: true, topic: 'Graph Traversal', feedback_summary: 'BFS understood. DFS needs practice.', misconceptions: ['DFS backtracking'], tool_verified: true },
        { score: 8, passed: true, topic: 'Binary Search Trees', feedback_summary: 'Strong BST operations.', misconceptions: [], tool_verified: true },
        { score: 7, passed: true, topic: 'Sorting Algorithms', feedback_summary: 'Quick sort partitioning mastered.', misconceptions: [], tool_verified: true },
        { score: 9, passed: true, topic: 'Recursion', feedback_summary: 'Master-level recursive problem solving.', misconceptions: [], tool_verified: true },
    ],
    last_evaluation_result: { score: 6, passed: true, topic: 'Graph Traversal', feedback_summary: 'BFS understood. DFS needs practice.', misconceptions: ['DFS backtracking'], tool_verified: true },
};



const Performance: React.FC<PerformanceProps> = ({ state: liveState }) => {
    const state = liveState || DEMO_STATE;
    const isDemo = !liveState;

    // Line chart data
    const lineData = state.evaluation_history.map((h, i) => ({
        turn: `Turn ${i + 1}`,
        score: h.score,
        topic: h.topic
    }));

    // Radar chart data
    const radarData = Object.entries(state.mastery_levels).map(([topic, data]) => ({
        subject: topic.length > 15 ? topic.substring(0, 15) + '…' : topic,
        mastery: data.score * 100,
        bkt: data.bkt_score * 100,
        fullMark: 100,
    }));

    // ELO bar chart data
    const eloData = Object.entries(state.mastery_levels).map(([topic, data]) => ({
        name: topic.length > 12 ? topic.substring(0, 12) + '…' : topic,
        elo: data.elo_score,
        fullName: topic,
    }));

    // Stats
    const avgScore = state.evaluation_history.length > 0
        ? (state.evaluation_history.reduce((sum, e) => sum + e.score, 0) / state.evaluation_history.length).toFixed(1)
        : '0';
    const passRate = state.evaluation_history.length > 0
        ? Math.round((state.evaluation_history.filter(e => e.passed).length / state.evaluation_history.length) * 100)
        : 0;
    const topTopic = Object.entries(state.mastery_levels).sort((a, b) => b[1].score - a[1].score)[0];
    const weakTopic = Object.entries(state.mastery_levels).sort((a, b) => a[1].score - b[1].score)[0];

    return (
        <div className="space-y-8 animate-fade-in px-4 pb-12">
            {/* Header */}
            <header className="flex items-start justify-between">
                <div>
                    <h2 className="text-3xl font-extrabold text-slate-800 mb-1">Performance Analytics</h2>
                    <p className="text-slate-500">In-depth analysis of your cognitive progression and mastery velocity.</p>
                </div>
                {isDemo && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-700">
                        <SparklesIcon className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Demo Data</span>
                    </div>
                )}
            </header>

            {/* Quick Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass-card p-5 hover-lift">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Avg Score</p>
                    <p className="text-3xl font-extrabold text-slate-800">{avgScore}</p>
                    <p className="text-[10px] text-slate-400 mt-1">out of 10</p>
                </div>
                <div className="glass-card p-5 hover-lift">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Pass Rate</p>
                    <p className="text-3xl font-extrabold text-emerald-600">{passRate}%</p>
                    <p className="text-[10px] text-slate-400 mt-1">{state.evaluation_history.filter(e => e.passed).length}/{state.evaluation_history.length} passed</p>
                </div>
                <div className="glass-card p-5 hover-lift">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Top Domain</p>
                    <p className="text-lg font-extrabold text-slate-800 truncate">{topTopic?.[0] || '—'}</p>
                    <p className="text-[10px] text-emerald-500 mt-1 font-bold">{topTopic ? `${(topTopic[1].score * 100).toFixed(0)}% mastery` : ''}</p>
                </div>
                <div className="glass-card p-5 hover-lift">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Needs Work</p>
                    <p className="text-lg font-extrabold text-slate-800 truncate">{weakTopic?.[0] || '—'}</p>
                    <p className="text-[10px] text-rose-500 mt-1 font-bold">{weakTopic ? `${(weakTopic[1].score * 100).toFixed(0)}% mastery` : ''}</p>
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Progress Over Time */}
                <div className="glass-card p-8 min-h-[420px] hover-lift">
                    <h3 className="text-lg font-bold text-slate-800 mb-8 flex items-center gap-2">
                        <BeakerIcon className="w-5 h-5 text-emerald-500" />
                        Learning Progression
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={lineData}>
                                <defs>
                                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(16,185,129,0.1)" vertical={false} />
                                <XAxis dataKey="turn" stroke="rgba(30,41,59,0.4)" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="rgba(30,41,59,0.4)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 10]} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', fontSize: '12px' }}
                                />
                                <Area type="monotone" dataKey="score" stroke="#10b981" fillOpacity={1} fill="url(#colorScore)" strokeWidth={3} dot={{ r: 4, fill: '#10b981', stroke: '#fff', strokeWidth: 2 }} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Cognitive Radar */}
                <div className="glass-card p-8 min-h-[420px] flex flex-col hover-lift">
                    <h3 className="text-lg font-bold text-slate-800 mb-8 flex items-center gap-2">
                        <FireIcon className="w-5 h-5 text-amber-500" />
                        Subject Mastery Radar
                    </h3>
                    {radarData.length > 0 ? (
                        <div className="h-[300px] w-full flex-1">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart data={radarData}>
                                    <PolarGrid stroke="rgba(16,185,129,0.2)" />
                                    <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(30,41,59,0.7)', fontSize: 10 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} axisLine={false} tick={false} />
                                    <Radar name="Mastery %" dataKey="mastery" stroke="#10b981" fill="#10b981" fillOpacity={0.3} strokeWidth={2} />
                                    <Radar name="BKT Score %" dataKey="bkt" stroke="#6366f1" fill="#6366f1" fillOpacity={0.1} strokeWidth={2} strokeDasharray="4 4" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', fontSize: '12px' }}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-slate-400 italic">No mastery data recorded.</div>
                    )}
                </div>
            </div>

            {/* ELO Rating Bar Chart */}
            <div className="glass-card p-8 hover-lift">
                <h3 className="text-lg font-bold text-slate-800 mb-8 flex items-center gap-2">
                    <ArrowTrendingUpIcon className="w-5 h-5 text-blue-500" />
                    ELO Rating by Domain
                </h3>
                <div className="h-[250px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={eloData} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(16,185,129,0.1)" horizontal={false} />
                            <XAxis type="number" domain={[1100, 1600]} stroke="rgba(30,41,59,0.4)" fontSize={10} tickLine={false} />
                            <YAxis type="category" dataKey="name" stroke="rgba(30,41,59,0.4)" fontSize={11} tickLine={false} axisLine={false} width={120} />
                            <Tooltip
                                contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', fontSize: '12px' }}
                                formatter={(value: number | undefined) => [`ELO: ${value ?? 0}`, 'Rating']}
                            />
                            <Bar dataKey="elo" radius={[0, 8, 8, 0]} barSize={24}>
                                {eloData.map((_, i) => (
                                    <Cell key={i} fill={`hsl(${160 + i * 20}, 70%, ${45 + i * 5}%)`} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Mastery Detail Table */}
            <div className="glass-card p-8 overflow-x-auto hover-lift">
                <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <AcademicCapIcon className="w-5 h-5 text-emerald-500" />
                    Mastery Detail View
                </h3>
                <table className="w-full text-left">
                    <thead>
                        <tr className="border-b border-emerald-100 text-xs font-bold text-slate-400 uppercase tracking-widest">
                            <th className="pb-4 pt-0">Topic</th>
                            <th className="pb-4 pt-0">Mastery</th>
                            <th className="pb-4 pt-0">BKT Score</th>
                            <th className="pb-4 pt-0">ELO Rating</th>
                            <th className="pb-4 pt-0">Velocity</th>
                            <th className="pb-4 pt-0">Attempts</th>
                            <th className="pb-4 pt-0">Status</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm">
                        {Object.entries(state.mastery_levels)
                            .sort((a, b) => b[1].score - a[1].score)
                            .map(([topic, data]) => (
                                <tr key={topic} className="border-b border-slate-100 hover:bg-emerald-50/50 transition-colors">
                                    <td className="py-4 font-semibold text-slate-700">{topic}</td>
                                    <td className="py-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
                                                <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${data.score * 100}%` }} />
                                            </div>
                                            <span className="text-emerald-600 font-bold">{(data.score * 100).toFixed(0)}%</span>
                                        </div>
                                    </td>
                                    <td className="py-4 text-slate-500 font-mono">{(data.bkt_score * 100).toFixed(1)}%</td>
                                    <td className="py-4 font-bold text-blue-600">{data.elo_score}</td>
                                    <td className={`py-4 font-bold ${data.learning_velocity > 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                        {data.learning_velocity > 0 ? '↗' : '↘'} {Math.abs(data.learning_velocity).toFixed(2)}
                                    </td>
                                    <td className="py-4 text-slate-500">{data.attempts}</td>
                                    <td className="py-4">
                                        <span className={`px-2.5 py-1 rounded-lg text-[10px] uppercase font-black tracking-wider ${data.status === 'mastered' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' :
                                            data.status === 'in_progress' ? 'bg-amber-100 text-amber-700 border border-amber-200' : 'bg-slate-100 text-slate-500 border border-slate-200'
                                            }`}>
                                            {data.status.replace('_', ' ')}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                    </tbody>
                </table>
            </div>

            {/* Evaluation History Timeline */}
            <div className="glass-card p-8 hover-lift">
                <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <ShieldCheckIcon className="w-5 h-5 text-blue-500" />
                    Evaluation History
                </h3>
                <div className="flex gap-3 overflow-x-auto pb-2">
                    {state.evaluation_history.map((evalItem, i) => (
                        <div key={i} className={`flex-shrink-0 w-48 p-4 rounded-xl border shadow-sm ${evalItem.passed ? 'bg-white border-emerald-100' : 'bg-white border-rose-100'}`}>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Turn {i + 1}</span>
                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-black text-sm ${evalItem.passed ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
                                    {evalItem.score}
                                </div>
                            </div>
                            <p className="text-xs font-bold text-slate-700 mb-1">{evalItem.topic}</p>
                            <p className="text-[10px] text-slate-400 leading-relaxed line-clamp-2">{evalItem.feedback_summary}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Performance;
