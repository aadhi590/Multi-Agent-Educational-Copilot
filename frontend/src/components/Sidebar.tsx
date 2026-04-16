
import { NavLink } from 'react-router-dom';
import {
    ChatBubbleLeftRightIcon,
    Squares2X2Icon,
    DocumentTextIcon,
    ChartBarIcon,
    AcademicCapIcon,
    HomeIcon,
    MapIcon,
} from '@heroicons/react/24/outline';

const Sidebar = () => {
    const navItems = [
        { name: 'Landing', path: '/', icon: HomeIcon },
        { name: 'Dashboard', path: '/dashboard', icon: Squares2X2Icon },
        { name: 'Tutor Chat', path: '/chat', icon: ChatBubbleLeftRightIcon },
        { name: 'Curriculum', path: '/plan', icon: MapIcon },
        { name: 'Analytics', path: '/analytics', icon: ChartBarIcon },
    ];

    return (
        <aside className="w-64 h-screen glass border-r border-gray-200 flex flex-col fixed left-0 top-0 z-20">
            <div className="p-6 flex items-center gap-3 bg-gradient-to-b from-emerald-50/50 to-transparent">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 transform hover:rotate-12 transition-transform">
                    <AcademicCapIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h1 className="text-xl font-bold text-slate-800 tracking-tight">EDUSAATHI</h1>
                    <p className="text-[10px] text-emerald-600 uppercase tracking-widest font-semibold">Educational AI</p>
                </div>
            </div>

            <nav className="flex-1 px-4 py-6 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        end={item.path === '/'}
                        className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group
              ${isActive
                                ? 'bg-gradient-to-r from-emerald-100/80 to-emerald-50/50 text-emerald-800 border border-emerald-200/60 shadow-sm'
                                : 'text-slate-500 hover:text-emerald-700 hover:bg-emerald-50/80 hover:scale-[1.02] border border-transparent'}
            `}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.name}</span>
                    </NavLink>
                ))}
            </nav>

            {/* Agent Legend */}
            <div className="px-4 pb-3">
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-2 px-2">Active Agents</p>
                <div className="space-y-1">
                    {[
                        { name: 'Tutor', color: 'bg-emerald-500' },
                        { name: 'Evaluator', color: 'bg-blue-500' },
                        { name: 'Coach', color: 'bg-rose-500' },
                        { name: 'Planner', color: 'bg-amber-500' },
                    ].map((agent) => (
                        <div key={agent.name} className="flex items-center gap-2 px-2 py-1">
                            <div className={`w-2 h-2 rounded-full ${agent.color}`} />
                            <span className="text-[10px] font-medium text-slate-500">{agent.name}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="p-4 border-t border-gray-100">
                <div className="bg-emerald-50 rounded-2xl p-4 border border-emerald-100">
                    <p className="text-xs text-emerald-700 font-semibold mb-1">Multi-Agent System</p>
                    <p className="text-[10px] text-slate-500 leading-relaxed">
                        LangGraph · Gemini · RAG · BKT
                    </p>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
