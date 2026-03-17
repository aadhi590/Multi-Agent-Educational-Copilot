import React, { useState, useRef, useEffect } from 'react';
import type { Message, AgentState } from '../types';
import {
    PaperAirplaneIcon,
    SparklesIcon,
    UserCircleIcon,
    AcademicCapIcon,
    ShieldCheckIcon,
    LightBulbIcon,
    ExclamationCircleIcon
} from '@heroicons/react/24/outline';

interface ChatProps {
    onStateUpdate: (state: AgentState) => void;
}

const Chat: React.FC<ChatProps> = ({ onStateUpdate }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [activeAgent, setActiveAgent] = useState('tutor');
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
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    student_id: 'student_123', // Hardcoded for demo, would be from auth
                }),
            });

            const data = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                agent: data.agent,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
            setActiveAgent(data.agent);
            onStateUpdate(data.state);
        } catch (error) {
            console.error('Chat error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getAgentIcon = (agent: string) => {
        switch (agent) {
            case 'tutor': return <AcademicCapIcon className="w-5 h-5 text-emerald-500" />;
            case 'evaluator': return <ShieldCheckIcon className="w-5 h-5 text-teal-500" />;
            case 'planner': return <LightBulbIcon className="w-5 h-5 text-amber-500" />;
            case 'coach': return <SparklesIcon className="w-5 h-5 text-rose-500" />;
            case 'critic': return <ExclamationCircleIcon className="w-5 h-5 text-red-500" />;
            default: return <SparklesIcon className="w-5 h-5 text-emerald-500" />;
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-120px)] animate-fade-in relative max-w-5xl mx-auto">
            {/* Agent Status Bar */}
            <div className="flex items-center justify-between mb-4 px-2">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center border border-emerald-100 shadow-sm">
                        {getAgentIcon(activeAgent)}
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-slate-800 capitalize">{activeAgent} Agent</h3>
                        <p className="text-[10px] text-emerald-600 font-medium tracking-wider uppercase">Active Session</p>
                    </div>
                </div>

                <div className="hidden sm:flex items-center gap-2">
                    {['Meta', 'Tutor', 'Planner', 'Evaluator', 'Coach', 'Critic'].map((agent) => (
                        <div
                            key={agent}
                            className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-tighter transition-all duration-300 ${activeAgent === agent.toLowerCase() ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20 scale-105' : 'bg-emerald-50 text-slate-500 border border-emerald-100'}`}
                        >
                            {agent.toUpperCase()}
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
                        <div className="w-20 h-20 rounded-full bg-emerald-50 flex items-center justify-center mb-6">
                            <SparklesIcon className="w-10 h-10 text-emerald-400" />
                        </div>
                        <h3 className="text-xl font-bold text-slate-800 mb-2 italic">How can I help you today?</h3>
                        <p className="text-slate-500 max-w-xs text-sm">
                            I can explain complex concepts in DSA, Physics, or Math using the Socratic method.
                        </p>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
                    >
                        <div className={`flex gap-3 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border border-emerald-100 ${message.role === 'user' ? 'bg-emerald-600' : 'bg-emerald-50'}`}>
                                {message.role === 'user' ? <UserCircleIcon className="w-5 h-5 text-white" /> : getAgentIcon(message.agent || 'tutor')}
                            </div>
                            <div className={`p-4 rounded-2xl ${message.role === 'user' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20' : 'glass-card text-slate-800 shadow-sm'}`}>
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                                {message.agent && (
                                    <div className="mt-3 pt-2 border-t border-emerald-100 flex justify-between items-center">
                                        <span className="text-[10px] font-bold text-slate-400 tracking-widest">{message.agent.toUpperCase()} LOG</span>
                                        <span className="text-[10px] text-slate-400 font-mono italic">{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start animate-pulse">
                        <div className="flex gap-3 max-w-[85%]">
                            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center border border-emerald-100">
                                <SparklesIcon className="w-4 h-4 text-emerald-300" />
                            </div>
                            <div className="glass p-4 rounded-2xl flex items-center gap-1">
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
                        className="w-full bg-white border border-emerald-200 rounded-2xl px-6 py-4 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all shadow-sm"
                    />
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                        <kbd className="hidden sm:inline-flex px-1.5 py-0.5 rounded border border-emerald-100 bg-emerald-50 text-[10px] text-slate-400 font-sans tracking-tighter">Enter</kbd>
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
