import React from 'react';
import type { AgentState } from '../types';
import { ChartBarIcon, BookOpenIcon, BoltIcon, FireIcon } from '@heroicons/react/24/outline';

interface DashboardProps {
    state: AgentState | null;
}

const Dashboard: React.FC<DashboardProps> = ({ state }) => {
    if (!state) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center text-slate-500">
            <div className="w-16 h-16 rounded-3xl bg-emerald-50 flex items-center justify-center mb-4 border border-emerald-100">
                <BoltIcon className="w-8 h-8 text-emerald-300" />
            </div>
            <p>Start a conversation to see your analytics</p>
        </div>
    );

    const stats = [
        { name: 'Global Mastery', value: `${(state.global_mastery_score * 100).toFixed(1)}%`, icon: ChartBarIcon, color: 'text-emerald-500 bg-emerald-50 border border-emerald-100' },
        { name: 'Topics Studied', value: Object.keys(state.mastery_levels).length, icon: BookOpenIcon, color: 'text-teal-500 bg-teal-50 border border-teal-100' },
        { name: 'Last Score', value: state.last_evaluation_result?.score ? `${state.last_evaluation_result.score}/10` : '—', icon: BoltIcon, color: 'text-amber-500 bg-amber-50 border border-amber-100' },
        { name: 'Focus Topic', value: state.current_topic || 'General', icon: FireIcon, color: 'text-rose-500 bg-rose-50 border border-rose-100' },
    ];

    return (
        <div className="space-y-8 animate-fade-in px-4 pb-12">
            <header>
                <h2 className="text-3xl font-bold text-slate-800 mb-2">Learning Dashboard</h2>
                <p className="text-slate-500">Track your progress across multiple scientific domains.</p>
            </header>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat) => (
                    <div key={stat.name} className="glass-card p-6 flex items-start justify-between shadow-sm">
                        <div>
                            <p className="text-sm font-medium text-slate-500 mb-1">{stat.name}</p>
                            <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
                        </div>
                        <div className={`p-3 rounded-xl ${stat.color}`}>
                            <stat.icon className="w-6 h-6" />
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Mastery Breakdown */}
                <div className="lg:col-span-2 glass-card p-8 shadow-sm">
                    <h3 className="text-xl font-semibold text-slate-800 mb-6 flex items-center gap-2">
                        <ChartBarIcon className="w-5 h-5 text-emerald-500" />
                        Domain Mastery
                    </h3>
                    <div className="space-y-6">
                        {Object.entries(state.mastery_levels).map(([topic, data]) => (
                            <div key={topic} className="space-y-2">
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-slate-700 font-medium">{topic}</span>
                                    <span className="text-emerald-600 font-bold">{(data.score * 100).toFixed(0)}%</span>
                                </div>
                                <div className="h-2 w-full bg-emerald-50 rounded-full overflow-hidden border border-emerald-100">
                                    <div
                                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-1000"
                                        style={{ width: `${data.score * 100}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                                    <span>Status: {data.status}</span>
                                    <span>Attempts: {data.attempts}</span>
                                </div>
                            </div>
                        ))}
                        {Object.keys(state.mastery_levels).length === 0 && (
                            <p className="text-center text-slate-400 py-8 italic font-light">No domain data yet</p>
                        )}
                    </div>
                </div>

                {/* Recent Evaluations */}
                <div className="glass-card p-8 shadow-sm">
                    <h3 className="text-xl font-semibold text-slate-800 mb-6 flex items-center gap-2">
                        <BoltIcon className="w-5 h-5 text-amber-500" />
                        Recent Activity
                    </h3>
                    <div className="space-y-4">
                        {state.evaluation_history.slice(0, 5).map((eval_item, i) => (
                            <div key={i} className="p-4 rounded-xl bg-white border border-slate-100 shadow-sm flex gap-4">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${eval_item.passed ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-rose-50 text-rose-600 border border-rose-100'}`}>
                                    <span className="font-bold text-sm">{eval_item.score}</span>
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-slate-800">{eval_item.topic}</p>
                                    <p className="text-xs text-slate-500 line-clamp-2 mt-1 leading-relaxed">{eval_item.feedback_summary}</p>
                                </div>
                            </div>
                        ))}
                        {state.evaluation_history.length === 0 && (
                            <p className="text-center text-slate-400 py-8 italic">No recent evaluations</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
