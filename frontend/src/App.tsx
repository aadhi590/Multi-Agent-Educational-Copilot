import React, { useState, useEffect, useRef } from 'react';
import './index.css';

type Message = {
  id: string;
  text: string;
  sender: 'human' | 'agent';
  agentRole?: 'planner' | 'tutor' | 'evaluator' | 'coach';
};

const agents = [
  { id: 'tutor', name: 'Tutor', icon: 'tutor', description: 'Socratic Guide', color: 'var(--agent-tutor)' },
  { id: 'planner', name: 'Planner', icon: 'planner', description: 'Curriculum Architect', color: 'var(--agent-planner)' },
  { id: 'evaluator', name: 'Evaluator', icon: 'evaluator', description: 'Mastery Assessor', color: 'var(--agent-evaluator)' },
  { id: 'coach', name: 'Coach', icon: 'coach', description: 'Motivational Mentor', color: 'var(--agent-coach)' },
  { id: 'animator', name: 'Animator', icon: 'animator', description: 'Video & Animation Creator', color: '#ff58a6' },
];

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: "Hello! I'm your Multi-Agent Educational Copilot. What would you like to learn today?", sender: 'agent', agentRole: 'planner' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeTab, setActiveTab] = useState('tutor');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const newHumanMsg: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'human'
    };

    setMessages(prev => [...prev, newHumanMsg]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          agent_type: activeTab
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      const responseText = data.response;

      const newAgentMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        sender: 'agent',
        agentRole: activeTab as any
      };

      setMessages(prev => [...prev, newAgentMsg]);
    } catch (error) {
      console.error("Fetch error:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error occurred";
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        text: `⚠️ ${errorMessage}. Make sure the backend server is running on port 8000.`,
        sender: 'agent',
        agentRole: activeTab as any
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">E</div>
          Copilot
        </div>

        <div style={{ color: 'var(--text-dim)', marginBottom: '10px', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Active Agents</div>
        <div className="agent-list">
          {agents.map(agent => (
            <div
              key={agent.id}
              className={`agent-item ${activeTab === agent.id ? 'active' : ''}`}
              onClick={() => setActiveTab(agent.id)}
            >
              <div className={`agent-dot ${agent.id}`}></div>
              <div>
                <div style={{ fontWeight: 500, color: '#fff' }}>{agent.name}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{agent.description}</div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Chat */}
      <main className="main-chat">
        <header className="chat-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2>Learning Workspace</h2>
          </div>
          <div style={{ display: 'flex', gap: '15px' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--accent-color)', textShadow: '0 0 5px var(--accent-glow)' }}>Live Engine Mode</span>
          </div>
        </header>

        <div className="chat-messages">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              {msg.sender === 'agent' && (
                <div className="message-agent-name" style={{ color: agents.find(a => a.id === msg.agentRole)?.color }}>
                  <div className={`agent-dot ${msg.agentRole}`} style={{ width: '6px', height: '6px', display: 'inline-block' }}></div>
                  {msg.agentRole} Agent
                </div>
              )}
              <div className="message-text">{msg.text}</div>
            </div>
          ))}
          {isTyping && (
            <div className={`message agent`}>
              <div className="message-agent-name" style={{ color: agents.find(a => a.id === activeTab)?.color }}>
                <div className={`agent-dot ${activeTab}`} style={{ width: '6px', height: '6px', display: 'inline-block' }}></div>
                {activeTab} Agent
              </div>
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask a question or state your goal..."
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button className="send-btn" onClick={handleSend}>
              <svg viewBox="0 0 24 24">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
