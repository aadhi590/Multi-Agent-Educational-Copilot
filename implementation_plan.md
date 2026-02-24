# Multi-Agent Educational Copilot: Implementation Plan

## Overview
The goal of this project is to build a Multi-Agent Educational Copilot, operationalizing theoretical agentic AI into a role-specialized software system. This system will dynamically route learner interactions to appropriate agents based on the learner's intent, state, and history.

## Technology Stack
*   **Backend:** FastAPI with LangChain for multi-agent orchestration.
*   **AI Engine:** Gemini Pro (via Google Generative AI) for reasoning and persona logic.
*   **Database:** Firebase Admin SDK for persistent 'Learner State' and session history.
*   **Frontend:** React (TypeScript) with a real-time, streaming chat interface.

## Architecture & Core Components

### 1. The Orchestrator (`backend/main.py`)
A FastAPI application responsible for:
*   Asynchronous routing logic.
*   Fetching student history from Firebase.
*   Delegating queries to specific agents based on learner intent and history.
*   State Estimation: Classifying interaction patterns into 'Confusion', 'Progression', or 'Mastery'.

### 2. The Agent Cluster (`backend/agents/`)
A modular directory containing four distinct role-specialized agents:
*   **Planner (`planner.py`):** Manages the curriculum roadmap and learning objectives.
*   **Tutor (`tutor.py`):** A Socratic agent providing hints and scaffolds (no direct answers).
*   **Evaluator (`evaluator.py`):** An objective grader for mastery verification.
*   **Coach (`coach.py`):** A motivational agent that triggers interventions when frustration is detected.

## Execution Phases

### Phase 1: Initialization and Setup
*   Initialize the workspace and folder structure for both backend and frontend.
*   Set up a Python virtual environment and install backend dependencies (FastAPI, LangChain, Google Generative AI SDK, Firebase Admin).
*   Initialize the React TypeScript frontend.

### Phase 2: Agent Personas and System Prompts
*   Generate detailed pedagogical logic for each agent.
*   Create artifacts specifically for verifying the system prompts and instructional consistency of the Planner, Tutor, Evaluator, and Coach agents.

### Phase 3: Core Implementation
*   Develop the FastAPI backend orchestrator and agent routing logic.
*   Integrate Firebase for state management.
*   Develop the React frontend with a real-time streaming chat interface.
*   Connect the frontend to the backend orchestrator.

### Phase 4: Testing and Verification
*   Run automated end-to-end tests using browser control.
*   Specifically verify the intelligent routing mechanism (e.g., ensuring a "confused student" query is correctly routed to the Tutor agent).

---
*Please review this implementation plan. Once approved, we will begin Phase 1 and create the individual artifacts for each agent's pedagogical logic.*
