import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { AgentState } from '../types';
import {
    ChartBarIcon,
    BookOpenIcon,
    BoltIcon,
    FireIcon,
    AcademicCapIcon,
    ShieldCheckIcon,
    HeartIcon,
    MapIcon,
    ChatBubbleLeftRightIcon,
    ArrowTrendingUpIcon,
    ClockIcon,
    SparklesIcon,
} from '@heroicons/react/24/outline';

interface DashboardProps {
    state: AgentState | null;
}

// ─── Demo data for showcasing when no live session exists ───
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
    remaining_objectives: ['DFS', 'Dijkstra Algorithm', 'Topological Sort'],
    learning_objectives: ['BFS', 'DFS', 'Dijkstra', 'Topological Sort', 'MST'],
    syllabus: [],
    evaluation_history: [
        { score: 9, passed: true, topic: 'Recursion', feedback_summary: 'Excellent understanding of recursive thinking patterns.', misconceptions: [], tool_verified: true },
        { score: 8, passed: true, topic: 'Binary Search Trees', feedback_summary: 'Strong BST operations knowledge. Minor gap in balancing.', misconceptions: ['AVL rotation direction'], tool_verified: true },
        { score: 7, passed: true, topic: 'Sorting Algorithms', feedback_summary: 'Good grasp of comparison sorts. Needs work on radix sort.', misconceptions: ['Radix sort complexity'], tool_verified: true },
        { score: 5, passed: false, topic: 'Dynamic Programming', feedback_summary: 'Identified subproblems but struggled with memoization.', misconceptions: ['Overlapping subproblems vs unique'], tool_verified: true },
        { score: 6, passed: true, topic: 'Graph Traversal', feedback_summary: 'BFS understood well. DFS needs more practice.', misconceptions: ['DFS backtracking'], tool_verified: true },
    ],
    last_evaluation_result: { score: 6, passed: true, topic: 'Graph Traversal', feedback_summary: 'BFS understood well. DFS needs more practice.', misconceptions: ['DFS backtracking'], tool_verified: true },
};

const AGENT_ACTIVITY = [
    { agent: 'Tutor', icon: AcademicCapIcon, action: 'Taught Binary Search Trees via Socratic dialogue', time: '5 min ago', gradient: 'from-emerald-500 to-teal-500' },
    { agent: 'Evaluator', icon: ShieldCheckIcon, action: 'Assessed Graph Traversal — Score: 6/10', time: '12 min ago', gradient: 'from-blue-500 to-indigo-500' },
    { agent: 'Coach', icon: HeartIcon, action: 'Motivational intervention for Dynamic Programming', time: '20 min ago', gradient: 'from-rose-500 to-pink-500' },
    { agent: 'Planner', icon: MapIcon, action: 'Updated curriculum roadmap with Graph Theory module', time: '35 min ago', gradient: 'from-amber-500 to-orange-500' },
];

