import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    AcademicCapIcon,
    ChatBubbleLeftRightIcon,
    ShieldCheckIcon,
    HeartIcon,
    MapIcon,
    ChartBarIcon,
    SparklesIcon,
    ArrowRightIcon,
    BoltIcon,
    CpuChipIcon,
} from '@heroicons/react/24/outline';

const AGENTS = [
    {
        name: 'Tutor Agent',
        subtitle: 'Socratic Dialogue Engine',
        description:
            'Guides students through concepts using the Socratic method — asking probing questions instead of giving direct answers to build deep understanding.',
        icon: AcademicCapIcon,
        gradient: 'from-emerald-500 to-teal-600',
        lightBg: 'bg-emerald-50',
        border: 'border-emerald-200',
        textColor: 'text-emerald-700',
        demo: '"Why do you think a linked list uses more memory than an array? What trade-off does that enable?"',
    },
    {
        name: 'Evaluator Agent',
        subtitle: 'Adaptive Assessment',
        description:
            'Evaluates student responses using rubric-based scoring with tool-verified answers, tracks misconceptions, and provides structured feedback.',
        icon: ShieldCheckIcon,
        gradient: 'from-blue-500 to-indigo-600',
        lightBg: 'bg-blue-50',
        border: 'border-blue-200',
        textColor: 'text-blue-700',
        demo: '"Score: 7/10 — Good understanding of pointers, but you confused stack vs. heap allocation."',
    },
    {
        name: 'Coach Agent',
        subtitle: 'Motivational Intervention',
        description:
            'Detects frustration and disengagement through sentiment analysis, then intervenes with encouragement, study strategies, and growth mindset framing.',
        icon: HeartIcon,
        gradient: 'from-rose-500 to-pink-600',
        lightBg: 'bg-rose-50',
        border: 'border-rose-200',
        textColor: 'text-rose-700',
        demo: '"I can see this topic is challenging. Remember — every expert was once a beginner. Let\'s try a simpler example."',
    },
    {
        name: 'Planner Agent',
        subtitle: 'Curriculum Roadmap',
        description:
            'Generates personalized, module-based syllabi and learning roadmaps that adapt dynamically based on mastery progression and knowledge gaps.',
        icon: MapIcon,
        gradient: 'from-amber-500 to-orange-600',
        lightBg: 'bg-amber-50',
        border: 'border-amber-200',
        textColor: 'text-amber-700',
        demo: '"Module 3: Trees & Graphs — Estimated 60 min — Prerequisites: Arrays, Recursion ✓"',
    },
];

const FEATURES = [
    { title: 'Multi-Agent Orchestration', desc: 'LangGraph-powered meta-agent routes to the right specialist', icon: CpuChipIcon },
    { title: 'RAG Knowledge Base', desc: 'Retrieval-augmented generation for domain-specific accuracy', icon: BoltIcon },
    { title: 'Bayesian Knowledge Tracing', desc: 'BKT + ELO scoring tracks true mastery probability', icon: ChartBarIcon },
    { title: 'Sentiment Analysis', desc: 'Real-time frustration detection triggers coach interventions', icon: HeartIcon },
];

