import React from 'react';
import type { AgentState } from '../types';
import {
    DocumentTextIcon,
    CheckCircleIcon,
    PlayIcon,
    MapIcon,
    ClockIcon,
    BookOpenIcon,
    ArrowRightIcon,
    SparklesIcon,
    LightBulbIcon,
    AcademicCapIcon,
} from '@heroicons/react/24/outline';

interface StudyPlanProps {
    state: AgentState | null;
}

// ─── Demo syllabus for showcasing Planner Agent output ───
const DEMO_SYLLABUS = [
    {
        title: 'Foundations of Data Structures',
        description: 'Build a solid foundation with core data structures including arrays, linked lists, stacks, and queues. Understand memory allocation, pointer mechanics, and abstract data types.',
        topics: ['Arrays & Memory Layout', 'Linked Lists (Singly & Doubly)', 'Stacks', 'Queues & Deques', 'Abstract Data Types'],
        estimated_time: '90 min',
        status: 'completed',
        mastery: 92,
    },
    {
        title: 'Trees & Hierarchical Structures',
        description: 'Explore tree-based data structures from binary trees to balanced search trees. Learn traversal algorithms, insertion/deletion operations, and self-balancing mechanisms.',
        topics: ['Binary Trees', 'Binary Search Trees', 'AVL Trees', 'Tree Traversals (In/Pre/Post)', 'Heap & Priority Queue'],
        estimated_time: '120 min',
        status: 'completed',
        mastery: 85,
    },
    {
        title: 'Sorting & Searching Algorithms',
        description: 'Master comparison-based and non-comparison sorting algorithms. Analyze time/space complexity trade-offs and understand when to apply each algorithm.',
        topics: ['Bubble & Selection Sort', 'Merge Sort', 'Quick Sort', 'Binary Search', 'Radix & Counting Sort'],
        estimated_time: '90 min',
        status: 'in_progress',
        mastery: 72,
    },
    {
        title: 'Graph Theory & Traversal',
        description: 'Understand graph representations and traversal algorithms. Build intuition for pathfinding, connectivity, and topological ordering in directed/undirected graphs.',
        topics: ['Graph Representations', 'BFS (Breadth-First Search)', 'DFS (Depth-First Search)', 'Dijkstra\'s Algorithm', 'Topological Sort'],
        estimated_time: '120 min',
        status: 'current',
        mastery: 55,
    },
    {
        title: 'Dynamic Programming',
        description: 'Develop the ability to recognize and solve DP problems by identifying optimal substructure and overlapping subproblems. Practice memoization and tabulation approaches.',
        topics: ['Fibonacci & Memoization', 'Knapsack Problem', 'Longest Common Subsequence', 'Matrix Chain Multiplication', 'DP on Trees'],
        estimated_time: '150 min',
        status: 'upcoming',
        mastery: 30,
    },
    {
        title: 'Advanced Algorithms & Problem Solving',
        description: 'Tackle advanced algorithmic paradigms including greedy strategies, divide-and-conquer, backtracking, and competitive programming patterns.',
        topics: ['Greedy Algorithms', 'Divide & Conquer', 'Backtracking', 'String Algorithms (KMP)', 'Complexity Analysis Mastery'],
        estimated_time: '120 min',
        status: 'upcoming',
        mastery: 0,
    },
];

