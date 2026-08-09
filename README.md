# AI Interview Agent

AI-powered mock interview platform that simulates realistic technical interviews based on a candidate's curriculum progress and profile. Built for hackathon submission.

## How It Works

1. **Start** — Frontend sends candidate profile → Backend creates interview session → LLM generates first question
2. **Chat** — Candidate answers → LLM evaluates & asks next question (tracks curriculum coverage, avoids repeats)
3. **End** — Backend requests structured feedback → LLM returns strengths, gaps, and next steps

## Tech Stack

| Layer | Tech | Why |
|-------|------|-----|
| Backend | **FastAPI** + Pydantic v2 | Async, typed, auto-docs |
| Frontend | **Next.js 15** (App Router) + Tailwind CSS | SSR, modern React |
| LLM | **OpenAI SDK** (compatible with Groq, Gemini, etc.) | Swap provider via env vars, zero code change |
| Data | `curriculum.json` + `candidates.json` | Seed data for interview context |

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # then edit .env with your API key
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000 · Backend: http://localhost:8000 · Docs: http://localhost:8000/docs

## LLM Setup (Pick One)

The app uses the **OpenAI SDK** which supports any OpenAI-compatible API via `OPENAI_BASE_URL`. No code changes needed — just set environment variables.

### Option A: Groq (Free, Fastest) ✨ Recommended for hackathon

1. Get free key: https://console.groq.com/keys
2. Set in `backend/.env`:

```env
OPENAI_API_KEY=gsk_xxxxxxxxxxxx
OPENAI_MODEL=llama-3.3-70b-versatile
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

### Option B: Google Gemini (Free, Generous limits)

1. Get free key: https://aistudio.google.com/apikey
2. Set in `backend/.env`:

```env
OPENAI_API_KEY=AIzaxxxxxxxxxxxx
OPENAI_MODEL=gemini-2.0-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
```

### Option C: OpenAI (Paid)

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
```

### Option D: No LLM (Stub mode — works offline)

Leave `OPENAI_API_KEY` empty. The app uses `StubLLMService` which returns fixed responses. Good for testing without any API key.

## API Reference

### `POST /api/interview`

Single endpoint, three request shapes:

| Action | Request Body | Response |
|--------|-------------|----------|
| **Start** | `{sessionId, candidate}` | `{reply, done:false, feedback:null, progress}` |
| **Continue** | `{sessionId, message}` | `{reply, done:false, feedback:null, progress}` |
| **End** | `{sessionId, done:true}` | `{reply, done:true, feedback:{summary,strengths,gaps,next}, progress}` |

**Errors:** 404 (session not found), 409 (session already completed), 422 (validation), 502 (LLM error), 503 (LLM misconfigured)

## Project Structure

```
AI-Interviewer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, exception handlers
│   │   ├── config.py            # Pydantic Settings (env vars)
│   │   ├── exceptions.py        # Custom exception types
│   │   ├── routes/
│   │   │   ├── health.py        # GET /health
│   │   │   └── interviews.py    # POST /api/interview
│   │   ├── services/
│   │   │   ├── data_loader.py          # Generic JSON loader + validator
│   │   │   ├── curriculum_service.py   # Curriculum data (cached)
│   │   │   ├── candidate_service.py   # Candidate lookup
│   │   │   ├── session_service.py     # In-memory session CRUD
│   │   │   ├── interview_service.py   # Start/continue/end orchestration
│   │   │   ├── llm_service.py         # LLMService ABC + OpenAI + Stub
│   │   │   ├── prompt_builder.py      # Interview prompt construction
│   │   │   ├── feedback_service.py    # Feedback generation + parsing
│   │   │   └── feedback_prompt_builder.py
│   │   ├── models/              # Pydantic schemas (candidate, curriculum, session, interview, feedback)
│   │   └── data/                # curriculum.json, candidates.json
│   ├── tests/                   # 260 tests (pytest)
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Home page
│   │   ├── interview/page.tsx           # Interview chat page
│   │   └── feedback/page.tsx            # Feedback page
│   ├── components/interview/
│   │   ├── ChatContainer.tsx            # Main chat UI
│   │   ├── ChatInput.tsx                # Auto-resize textarea
│   │   ├── ChatMessage.tsx              # Message bubble (AI/Candidate)
│   │   ├── TypingIndicator.tsx          # Bouncing dots
│   │   └── FeedbackPanel.tsx            # Structured feedback display
│   ├── hooks/useInterviewChat.ts        # Interview state + API integration
│   ├── lib/api.ts                       # API client
│   └── types/interview.ts               # TypeScript types
│
├── PROMPTS.md                  # Prompt engineering notes
└── README.md
```

## Architecture

```
Browser → Next.js (port 3000)
              ↓ /api/* rewrite
         FastAPI (port 8000)
              ↓
         LLMService (OpenAI SDK)
              ↓
         OpenAI / Groq / Gemini / Stub
```

- **Routes** are thin — they validate input and delegate to services
- **Services** contain all business logic (session management, prompt building, LLM calls)
- **Models** are pure Pydantic schemas — no logic, just validation
- **Prompt construction** is separate from LLM provider — swap providers without touching prompts
- **Frontend** uses same-origin API calls proxied through Next.js rewrites (no CORS issues in production)

## Testing

```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v              # 260 tests
```

## Conventions

| Layer | Purpose |
|-------|---------|
| `routes/` | HTTP endpoints — thin handlers that delegate to services |
| `services/` | Business logic, orchestration, external API calls |
| `models/` | Request/response schemas and domain types |
| `prompts/` | Version-controlled LLM prompt templates |
| `data/` | Seed data, fixtures, and static reference files |
| `components/ui/` | Generic, reusable UI building blocks |
| `components/layout/` | Page structure components |
| `components/interview/` | Domain-specific interview UI |

## Deployment

### Frontend → Vercel

```bash
cd frontend
npx vercel
# Set env var: NEXT_PUBLIC_API_URL= (empty, uses rewrites)
```

### Backend → Railway / Render

1. Connect repo, set root directory to `backend/`
2. Set environment variables from `.env.example`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Update frontend `NEXT_PUBLIC_API_URL` to backend URL

---

Built for hackathon submission — **AI Interview Agent** 🤖
