import React, { useState, useEffect, useRef, useCallback } from 'react';
import './index.css';

// ── Types ────────────────────────────────────────────────────────────────────
type AgentId = 'tutor' | 'planner' | 'evaluator' | 'coach';

interface Message {
  id: string;
  text: string;
  sender: 'human' | 'agent';
  agent?: AgentId;
  timestamp: Date;
}

interface TopicMastery {
  score: number;
  attempts: number;
  status: string;
  elo_score?: number;
  bkt_score?: number;
}

interface SessionState {
  frustration_level: number;
  engagement_score: number;
  sentiment: string;
  global_mastery_score: number;
  mastery_levels: Record<string, TopicMastery>;
  current_topic: string;
  session_id: string;
}

// ── Agent Config ──────────────────────────────────────────────────────────────
const AGENTS = [
  { id: 'tutor' as AgentId, name: 'Tutor', icon: '🧑‍🏫', desc: 'Socratic Guide', color: 'var(--tutor)', cls: 'tutor' },
  { id: 'planner' as AgentId, name: 'Planner', icon: '🗺️', desc: 'Curriculum Architect', color: 'var(--planner)', cls: 'planner' },
  { id: 'evaluator' as AgentId, name: 'Evaluator', icon: '📊', desc: 'Mastery Assessor', color: 'var(--evaluator)', cls: 'evaluator' },
  { id: 'coach' as AgentId, name: 'Coach', icon: '💪', desc: 'Motivational Mentor', color: 'var(--coach)', cls: 'coach' },
];

// ── Minimal Markdown renderer ─────────────────────────────────────────────────
function renderMarkdown(text: string): string {
  return text
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/^[-•] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
}

function formatTime(d: Date) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

