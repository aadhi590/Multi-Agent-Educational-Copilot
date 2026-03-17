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
    PolarRadiusAxis
} from 'recharts';
import { ChartBarIcon, BeakerIcon, FireIcon } from '@heroicons/react/24/outline';

interface PerformanceProps {
    state: AgentState | null;
}

const Performance: React.FC<PerformanceProps> = ({ state }) => {
    if (!state) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center text-slate-500">
            <div className="w-16 h-16 rounded-3xl bg-emerald-50 flex items-center justify-center mb-4 border border-emerald-100">
                <ChartBarIcon className="w-8 h-8 text-emerald-300" />
            </div>
            <p>Start learning to generate performance analytics</p>
        </div>
    );

    // Prepare line chart data (Mastery over turns)
    const lineData = state.evaluation_history.map((h, i) => ({
        turn: i + 1,
        score: h.score,
        topic: h.topic
    }));

    // Prepare radar chart data (Mastery across different topics)
    const radarData = Object.entries(state.mastery_levels).map(([topic, data]) => ({
        subject: topic,
        A: data.score * 100,
        fullMark: 100,
    }));

    return (
        <div className="space-y-8 animate-fade-in px-4 pb-12">
            <header>
                <h2 className="text-3xl font-bold text-slate-800 mb-2 italic">Performance Analytics</h2>
                <p className="text-slate-500">In-depth analysis of your cognitive progression and mastery velocity.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Progress Over Time */}
                <div className="glass-card p-8 min-h-[400px] shadow-sm">
                    <h3 className="text-lg font-semibold text-slate-800 mb-8 flex items-center gap-2">
                        <BeakerIcon className="w-5 h-5 text-emerald-500" />
                        Learning Progression (Last 10 Turns)
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
                                <XAxis
                                    dataKey="turn"
                                    stroke="rgba(30,41,59,0.4)"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <YAxis
                                    stroke="rgba(30,41,59,0.4)"
                                    fontSize={10}
                                    tickLine={false}
                                    axisLine={false}
                                    domain={[0, 10]}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}
                                    itemStyle={{ color: '#10b981', fontSize: '12px' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="score"
                                    stroke="#10b981"
                                    fillOpacity={1}
                                    fill="url(#colorScore)"
                                    strokeWidth={3}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Cognitive Map */}
                <div className="glass-card p-8 min-h-[400px] flex flex-col items-center shadow-sm">
                    <h3 className="text-lg font-semibold text-slate-800 mb-8 flex self-start items-center gap-2">
                        <FireIcon className="w-5 h-5 text-amber-500" />
                        Subject Mastery Radar
                    </h3>
                    {radarData.length > 0 ? (
                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart data={radarData}>
                                    <PolarGrid stroke="rgba(16,185,129,0.2)" />
                                    <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(30,41,59,0.7)', fontSize: 10 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} axisLine={false} tick={false} />
                                    <Radar
                                        name="Mastery"
                                        dataKey="A"
                                        stroke="#10b981"
                                        fill="#10b981"
                                        fillOpacity={0.3}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-slate-400 italic">
                            No mastery data recorded across topics.
                        </div>
                    )}
                </div>
            </div>

            <div className="glass-card p-8 overflow-x-auto shadow-sm">
                <h3 className="text-lg font-semibold text-slate-800 mb-6">Mastery Detail View</h3>
                <table className="w-full text-left">
                    <thead>
                        <tr className="border-b border-emerald-100 text-xs font-bold text-slate-400 uppercase tracking-widest">
                            <th className="pb-4 pt-0">Topic</th>
                            <th className="pb-4 pt-0">Mastery Level</th>
                            <th className="pb-4 pt-0">BKT Probability</th>
                            <th className="pb-4 pt-0">Velocity</th>
                            <th className="pb-4 pt-0">Attemps</th>
                            <th className="pb-4 pt-0">Status</th>
                        </tr>
                    </thead>
                    <tbody className="text-sm">
                        {Object.entries(state.mastery_levels).map(([topic, data]) => (
                            <tr key={topic} className="border-b border-slate-100 hover:bg-emerald-50/50 transition-colors">
                                <td className="py-4 font-semibold text-slate-700">{topic}</td>
                                <td className="py-4 text-emerald-600 font-bold">{(data.score * 100).toFixed(1)}%</td>
                                <td className="py-4 text-slate-500">{(data.bkt_score * 100).toFixed(1)}%</td>
                                <td className={`py-4 font-medium ${data.learning_velocity > 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                    {data.learning_velocity > 0 ? '↗' : '↘'} {Math.abs(data.learning_velocity).toFixed(2)}
                                </td>
                                <td className="py-4 text-slate-500">{data.attempts}</td>
                                <td className="py-4">
                                    <span className={`px-2 py-1 rounded-md text-[10px] uppercase font-black ${data.status === 'mastered' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' :
                                        data.status === 'in_progress' ? 'bg-amber-100 text-amber-700 border border-amber-200' : 'bg-slate-100 text-slate-500 border border-slate-200'
                                        }`}>
                                        {data.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Performance;