const getStatusConfig = (status: string) => {
    switch (status) {
        case 'completed': return { color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', badge: 'COMPLETED', badgeBg: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: CheckCircleIcon };
        case 'in_progress': return { color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', badge: 'IN PROGRESS', badgeBg: 'bg-blue-100 text-blue-700 border-blue-200', icon: PlayIcon };
        case 'current': return { color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', badge: 'CURRENT FOCUS', badgeBg: 'bg-amber-100 text-amber-700 border-amber-200', icon: LightBulbIcon };
        default: return { color: 'text-slate-400', bg: 'bg-slate-50', border: 'border-slate-200', badge: 'UPCOMING', badgeBg: 'bg-slate-100 text-slate-500 border-slate-200', icon: ClockIcon };
    }
};

const StudyPlan: React.FC<StudyPlanProps> = ({ state }) => {
    const syllabus = (state?.syllabus && state.syllabus.length > 0) ? state.syllabus : null;
    const isDemo = !syllabus;
    const modules = isDemo ? DEMO_SYLLABUS : syllabus;

    // Calculate overall progress
    const completedModules = DEMO_SYLLABUS.filter(m => m.status === 'completed').length;
    const totalModules = DEMO_SYLLABUS.length;
    const overallProgress = isDemo ? Math.round((completedModules / totalModules) * 100) : (state?.global_mastery_score ? Math.round(state.global_mastery_score * 100) : 0);

    return (
        <div className="space-y-8 animate-fade-in px-4 pb-12">
            {/* Header */}
            <header className="flex items-start justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg">
                            <MapIcon className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-3xl font-extrabold text-slate-800 tracking-tight">Planner Agent — Curriculum Roadmap</h2>
                            <p className="text-slate-500">Personalized learning path designed by the AI Planner Agent</p>
                        </div>
                    </div>
                </div>
                {isDemo && (
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-700">
                        <SparklesIcon className="w-4 h-4" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Demo Roadmap</span>
                    </div>
                )}
            </header>

            {/* Progress Overview */}
            <div className="glass-card p-6 hover-lift">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <AcademicCapIcon className="w-5 h-5 text-emerald-500" />
                        <span className="font-bold text-slate-800">Overall Curriculum Progress</span>
                    </div>
                    <span className="text-2xl font-extrabold text-emerald-600">{overallProgress}%</span>
                </div>
                <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-emerald-400 via-teal-500 to-emerald-600 rounded-full transition-all duration-1000"
                        style={{ width: `${overallProgress}%` }}
                    />
                </div>
                <div className="flex justify-between mt-3 text-xs text-slate-400">
                    <span>{completedModules} of {totalModules} modules completed</span>
                    <span>{state?.remaining_objectives?.length || 3} objectives remaining</span>
                </div>
            </div>

            {/* Timeline Modules */}
            <div className="relative">
                {/* Vertical timeline line */}
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-emerald-300 via-amber-300 to-slate-200 hidden lg:block" />

                <div className="space-y-6">
                    {(modules || []).map((module, mIdx) => {
                        const mod = isDemo ? (module as typeof DEMO_SYLLABUS[0]) : module;
                        const statusConfig = isDemo ? getStatusConfig((mod as typeof DEMO_SYLLABUS[0]).status) : getStatusConfig(mIdx < 2 ? 'completed' : mIdx === 2 ? 'current' : 'upcoming');
                        const StatusIcon = statusConfig.icon;
                        const mastery = isDemo ? (mod as typeof DEMO_SYLLABUS[0]).mastery : 0;

                        return (
                            <div key={mIdx} className="lg:pl-16 relative">
                                {/* Timeline dot */}
                                <div className={`absolute left-4 top-8 w-5 h-5 rounded-full border-2 ${statusConfig.border} ${statusConfig.bg} hidden lg:flex items-center justify-center z-10`}>
                                    <div className={`w-2 h-2 rounded-full ${statusConfig.color.replace('text', 'bg')}`} />
                                </div>

                                <div className={`glass-card overflow-hidden group border ${statusConfig.border} hover-lift`}>
                                    {/* Module Header */}
                                    <div className={`${statusConfig.bg} p-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 border-b ${statusConfig.border} group-hover:brightness-95 transition-all`}>
                                        <div className="flex items-center gap-4">
                                            <div className={`w-12 h-12 rounded-2xl bg-white flex items-center justify-center ${statusConfig.color} font-black text-lg border ${statusConfig.border} shadow-sm`}>
                                                {mIdx + 1}
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-bold text-slate-800 group-hover:text-emerald-700 transition-colors">{mod.title}</h3>
                                                <div className="flex items-center gap-3 mt-1">
                                                    <span className="flex items-center gap-1 text-xs text-slate-400">
                                                        <ClockIcon className="w-3.5 h-3.5" />
                                                        {mod.estimated_time || '45 min'}
                                                    </span>
                                                    <span className="flex items-center gap-1 text-xs text-slate-400">
                                                        <BookOpenIcon className="w-3.5 h-3.5" />
                                                        {mod.topics.length} topics
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            {isDemo && mastery > 0 && (
                                                <div className="flex items-center gap-2">
                                                    <div className="w-16 h-2 bg-white/80 rounded-full overflow-hidden">
                                                        <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${mastery}%` }} />
                                                    </div>
                                                    <span className="text-xs font-bold text-slate-500">{mastery}%</span>
                                                </div>
                                            )}
                                            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest border ${statusConfig.badgeBg}`}>
                                                <StatusIcon className="w-3.5 h-3.5" />
                                                {statusConfig.badge}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Module Content */}
                                    <div className="p-8 bg-white">
                                        <p className="text-slate-600 text-sm leading-relaxed mb-8 max-w-3xl border-l-2 border-emerald-300 pl-4">{mod.description}</p>

                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                            {mod.topics.map((topic, tIdx) => (
                                                <div key={tIdx} className={`flex items-center gap-3 p-3 rounded-xl border transition-all cursor-default ${isDemo && ((mod as typeof DEMO_SYLLABUS[0]).status === 'completed' || ((mod as typeof DEMO_SYLLABUS[0]).status === 'in_progress' && tIdx < 3))
                                                    ? 'bg-emerald-50 border-emerald-200'
                                                    : 'bg-slate-50 border-slate-100 hover:bg-emerald-50/50 hover:border-emerald-200'
                                                    }`}>
                                                    {isDemo && ((mod as typeof DEMO_SYLLABUS[0]).status === 'completed' || ((mod as typeof DEMO_SYLLABUS[0]).status === 'in_progress' && tIdx < 3)) ? (
                                                        <CheckCircleIcon className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                                                    ) : (
                                                        <div className="w-2 h-2 rounded-full bg-slate-300 flex-shrink-0" />
                                                    )}
                                                    <span className="text-sm font-medium text-slate-700">{topic}</span>
                                                </div>
                                            ))}
                                        </div>

                                        {isDemo && (mod as typeof DEMO_SYLLABUS[0]).status === 'current' && (
                                            <div className="mt-6 p-4 rounded-xl bg-amber-50 border border-amber-200">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <LightBulbIcon className="w-4 h-4 text-amber-500" />
                                                    <span className="text-xs font-bold text-amber-700 uppercase tracking-wider">Planner Agent Recommendation</span>
                                                </div>
                                                <p className="text-sm text-amber-800">Focus on DFS and Dijkstra's Algorithm next. Your BFS understanding is strong — use that foundation to build intuition for weighted graph traversal.</p>
                                            </div>
                                        )}

                                        <div className="mt-6 flex justify-end">
                                            <button className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold transition-all border border-emerald-200 shadow-sm group">
                                                <PlayIcon className="w-4 h-4 text-emerald-600" />
                                                Start Module
                                                <ArrowRightIcon className="w-3 h-3 text-emerald-500 group-hover:translate-x-0.5 transition-transform" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default StudyPlan;