const STUDENT_ID = `student_${Math.random().toString(36).slice(2, 9)}`;

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      text: "👋 Hello! I'm your **Multi-Agent Educational Copilot**.\n\nI adapt in real-time to your learning style. Just tell me what you want to learn and I'll coordinate the right specialist for you!\n\n*Topics: DSA, OOP, Networks, DBMS, Physics, Math, Chemistry*",
      sender: 'agent',
      agent: 'planner',
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState<AgentId>('tutor');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionState, setSessionState] = useState<SessionState>({
    frustration_level: 0,
    engagement_score: 0.8,
    sentiment: 'neutral',
    global_mastery_score: 0,
    mastery_levels: {},
    current_topic: '—',
    session_id: '',
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const humanMsg: Message = {
      id: Date.now().toString(),
      text: trimmed,
      sender: 'human',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, humanMsg]);
    setInput('');
    if (inputRef.current) { inputRef.current.style.height = 'auto'; }
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          student_id: STUDENT_ID,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Server error' }));
        throw new Error(err.detail || `Error ${res.status}`);
      }

      const data = await res.json();

      // Update session tracking
      if (data.session_id) setSessionId(data.session_id);
      if (data.agent && AGENTS.find(a => a.id === data.agent)) {
        setActiveAgent(data.agent as AgentId);
      }

      // Update live state panel
      if (data.state) {
        setSessionState(prev => ({ ...prev, ...data.state }));
      }

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: 'agent',
        agent: data.agent as AgentId,
        timestamp: new Date(),
      }]);

    } catch (e) {
      const err = e instanceof Error ? e.message : 'Unknown error';
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        text: `⚠️ **Connection Error**: ${err}\n\nMake sure the backend is running on port **8000**.`,
        sender: 'agent',
        agent: 'tutor',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, sessionId]);

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Derived mastery ring
  const masteryPct = Math.round(sessionState.global_mastery_score * 100);
  const ringCircumference = 264;
  const ringOffset = ringCircumference - (masteryPct / 100) * ringCircumference;
  const ringColor = masteryPct >= 80 ? 'var(--tutor)' : masteryPct >= 50 ? 'var(--accent)' : 'var(--planner)';

  const masteryLabel =
    masteryPct >= 80 ? 'Mastered 🏆' :
      masteryPct >= 60 ? 'Proficient ✅' :
        masteryPct >= 40 ? 'Learning 📚' :
          masteryPct >= 20 ? 'Beginner 🌱' : 'Starting';

  return (
    <div className="app">

      {/* ── Left Sidebar ── */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">E</div>
          <div>
            <div className="brand-name">EduCopilot</div>
            <div className="brand-sub">Multi-Agent AI</div>
          </div>
        </div>

        <div className="section-label">Active Agents</div>

        <div className="agent-list">
          {AGENTS.map(agent => (
            <div
              key={agent.id}
              className={`agent-card ${activeAgent === agent.id ? 'active' : ''} ${loading && activeAgent === agent.id ? 'responding' : ''}`}
            >
              <div className={`agent-icon ${agent.cls}`}>{agent.icon}</div>
              <div className="agent-info">
                <div className="agent-name">{agent.name}</div>
                <div className="agent-desc">{agent.desc}</div>
              </div>
              <div className={`status-dot ${activeAgent === agent.id ? agent.cls : ''}`} />
            </div>
          ))}
        </div>

        <div className="section-label">Live Signals</div>

        <div className="sentiment-panel">
          <div className="sentiment-row">
            <div className="sentiment-label">
              <span>Frustration</span>
              <span>{Math.round(sessionState.frustration_level * 100)}%</span>
            </div>
            <div className="sentiment-bar">
              <div className="sentiment-fill fill-frustration" style={{ width: `${sessionState.frustration_level * 100}%` }} />
            </div>
          </div>
          <div className="sentiment-row">
            <div className="sentiment-label">
              <span>Engagement</span>
              <span>{Math.round(sessionState.engagement_score * 100)}%</span>
            </div>
            <div className="sentiment-bar">
              <div className="sentiment-fill fill-engagement" style={{ width: `${sessionState.engagement_score * 100}%` }} />
            </div>
          </div>
          <div className="sentiment-row">
            <div className="sentiment-label">
              <span>Sentiment</span>
              <span className="chip">{sessionState.sentiment}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main Chat ── */}
      <main className="main">
        <header className="chat-header">
          <div className="chat-title">Learning Workspace</div>
          <div className="chat-status">
            <div className="live-dot" />
            <span>LangGraph Orchestrator Active</span>
          </div>
        </header>

        <div className="messages">
          {messages.map(msg => (
            <div key={msg.id} className={`msg ${msg.sender}`}>
              <div className="msg-meta">
                {msg.sender === 'agent' && msg.agent && (
                  <div className={`agent-badge badge-${msg.agent}`}>
                    <div className="badge-dot" />
                    {AGENTS.find(a => a.id === msg.agent)?.name ?? msg.agent} Agent
                  </div>
                )}
                <span className="msg-time">{formatTime(msg.timestamp)}</span>
              </div>
              <div className="bubble">
                {msg.sender === 'agent'
                  ? <span dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.text) }} />
                  : msg.text
                }
              </div>
            </div>
          ))}

          {loading && (
            <div className="typing-bubble">
              <div className={`agent-badge badge-${activeAgent}`} style={{ width: 'fit-content' }}>
                <div className="badge-dot" />
                {AGENTS.find(a => a.id === activeAgent)?.name} Agent is thinking…
              </div>
              <div className="typing-dots">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-row">
            <div className="input-box">
              <textarea
                ref={inputRef}
                className="chat-input"
                placeholder="Ask a question, share your goal, or say how you're feeling…"
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKey}
                rows={1}
                disabled={loading}
              />
            </div>
            <button className="send-btn" onClick={sendMessage} disabled={loading || !input.trim()}>
              ↑
            </button>
          </div>
          <div className="input-hint">
            <span>Enter to send • Shift+Enter for new line</span>
            <span>Topic: <strong>{sessionState.current_topic}</strong></span>
          </div>
        </div>
      </main>

      {/* ── Right Panel — Mastery Dashboard ── */}
      <aside className="right-panel">
        <div className="panel-title">Mastery Dashboard</div>

        <div className="mastery-ring-wrap">
          <div className="mastery-ring">
            <svg viewBox="0 0 96 96" width="96" height="96">
              <circle className="ring-bg" cx="48" cy="48" r="42" />
              <circle
                className="ring-fill"
                cx="48" cy="48" r="42"
                stroke={ringColor}
                style={{ strokeDashoffset: ringOffset }}
              />
            </svg>
            <div className="ring-text">
              <span className="ring-pct" style={{ color: ringColor }}>{masteryPct}%</span>
              <span className="ring-lbl">global</span>
            </div>
          </div>
          <div className="mastery-status">{masteryLabel}</div>
        </div>

        <div className="panel-title">Topics</div>

        <div className="topic-list">
          {Object.keys(sessionState.mastery_levels).length === 0 ? (
            <div style={{ fontSize: 12, color: 'var(--text-dim)', padding: '8px 4px' }}>
              No topics assessed yet. Start learning to track progress!
            </div>
          ) : (
            Object.entries(sessionState.mastery_levels).map(([topic, data]) => (
              <div key={topic} className="topic-card">
                <div className="topic-header">
                  <span className="topic-name">{topic}</span>
                  <span className="topic-score">{Math.round((data.score ?? 0) * 100)}%</span>
                </div>
                <div className="topic-bar">
                  <div className="topic-fill" style={{ width: `${(data.score ?? 0) * 100}%` }} />
                </div>
                <div className="topic-meta">
                  <span>{data.attempts ?? 0} attempts</span>
                  <span>{data.status ?? 'unknown'}</span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="panel-title">Session Info</div>
        <div className="session-card">
          <div className="session-row">
            <span>Student ID</span>
            <span>{STUDENT_ID.slice(0, 12)}</span>
          </div>
          <div className="session-row">
            <span>Session</span>
            <span>{sessionId ? sessionId.slice(0, 8) + '…' : 'New'}</span>
          </div>
          <div className="session-row">
            <span>Messages</span>
            <span>{messages.length}</span>
          </div>
          <div className="session-row">
            <span>Active Agent</span>
            <span style={{ color: `var(--${activeAgent})` }}>{activeAgent}</span>
          </div>
        </div>
      </aside>
    </div>
  );
}