const Dashboard: React.FC<DashboardProps> = ({ state: liveState }) => {
    const navigate = useNavigate();
    const state = liveState || DEMO_STATE;
    const isDemo = !liveState;

    const stats = [
        { name: 'Global Mastery', value: `${(state.global_mastery_score * 100).toFixed(1)}%`, icon: ChartBarIcon, gradient: 'from-emerald-500 to-teal-500', lightBg: 'bg-emerald-50', border: 'border-emerald-100' },
        { name: 'Topics Studied', value: Object.keys(state.mastery_levels).length, icon: BookOpenIcon, gradient: 'from-blue-500 to-indigo-500', lightBg: 'bg-blue-50', border: 'border-blue-100' },
        { name: 'Last Score', value: state.last_evaluation_result?.score ? `${state.last_evaluation_result.score}/10` : '—', icon: BoltIcon, gradient: 'from-amber-500 to-orange-500', lightBg: 'bg-amber-50', border: 'border-amber-100' },
        { name: 'Engagement', value: `${(state.engagement_score * 100).toFixed(0)}%`, icon: FireIcon, gradient: 'from-rose-500 to-pink-500', lightBg: 'bg-rose-50', border: 'border-rose-100' },
    ];

    return (
        <div className="space-y-8 animate-fade-in px-4 pb-12">
            {/* Header */}
            <header className="flex items-start justify-between">
                <div>
                    <h2 className="text-3xl font-extrabold text-slate-800 mb-1">Student Mastery Dashboard</h2>
                    <p className="text-slate-500">Track your learning progression across multiple domains.</p>
                </div>
                {isDemo && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-700">
                        <SparklesIcon className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Demo Data</span>
                    </div>
                )}
            </header>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat) => (
                    <div key={stat.name} className="glass-card p-6 flex items-start justify-between hover-lift relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/20 to-transparent -mr-10 -mt-10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700 ease-out" />
                        <div className="relative z-10">
                            <p className="text-sm font-medium text-slate-500 mb-1">{stat.name}</p>
                            <p className="text-3xl font-extrabold text-slate-800">{stat.value}</p>
                        </div>
                        <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg`}>
                            <stat.icon className="w-6 h-6 text-white" />
                        </div>
                    </div>
                ))}
            </div>

            {/* Sentiment & Status Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6 hover-lift">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-100">
                            <ArrowTrendingUpIcon className="w-5 h-5 text-emerald-500" />
                        </div>
                        <div>
                            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Sentiment</p>
                            <p className="text-lg font-bold text-slate-800 capitalize">{state.sentiment}</p>
                        </div>
                    </div>
                    <div className="flex gap-1">
                        {['😊', '📚', '💪'].map((e, i) => (
                            <span key={i} className="text-lg">{e}</span>
                        ))}
                    </div>
                </div>
                <div className="glass-card p-6 hover-lift">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-rose-50 border border-rose-100">
                            <HeartIcon className="w-5 h-5 text-rose-500" />
                        </div>
                        <div>
                            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Frustration Level</p>
                            <p className="text-lg font-bold text-slate-800">{(state.frustration_level * 100).toFixed(0)}%</p>
                        </div>
                    </div>
                    <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-emerald-400 to-rose-400 rounded-full transition-all duration-1000" style={{ width: `${state.frustration_level * 100}%` }} />
                    </div>
                </div>
                <div className="glass-card p-6 hover-lift">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-blue-50 border border-blue-100">
                            <ClockIcon className="w-5 h-5 text-blue-500" />
                        </div>
                        <div>
                            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Current Focus</p>
                            <p className="text-lg font-bold text-slate-800">{state.current_topic}</p>
                        </div>
                    </div>
                    <p className="text-xs text-slate-400">{state.remaining_objectives.length} objectives remaining</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Mastery Breakdown */}
                <div className="lg:col-span-2 glass-card p-8 hover-lift">
                    <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <ChartBarIcon className="w-5 h-5 text-emerald-500" />
                        Domain Mastery
                    </h3>
                    <div className="space-y-5">
                        {Object.entries(state.mastery_levels).map(([topic, data]) => (
                            <div key={topic} className="space-y-2">
                                <div className="flex justify-between items-center text-sm">
                                    <div className="flex items-center gap-2">
                                        <span className="text-slate-700 font-semibold">{topic}</span>
                                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-wider ${data.status === 'mastered' ? 'bg-emerald-100 text-emerald-700' :
                                            data.status === 'in_progress' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'
                                            }`}>{data.status.replace('_', ' ')}</span>
                                    </div>
                                    <span className="text-emerald-600 font-bold">{(data.score * 100).toFixed(0)}%</span>
                                </div>
                                <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-1000 ${data.status === 'mastered'
                                            ? 'bg-gradient-to-r from-emerald-400 to-teal-500'
                                            : data.score >= 0.5 ? 'bg-gradient-to-r from-amber-400 to-orange-500' : 'bg-gradient-to-r from-rose-400 to-red-500'
                                            }`}
                                        style={{ width: `${data.score * 100}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                                    <span>BKT: {(data.bkt_score * 100).toFixed(0)}% · ELO: {data.elo_score}</span>
                                    <span className={data.learning_velocity > 0 ? 'text-emerald-500' : 'text-rose-500'}>
                                        {data.learning_velocity > 0 ? '↗' : '↘'} Velocity: {Math.abs(data.learning_velocity).toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Agent Activity Feed */}
                <div className="glass-card p-8 hover-lift">
                    <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <SparklesIcon className="w-5 h-5 text-purple-500" />
                        Agent Activity
                    </h3>
                    <div className="space-y-4">
                        {AGENT_ACTIVITY.map((item, i) => (
                            <div key={i} className="flex gap-3 p-3 rounded-xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                                <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${item.gradient} flex items-center justify-center flex-shrink-0 shadow-sm`}>
                                    <item.icon className="w-4 h-4 text-white" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-xs font-bold text-slate-700">{item.agent} Agent</p>
                                    <p className="text-[11px] text-slate-500 leading-relaxed truncate">{item.action}</p>
                                    <p className="text-[9px] text-slate-400 mt-0.5">{item.time}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Evaluations */}
            <div className="glass-card p-8 hover-lift">
                <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <ShieldCheckIcon className="w-5 h-5 text-blue-500" />
                    Evaluator Agent — Recent Assessments
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {state.evaluation_history.slice(0, 6).map((eval_item, i) => (
                        <div key={i} className={`p-5 rounded-xl border ${eval_item.passed ? 'bg-white border-emerald-100' : 'bg-white border-rose-100'} shadow-sm hover:shadow-md transition-shadow`}>
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-sm font-bold text-slate-800">{eval_item.topic}</span>
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${eval_item.passed
                                    ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                                    : 'bg-rose-50 text-rose-600 border border-rose-200'
                                    }`}>
                                    <span className="font-black text-sm">{eval_item.score}</span>
                                </div>
                            </div>
                            <p className="text-xs text-slate-500 leading-relaxed mb-3">{eval_item.feedback_summary}</p>
                            {eval_item.misconceptions.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                    {eval_item.misconceptions.map((m, j) => (
                                        <span key={j} className="px-2 py-0.5 rounded-md bg-rose-50 border border-rose-100 text-[9px] font-bold text-rose-600">{m}</span>
                                    ))}
                                </div>
                            )}
                            {eval_item.tool_verified && (
                                <div className="mt-2 flex items-center gap-1 text-[9px] text-emerald-600 font-bold">
                                    <ShieldCheckIcon className="w-3 h-3" />
                                    Tool Verified
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <button
                    onClick={() => navigate('/chat')}
                    className="glass-card p-6 hover-lift flex items-center gap-4 text-left group"
                >
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                        <ChatBubbleLeftRightIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h4 className="font-bold text-slate-800 group-hover:text-emerald-700 transition-colors">Start Learning Session</h4>
                        <p className="text-xs text-slate-500">Chat with the Tutor Agent using Socratic dialogue</p>
                    </div>
                </button>
                <button
                    onClick={() => navigate('/plan')}
                    className="glass-card p-6 hover-lift flex items-center gap-4 text-left group"
                >
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                        <MapIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h4 className="font-bold text-slate-800 group-hover:text-amber-700 transition-colors">View Curriculum Roadmap</h4>
                        <p className="text-xs text-slate-500">See your personalized Planner Agent syllabus</p>
                    </div>
                </button>
            </div>
        </div>
    );
};

export default Dashboard;
