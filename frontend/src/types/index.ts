export interface AgentState {
    frustration_level: number;
    engagement_score: number;
    sentiment: string;
    global_mastery_score: number;
    mastery_levels: Record<string, MasteryData>;
    current_topic: string;
    session_id: string;
    remaining_objectives: string[];
    learning_objectives: string[];
    syllabus: SyllabusModule[];
    evaluation_history: EvaluationResult[];
    last_evaluation_result?: EvaluationResult;
}

export interface MasteryData {
    score: number;
    elo_score: number;
    bkt_score: number;
    attempts: number;
    status: 'not_started' | 'in_progress' | 'mastered';
    learning_velocity: number;
    learning_objectives_met: string[];
}

export interface SyllabusModule {
    title: string;
    description: string;
    topics: string[];
    estimated_time: string;
}

export interface EvaluationResult {
    score: number;
    passed: boolean;
    topic: string;
    feedback_summary: string;
    misconceptions: string[];
    tool_verified: boolean;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    agent?: string;
    timestamp: Date;
}
