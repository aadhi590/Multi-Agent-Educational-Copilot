# EduSaathi — Multi-Agent Educational Copilot

A **Multi-Agent AI tutoring system** that breaks the teacher role into specialized agents — Planner, Tutor, Evaluator, Coach, and Critic — orchestrated via LangGraph for adaptive, personalised learning experiences.

---

## 🧠 Architecture Overview

| Agent | Role |
|-------|------|
| **Planner** | Manages learning path and curriculum |
| **Tutor** | Provides hints and interactive scaffolding |
| **Evaluator** | Assesses student performance and mastery |
| **Coach** | Monitors frustration and provides motivation |
| **Critic** | Reviews responses for quality and accuracy |
| **Meta / Orchestrator** | Routes messages to the right agent using LangGraph |

---

## 📋 Prerequisites

Make sure you have the following installed:

- **Python** 3.10 or higher → [python.org](https://python.org)
- **Node.js** 18 or higher + npm → [nodejs.org](https://nodejs.org)
- **Git** → [git-scm.com](https://git-scm.com)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/aadhi590/Multi-Agent-Educational-Copilot.git
cd Multi-Agent-Educational-Copilot
```

---

### 2. Backend Setup

#### a) Create a virtual environment

```bash
cd backend
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

#### b) Install dependencies

```bash
pip install -r requirements.txt
```

#### c) Create the `.env` file

Create a file named `.env` inside the `backend/` folder with the following content:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-key.json
```

> **Where to get these:**
> - `GOOGLE_API_KEY` → [Google AI Studio](https://aistudio.google.com/app/apikey)
> - `FIREBASE_SERVICE_ACCOUNT_PATH` → Download your service account JSON from [Firebase Console](https://console.firebase.google.com) → Project Settings → Service Accounts → Generate new private key. Save it as `firebase-key.json` inside `backend/`.

> **Note:** Firebase is **optional**. If `firebase-key.json` is not provided, the app will run without database persistence (in-memory sessions only).

#### d) Start the backend server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**
API docs (Swagger UI): **http://localhost:8000/docs**

---

### 3. Frontend Setup

Open a **new terminal** (keep the backend running).

```bash
cd frontend
npm install
npm run dev
```

The app will be available at: **http://localhost:5173**

---

## 🗂️ Project Structure

```
Multi-Agent-Educational-Copilot/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # 🔒 (not committed) API keys
│   ├── firebase-key.json        # 🔒 (not committed) Firebase credentials
│   ├── agents/                  # Planner, Tutor, Evaluator, Coach, Critic
│   ├── orchestration/           # LangGraph workflow orchestrator
│   ├── knowledge_store/         # ML-enhanced RAG knowledge base
│   ├── retrieval/               # Vector store for document retrieval
│   ├── evaluation/              # Mastery model and scoring
│   ├── tools/                   # Agent tools (calculator, search, etc.)
│   ├── state/                   # Shared agent state definition
│   └── database.py              # Firebase Firestore integration
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, Chat, Quiz, Resources
│   │   ├── components/          # Reusable React components
│   │   └── types/               # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## 🔒 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | Google Gemini API key for LLM inference |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | ⚠️ Optional | Path to Firebase service account JSON for session persistence |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Google Gemini (via `langchain-google-genai`) |
| **Agent Orchestration** | LangGraph |
| **Backend** | FastAPI + Uvicorn |
| **Database** | Firebase Firestore (optional) |
| **Frontend** | React 19 + TypeScript + Vite |
| **Styling** | Tailwind CSS v4 |
| **Charts** | Recharts |
| **ML** | NumPy, SymPy (sentiment & mastery scoring) |

---

## ✅ Verify the Setup

Once both servers are running, test the backend health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "agents": ["meta", "tutor", "planner", "evaluator", "coach", "critic"],
  "features": ["rag", "tools", "mastery_tracking", "sentiment_analysis"]
}
```

Then open **http://localhost:5173** in your browser to use the EduSaathi interface.
