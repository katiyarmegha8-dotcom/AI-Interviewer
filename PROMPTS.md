# AI Prompt Log — AI Interview Agent

This file documents the prompts used during AI-assisted development
of the AI Interview Agent.

---

## Prompt 1 — Initial Project Structure

### AI Tool
Cursor Agent

### Prompt

Create a production-ready project structure for an AI Interview Agent.

Requirements:
- Frontend: Next.js (App Router) + Tailwind CSS
- Backend: FastAPI
- Organize backend into routes, services, models, prompts, and data folders.
- Organize frontend into reusable components.
- Do not implement features yet.
- Create clean folder structure only.

### AI Response / Output

Cursor generated the initial monorepo scaffold containing:

- Next.js frontend with App Router and Tailwind CSS
- FastAPI backend
- Backend routes, services, models, prompts and data directories
- Frontend app and reusable component directories
- Configuration files
- Environment example files
- Dependency files
- Initial application entry points

### Where It Was Used

The generated structure was used as the initial architecture of the
AI Interview Agent project.

### Human Review

The generated files were reviewed using Cursor's Changes panel and Git
diff. The project structure, configuration files, dependencies and
environment examples were checked before continuing development.

The scaffold was then committed to Git.

---

## Prompt 2 — FastAPI Backend Setup

### AI Tool

Cursor Agent

### Prompt

Set up a FastAPI backend.

Requirements:

- Create main.py
- Enable CORS
- Add health endpoint
- Prepare project for future interview endpoints
- Use Pydantic
- Follow best practices

### AI Response / Output

Cursor generated a modular FastAPI backend structure containing:

- `app/main.py` for the application factory, CORS middleware, router registration and lifespan configuration
- `app/config.py` for Pydantic-based environment configuration and CORS origins
- `app/routes/health.py` containing the health check endpoint
- `app/routes/interviews.py` containing an empty interview router prepared for future interview endpoints
- Supporting backend package files and configuration

The FastAPI application was successfully started with Uvicorn.

The API documentation was verified through the `/docs` page, and the health
endpoint was available under:

`GET /api/v1/health`

### Where It Was Used

The generated FastAPI backend was used as the backend foundation for the
AI Interview Agent. The health endpoint provides a basic service check, while
the interview router provides the structure for implementing the interview
functionality in later stages.

### Human Review

The generated backend files were reviewed using Cursor's Changes panel and Git
diff. The FastAPI application structure, CORS configuration, Pydantic settings,
health route and interview route scaffold were checked.

The application was then run locally with Uvicorn and the `/docs` page was
opened to verify that the API was functioning.

The backend changes were then committed and pushed to GitHub.

---