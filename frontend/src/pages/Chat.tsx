import React, { useState, useRef, useEffect } from 'react';
import type { Message, AgentState } from '../types';
import {
    PaperAirplaneIcon,
    SparklesIcon,
    UserCircleIcon,
    AcademicCapIcon,
    ShieldCheckIcon,
    LightBulbIcon,
    HeartIcon,
    ExclamationCircleIcon,
    MapIcon,
    CheckCircleIcon,
    XCircleIcon,
} from '@heroicons/react/24/outline';

interface ChatProps {
    onStateUpdate: (state: AgentState) => void;
}

// ─── Agent styling map ───
const AGENT_STYLES: Record<string, { gradient: string; bg: string; border: string; icon: React.ElementType; label: string; tagline: string }> = {
    tutor: {
        gradient: 'from-emerald-500 to-teal-500',
        bg: 'bg-emerald-50',
        border: 'border-emerald-200',
        icon: AcademicCapIcon,
        label: 'Tutor',
        tagline: 'Socratic Dialogue',
    },
    evaluator: {
        gradient: 'from-blue-500 to-indigo-500',
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        icon: ShieldCheckIcon,
        label: 'Evaluator',
        tagline: 'Assessment Engine',
    },
    coach: {
        gradient: 'from-rose-500 to-pink-500',
        bg: 'bg-rose-50',
        border: 'border-rose-200',
        icon: HeartIcon,
        label: 'Coach',
        tagline: 'Motivational Support',
    },
    planner: {
        gradient: 'from-amber-500 to-orange-500',
        bg: 'bg-amber-50',
        border: 'border-amber-200',
        icon: MapIcon,
        label: 'Planner',
        tagline: 'Curriculum Design',
    },
    critic: {
        gradient: 'from-red-500 to-rose-600',
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: ExclamationCircleIcon,
        label: 'Critic',
        tagline: 'Quality Review',
    },
    meta: {
        gradient: 'from-purple-500 to-violet-600',
        bg: 'bg-purple-50',
        border: 'border-purple-200',
        icon: SparklesIcon,
        label: 'Meta',
        tagline: 'Orchestrator',
    },
};

const getAgentStyle = (agent: string) => AGENT_STYLES[agent] || AGENT_STYLES['tutor'];

// ─── Evaluator inline result card ───
const EvaluationCard: React.FC<{ content: string }> = ({ content }) => {
    // Try to parse evaluation-like content
    const scoreMatch = content.match(/(\d+)\s*\/\s*10/);
    const score = scoreMatch ? parseInt(scoreMatch[1]) : null;
    const passed = score !== null && score >= 6;

    if (score === null) return null;

    return (
        <div className={`mt-3 p-4 rounded-xl border ${passed ? 'bg-emerald-50/80 border-emerald-200' : 'bg-rose-50/80 border-rose-200'}`}>
            <div className="flex items-center gap-3 mb-2">
                {passed ? (
                    <CheckCircleIcon className="w-5 h-5 text-emerald-500" />
                ) : (
                    <XCircleIcon className="w-5 h-5 text-rose-500" />
                )}
                <span className={`text-sm font-bold ${passed ? 'text-emerald-700' : 'text-rose-700'}`}>
                    Assessment Result: {score}/10
                </span>
                <span className={`ml-auto px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-wider ${passed ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                    {passed ? 'PASSED' : 'NEEDS REVIEW'}
                </span>
            </div>
            <div className="w-full h-2 bg-white/80 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-1000 ${passed ? 'bg-gradient-to-r from-emerald-400 to-teal-500' : 'bg-gradient-to-r from-rose-400 to-red-500'}`}
                    style={{ width: `${score * 10}%` }}
                />
            </div>
        </div>
    );
};

// ─── Coach motivational card ───
const MotivationCard: React.FC = () => (
    <div className="mt-3 p-4 rounded-xl bg-gradient-to-r from-rose-50 to-pink-50 border border-rose-200/60">
        <div className="flex items-center gap-2 mb-1">
            <HeartIcon className="w-4 h-4 text-rose-500" />
            <span className="text-[10px] font-bold text-rose-600 uppercase tracking-widest">Motivational Intervention</span>
        </div>
        <div className="flex gap-1 mt-2">
            {['😊', '💪', '🌟', '📚', '🎯'].map((e) => (
                <span key={e} className="text-sm">{e}</span>
            ))}
        </div>
    </div>
);