const Landing: React.FC = () => {
    const navigate = useNavigate();
    const [activeAgent, setActiveAgent] = useState(0);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
        const interval = setInterval(() => {
            setActiveAgent((prev) => (prev + 1) % AGENTS.length);
        }, 4000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-[#f8fafc] overflow-x-hidden">
            {/* ─── HERO SECTION ─── */}
            <section className="relative min-h-screen flex flex-col items-center justify-center px-6 overflow-hidden">
                {/* Animated background orbs */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    <div className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-emerald-200/40 to-teal-200/20 blur-3xl animate-pulse" />
                    <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-blue-200/30 to-indigo-200/20 blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-br from-emerald-100/20 to-transparent blur-3xl" />
                </div>

                <div className={`relative z-10 text-center max-w-4xl mx-auto transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-50 border border-emerald-200/60 mb-8 shadow-sm">
                        <SparklesIcon className="w-4 h-4 text-emerald-500" />
                        <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest">Multi-Agent AI System</span>
                    </div>

                    {/* Logo */}
                    <div className="flex items-center justify-center gap-4 mb-6">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-600 flex items-center justify-center shadow-xl shadow-emerald-500/30 transform hover:rotate-12 transition-transform duration-500">
                            <AcademicCapIcon className="w-9 h-9 text-white" />
                        </div>
                    </div>

                    <h1 className="text-6xl md:text-7xl font-extrabold text-slate-900 tracking-tight leading-tight mb-4">
                        EDU<span className="gradient-text">SAATHI</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-slate-500 font-light max-w-2xl mx-auto mb-4 leading-relaxed">
                        A Multi-Agent Educational Copilot powered by{' '}
                        <span className="font-semibold text-slate-700">LangGraph</span>,{' '}
                        <span className="font-semibold text-slate-700">Gemini</span> &{' '}
                        <span className="font-semibold text-slate-700">RAG</span>
                    </p>
                    <p className="text-sm text-slate-400 mb-10 max-w-lg mx-auto">
                        Intelligent tutoring through Socratic dialogue, adaptive assessments, motivational coaching, and personalized curriculum planning — all orchestrated by AI agents.
                    </p>

                    {/* CTA Buttons */}
                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="group flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold text-lg shadow-xl shadow-emerald-500/30 hover:shadow-2xl hover:shadow-emerald-500/40 hover:scale-105 active:scale-95 transition-all duration-300"
                        >
                            <ChatBubbleLeftRightIcon className="w-6 h-6" />
                            Enter Copilot
                            <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button
                            onClick={() => {
                                document.getElementById('agents-section')?.scrollIntoView({ behavior: 'smooth' });
                            }}
                            className="flex items-center gap-2 px-8 py-4 rounded-2xl bg-white/70 backdrop-blur border border-emerald-200/50 text-slate-700 font-semibold hover:bg-emerald-50 hover:border-emerald-300 transition-all duration-300 shadow-sm"
                        >
                            <SparklesIcon className="w-5 h-5 text-emerald-500" />
                            View Architecture
                        </button>
                    </div>
                </div>

                {/* Scroll indicator */}
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
                    <div className="w-6 h-10 rounded-full border-2 border-emerald-300/50 flex items-start justify-center p-1.5">
                        <div className="w-1.5 h-3 rounded-full bg-emerald-400 animate-pulse" />
                    </div>
                </div>
            </section>

            {/* ─── AGENTS SHOWCASE ─── */}
            <section id="agents-section" className="py-24 px-6">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <span className="text-xs font-bold text-emerald-600 uppercase tracking-[0.3em] mb-3 block">Agent Architecture</span>
                        <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-4">Four Specialized AI Agents</h2>
                        <p className="text-lg text-slate-500 max-w-2xl mx-auto">Each agent has a distinct persona and role, orchestrated by a Meta-Agent that routes student interactions to the right specialist.</p>
                    </div>

                    {/* Agent Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {AGENTS.map((agent, idx) => (
                            <div
                                key={agent.name}
                                className={`glass-card p-8 cursor-pointer transition-all duration-500 ${activeAgent === idx ? 'ring-2 ring-emerald-400/50 scale-[1.02] shadow-xl' : 'hover:scale-[1.01]'}`}
                                onMouseEnter={() => setActiveAgent(idx)}
                            >
                                <div className="flex items-start gap-5">
                                    <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${agent.gradient} flex items-center justify-center shadow-lg flex-shrink-0`}>
                                        <agent.icon className="w-7 h-7 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-xl font-bold text-slate-800 mb-0.5">{agent.name}</h3>
                                        <p className={`text-xs font-bold uppercase tracking-widest ${agent.textColor} mb-3`}>{agent.subtitle}</p>
                                        <p className="text-sm text-slate-500 leading-relaxed mb-4">{agent.description}</p>

                                        {/* Demo quote */}
                                        <div className={`${agent.lightBg} ${agent.border} border rounded-xl p-4 transition-all duration-500 ${activeAgent === idx ? 'opacity-100 translate-y-0' : 'opacity-70 translate-y-1'}`}>
                                            <p className="text-xs text-slate-600 italic leading-relaxed">
                                                <span className={`font-bold ${agent.textColor} not-italic`}>Example: </span>
                                                {agent.demo}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── FEATURES ─── */}
            <section className="py-24 px-6 bg-gradient-to-b from-transparent via-emerald-50/30 to-transparent">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <span className="text-xs font-bold text-emerald-600 uppercase tracking-[0.3em] mb-3 block">Technology Stack</span>
                        <h2 className="text-4xl font-extrabold text-slate-900 mb-4">Powered by Cutting-Edge AI</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {FEATURES.map((feat) => (
                            <div key={feat.title} className="glass-card p-6 text-center hover-lift">
                                <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto mb-4">
                                    <feat.icon className="w-6 h-6 text-emerald-500" />
                                </div>
                                <h3 className="font-bold text-slate-800 mb-2">{feat.title}</h3>
                                <p className="text-sm text-slate-500">{feat.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── FLOW DIAGRAM ─── */}
            <section className="py-24 px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <span className="text-xs font-bold text-emerald-600 uppercase tracking-[0.3em] mb-3 block">Orchestration Flow</span>
                    <h2 className="text-4xl font-extrabold text-slate-900 mb-12">How It Works</h2>

                    <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-6">
                        {[
                            { step: '1', label: 'Student Input', sub: 'Question or answer' },
                            { step: '2', label: 'Meta-Agent', sub: 'Routes to specialist' },
                            { step: '3', label: 'Specialist Agent', sub: 'Tutor/Evaluator/Coach' },
                            { step: '4', label: 'Response + Update', sub: 'Mastery tracking' },
                        ].map((s, i) => (
                            <React.Fragment key={s.step}>
                                <div className="glass-card p-6 min-w-[160px] hover-lift">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 text-white font-bold text-lg flex items-center justify-center mx-auto mb-3 shadow-md">
                                        {s.step}
                                    </div>
                                    <h4 className="font-bold text-slate-800 text-sm">{s.label}</h4>
                                    <p className="text-xs text-slate-400 mt-1">{s.sub}</p>
                                </div>
                                {i < 3 && (
                                    <ArrowRightIcon className="w-6 h-6 text-emerald-300 hidden md:block flex-shrink-0" />
                                )}
                            </React.Fragment>
                        ))}
                    </div>
                </div>
            </section>

            {/* ─── FINAL CTA ─── */}
            <section className="py-24 px-6">
                <div className="max-w-3xl mx-auto text-center">
                    <div className="glass-card p-12 relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-teal-500/5" />
                        <div className="relative z-10">
                            <AcademicCapIcon className="w-12 h-12 text-emerald-500 mx-auto mb-6" />
                            <h2 className="text-3xl font-extrabold text-slate-900 mb-4">Ready to Experience AI-Powered Learning?</h2>
                            <p className="text-slate-500 mb-8 max-w-lg mx-auto">Start a conversation with EduSaathi and experience how multi-agent AI orchestration creates a personalized learning journey.</p>
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="group inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold shadow-xl shadow-emerald-500/30 hover:shadow-2xl hover:scale-105 transition-all duration-300"
                            >
                                Launch EduSaathi
                                <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-emerald-100">
                <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                        <AcademicCapIcon className="w-5 h-5 text-emerald-500" />
                        <span className="font-bold text-slate-700">EduSaathi</span>
                        <span className="text-xs text-slate-400">Multi-Agent Educational Copilot</span>
                    </div>
                    <p className="text-xs text-slate-400">Built with LangGraph · Gemini · FastAPI · React · RAG</p>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
