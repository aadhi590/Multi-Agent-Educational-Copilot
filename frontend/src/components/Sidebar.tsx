
import { NavLink } from 'react-router-dom';
import {
    ChatBubbleLeftRightIcon,
    Squares2X2Icon,
    DocumentTextIcon,
    ChartBarIcon,
    AcademicCapIcon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
    const navItems = [
        { name: 'Dashboard', path: '/', icon: Squares2X2Icon },
        { name: 'Tutor Chat', path: '/chat', icon: ChatBubbleLeftRightIcon },
        { name: 'Study Plan', path: '/plan', icon: DocumentTextIcon },
        { name: 'Performance', path: '/analytics', icon: ChartBarIcon },
    ];

    return (
        <aside className="w-64 h-screen glass border-r border-gray-200 flex flex-col fixed left-0 top-0 z-20">
            <div className="p-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-sm">
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
                        className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300
              ${isActive
                                ? 'bg-emerald-100/50 text-emerald-700 border border-emerald-200 shadow-sm'
                                : 'text-slate-500 hover:text-emerald-700 hover:bg-emerald-50 border border-transparent'}
            `}
                    >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.name}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="p-6 border-t border-gray-100">
                <div className="bg-emerald-50 rounded-2xl p-4 border border-emerald-100">
                    <p className="text-xs text-emerald-700 font-semibold mb-1">Study Session</p>
                    <p className="text-[10px] text-slate-500 leading-relaxed">
                        Your progress is being tracked across agents.
                    </p>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
