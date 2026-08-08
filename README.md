# AI Interview Agent

Monorepo for an AI-powered interview platform.

## Project Structure

```
AI-Interviewer/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py             # Application entry point
│   │   ├── config.py           # Environment & app settings
│   │   ├── routes/             # API route handlers
│   │   ├── services/           # Business logic layer
│   │   ├── models/             # Pydantic schemas & data models
│   │   ├── prompts/            # LLM prompt templates
│   │   └── data/               # Static data, fixtures, seed files
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # Next.js (App Router) + Tailwind CSS
│   ├── app/                    # App Router pages & layouts
│   ├── components/
│   │   ├── ui/                 # Reusable UI primitives
│   │   ├── layout/             # Layout components (header, footer, etc.)
│   │   └── interview/          # Interview-specific components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utilities & API client helpers
│   ├── types/                  # Shared TypeScript types
│   ├── public/                 # Static assets
│   └── .env.example
│
├── PROMPTS.md                  # Prompt design notes
└── README.md
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The frontend runs at [http://localhost:3000](http://localhost:3000).  
The backend runs at [http://localhost:8000](http://localhost:8000).

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
