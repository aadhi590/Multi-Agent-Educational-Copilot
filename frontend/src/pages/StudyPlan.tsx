import type { AgentState } from '../types';
import { DocumentTextIcon, CheckCircleIcon, PlayIcon } from '@heroicons/react/24/outline';

interface StudyPlanProps {
    state: AgentState | null;
}

const StudyPlan: React.FC<StudyPlanProps> = ({ state }) => {
    if (!state || !state.syllabus || state.syllabus.length === 0) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center text-slate-500">
            <div className="w-16 h-16 rounded-3xl bg-emerald-50 flex items-center justify-center mb-4 text-emerald-300 border border-emerald-100">
                <DocumentTextIcon className="w-8 h-8" />
            </div>
            <p className="max-w-xs">Ask the Tutor or Planner to generate a structured study plan for you.</p>
        </div>
    );

    return (
        <div className="space-y-8 animate-fade-in px-4 pb-12">
            <header>
                <h2 className="text-3xl font-bold text-slate-800 mb-2 italic tracking-tight">Structured Syllabus</h2>
                <p className="text-slate-500 tracking-wide">A tailored roadmap designed by the Planner Agent based on your learning goals.</p>
            </header>

            <div className="space-y-6">
                {state.syllabus.map((module, mIdx) => (
                    <div key={mIdx} className="glass-card shadow-sm overflow-hidden transition-all hover:border-emerald-200 group">
                        <div className="bg-emerald-50/50 p-6 flex justify-between items-center border-b border-emerald-100 group-hover:bg-emerald-50 transition-colors">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-emerald-600 font-bold border border-emerald-200 shadow-sm">
                                    {mIdx + 1}
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-slate-800 group-hover:text-emerald-700 transition-colors uppercase tracking-tight">{module.title}</h3>
                                    <p className="text-xs text-slate-400 uppercase tracking-[0.2em] font-black mt-0.5">{module.estimated_time || '45 MINS'}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-50 border border-teal-200 text-teal-600 text-[10px] font-black uppercase tracking-widest">
                                <CheckCircleIcon className="w-3.5 h-3.5" />
                                Adaptive Module
                            </div>
                        </div>

                        <div className="p-8 bg-white">
                            <p className="text-slate-600 text-sm leading-relaxed mb-8 max-w-2xl border-l-2 border-emerald-300 pl-4">{module.description}</p>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {module.topics.map((topic, tIdx) => (
                                    <div key={tIdx} className="flex items-center gap-3 p-4 rounded-xl bg-emerald-50 border border-emerald-100 hover:border-emerald-300 hover:bg-emerald-100/50 transition-all cursor-default">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]" />
                                        <span className="text-sm font-medium text-slate-700">{topic}</span>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-8 flex justify-end">
                                <button className="flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold transition-all border border-emerald-200 shadow-sm">
                                    <PlayIcon className="w-4 h-4 text-emerald-600" />
                                    Jump to Module
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StudyPlan;