// ─── Socratic indicator ───
const SocraticBadge: React.FC = () => (
    <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200/60">
        <LightBulbIcon className="w-3.5 h-3.5 text-emerald-500" />
        <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest">Socratic Method — Think & Respond</span>
    </div>
);

const Chat: React.FC<ChatProps> = ({ onStateUpdate }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [activeAgent, setActiveAgent] = useState('tutor');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        const currentInput = input;
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: currentInput,
                    student_id: 'student_demo',
                    session_id: sessionId,
                }),
            });

            const data = await response.json();

            if (data.session_id && !sessionId) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                agent: data.agent,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
            setActiveAgent(data.agent);
            if (data.state) {
                onStateUpdate(data.state);
            }
        } catch (error) {
            console.error('Chat error:', error);
            // Fallback: show error in chat
            setMessages((prev) => [
                ...prev,
                {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: 'I apologize, but I encountered a connection issue. Please ensure the backend server is running on port 8001.',
                    agent: 'system',
                    timestamp: new Date(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const agentStyle = getAgentStyle(activeAgent);
    const AgentIcon = agentStyle.icon;

    // Quick prompts for demo
    const quickPrompts = [
        { label: '🎓 Teach me Binary Search Trees', prompt: 'Teach me about Binary Search Trees in Data Structures' },
        { label: '📝 Quiz me on sorting algorithms', prompt: 'Quiz me on sorting algorithms. Ask me a question and evaluate my answer.' },
        { label: '📋 Create a study plan for DSA', prompt: 'Create a structured study plan for Data Structures and Algorithms' },
        { label: '💡 Explain recursion simply', prompt: 'I\'m really struggling with recursion. Can you explain it in a simple way?' },
    ];

    return (
        <div className="flex flex-col h-[calc(100vh-120px)] animate-fade-in relative max-w-5xl mx-auto">
            {/* Agent Status Bar */}
            <div className="flex items-center justify-between mb-4 px-2">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agentStyle.gradient} flex items-center justify-center shadow-lg`}>
                        <AgentIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-slate-800 capitalize">{agentStyle.label} Agent</h3>
                        <p className="text-[10px] text-emerald-600 font-medium tracking-wider uppercase">{agentStyle.tagline}</p>
                    </div>
                </div>

                <div className="hidden sm:flex items-center gap-2">
                    {Object.entries(AGENT_STYLES).filter(([k]) => k !== 'meta').map(([key, style]) => (
                        <div
                            key={key}
                            className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-tighter transition-all duration-300 ${activeAgent === key
                                ? `bg-gradient-to-r ${style.gradient} text-white shadow-md scale-105`
                                : `${style.bg} text-slate-500 border ${style.border}`
                                }`}
                        >
                            {style.label.toUpperCase()}
                        </div>
                    ))}
                </div>
            </div>

            {/* Chat Messages */}
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto pr-4 space-y-6 scrollbar-hide"
            >
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center px-6">
                        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-100 to-teal-100 flex items-center justify-center mb-6 shadow-lg shadow-emerald-200/30">
                            <SparklesIcon className="w-10 h-10 text-emerald-500" />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-800 mb-2">How can I help you today?</h3>
                        <p className="text-slate-500 max-w-md text-sm mb-8 leading-relaxed">
                            I can explain concepts using the Socratic method, evaluate your understanding, create study plans, or provide motivational support.
                        </p>

                        {/* Quick prompts */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
                            {quickPrompts.map((qp) => (
                                <button
                                    key={qp.label}
                                    onClick={() => setInput(qp.prompt)}
                                    className="text-left px-4 py-3 rounded-xl bg-white/70 backdrop-blur border border-emerald-100 text-sm text-slate-600 hover:bg-emerald-50 hover:border-emerald-200 hover:text-emerald-700 transition-all duration-300 shadow-sm hover:shadow-md"
                                >
                                    {qp.label}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((message) => {
                    const msgAgent = message.agent || 'tutor';
                    const msgStyle = getAgentStyle(msgAgent);
                    const MsgIcon = msgStyle.icon;
                    const isTutor = msgAgent === 'tutor';
                    const isEvaluator = msgAgent === 'evaluator';
                    const isCoach = msgAgent === 'coach';
                    const hasQuestion = message.role === 'assistant' && message.content.includes('?');

                    return (
                        <div
                            key={message.id}
                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
                        >
                            <div className={`flex gap-3 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                {/* Avatar */}
                                <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${message.role === 'user'
                                    ? 'bg-gradient-to-br from-slate-700 to-slate-900'
                                    : `bg-gradient-to-br ${msgStyle.gradient}`
                                    }`}>
                                    {message.role === 'user' ? (
                                        <UserCircleIcon className="w-5 h-5 text-white" />
                                    ) : (
                                        <MsgIcon className="w-4 h-4 text-white" />
                                    )}
                                </div>

                                {/* Message bubble */}
                                <div className={`rounded-2xl overflow-hidden ${message.role === 'user'
                                    ? 'bg-gradient-to-br from-slate-800 to-slate-900 text-white shadow-lg shadow-slate-800/20 rounded-tr-sm'
                                    : `glass-card ${msgStyle.border} border rounded-tl-sm`
                                    }`}>
                                    {/* Agent header for assistant messages */}
                                    {message.role === 'assistant' && (
                                        <div className={`px-4 pt-3 pb-1 flex items-center gap-2 ${msgStyle.bg} border-b ${msgStyle.border}`}>
                                            <MsgIcon className={`w-3.5 h-3.5 ${msgStyle.border.replace('border', 'text').replace('-200', '-500')}`} />
                                            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                                {msgStyle.label} Agent
                                            </span>
                                            <span className="text-[9px] text-slate-400 ml-auto">
                                                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        </div>
                                    )}

                                    <div className="p-4">
                                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

                                        {/* Socratic badge for tutor questions */}
                                        {message.role === 'assistant' && isTutor && hasQuestion && <SocraticBadge />}

                                        {/* Evaluation card for evaluator */}
                                        {message.role === 'assistant' && isEvaluator && <EvaluationCard content={message.content} />}

                                        {/* Motivational card for coach */}
                                        {message.role === 'assistant' && isCoach && <MotivationCard />}

                                        {/* User message timestamp */}
                                        {message.role === 'user' && (
                                            <div className="mt-2 pt-1.5 border-t border-white/10 text-right">
                                                <span className="text-[10px] text-white/40">
                                                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}

                {isLoading && (
                    <div className="flex justify-start animate-pulse">
                        <div className="flex gap-3 max-w-[85%]">
                            <div className={`w-8 h-8 rounded-xl bg-gradient-to-br ${agentStyle.gradient} flex items-center justify-center shadow-sm`}>
                                <AgentIcon className="w-4 h-4 text-white" />
                            </div>
                            <div className="glass-card p-4 rounded-2xl flex items-center gap-2">
                                <span className="text-[10px] text-slate-400 font-medium mr-2">{agentStyle.label} is thinking</span>
                                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <form
                onSubmit={handleSendMessage}
                className="mt-6 flex gap-3 pb-4"
            >
                <div className="relative flex-1">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask me anything..."
                        className="w-full glass-card border border-emerald-200/50 rounded-2xl px-6 py-4 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-4 focus:ring-emerald-500/20 focus:border-emerald-500/50 transition-all shadow-lg hover:shadow-xl"
                    />
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                        <kbd className="hidden sm:inline-flex px-2 py-1 rounded-md border border-emerald-200/50 bg-white/50 text-[10px] font-bold text-slate-400 font-sans tracking-tighter uppercase backdrop-blur-md shadow-sm">Enter</kbd>
                    </div>
                </div>
                <button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-500/20 hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100"
                >
                    <PaperAirplaneIcon className="w-6 h-6" />
                </button>
            </form>
        </div>
    );
};

export default Chat;
