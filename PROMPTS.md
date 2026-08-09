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
## Prompt 3 — Next.js Frontend Implementation

### AI Tool

Cursor Agent

### Prompt

Implement the frontend for the AI Interviewer using the existing Next.js and Tailwind CSS project.

Requirements:

* Build the main frontend experience for the AI Interviewer
* Create the interview and feedback pages
* Create reusable layout components
* Create reusable UI components
* Maintain a clean and consistent visual design
* Use the existing Tailwind CSS configuration
* Follow the existing project structure
* Keep components modular and reusable
* Ensure the implementation is responsive
* Use proper TypeScript and React conventions
* Avoid unnecessary dependencies
* Ensure the application can run successfully with the existing project setup

### AI Response / Output

Cursor implemented the requested frontend structure and generated the required pages and reusable components.

The implementation included:

* Updated `frontend/app/page.tsx`
* Updated `frontend/app/layout.tsx`
* Updated `frontend/app/globals.css`
* Added the interview route under `frontend/app/interview/`
* Added the feedback route under `frontend/app/feedback/`
* Added `PageContainer` as a reusable layout component
* Added `SiteHeader` and `SiteFooter` for consistent application layout
* Added `Button` as a reusable UI component
* Added `PlaceholderPanel` for the interview interface
* Updated `tailwind.config.ts`

The frontend dependencies were installed using `npm install`, and the application was successfully started locally using the project's development server.

### Where It Was Used

The generated frontend forms the user-facing layer of the AI Interviewer application.

The interview and feedback routes provide the initial application flow, while the reusable layout and UI components provide a consistent foundation for connecting the frontend with the FastAPI backend and future AI interview functionality.

### Human Review

The generated changes were reviewed in Cursor using the Changes panel and Git diff.

The newly created routes, reusable components, styling changes, TypeScript files and Tailwind configuration were reviewed before committing the implementation.

The frontend was then tested locally by installing the project dependencies and starting the development server with:

`npm install`

`npm run dev`

The application was opened through the local development URL to verify that the frontend loaded successfully.

After local verification, the changes were committed to Git using:

`git commit -m "feat: complete frontend implementation"`

The commit was then pushed to the GitHub repository.

### Vibe Coding Workflow

Cursor Agent was used to generate the initial implementation from the defined requirements. The generated code was then reviewed and tested by the developer before being accepted into the project.

The workflow followed an iterative AI-assisted development process:

**Prompt → AI-generated implementation → Human review → Local testing → Git commit → GitHub push**

This kept the developer responsible for reviewing the generated code and verifying the resulting application rather than treating the AI output as automatically correct.


## Prompt 4 — Data Models & Services

Implement the backend data layer for the AI Interview Agent using the provided hackathon data and technical specification.

Requirements:

* Add the required backend data files under `backend/data/`.
* Create Pydantic models for the curriculum and candidate data.
* Add:

  * `backend/app/models/curriculum.py`
  * `backend/app/models/candidate.py`
* Implement reusable JSON loading and validation services.
* Add appropriate custom exceptions for missing or invalid data files.
* Implement services for:

  * retrieving curriculum information
  * retrieving a candidate by candidate ID
* Keep the data layer modular and independent from API routes.
* Follow the existing FastAPI project architecture and type-safe Python conventions.
* Add unit tests covering the models, JSON loading, candidate lookup, curriculum retrieval, and error cases.
* Do not hardcode candidate or curriculum information that should come from the provided JSON data.


---

## Prompt 4 — Curriculum and Candidate Data Loaders

### AI Tool

Cursor Agent

### Prompt

Load `curriculum.json` and `candidate_profiles.json`.

Create reusable services that:

- Read JSON files
- Validate data
- Return curriculum
- Return candidate by ID

Use clean Python architecture.

### AI Response / Output

Cursor implemented reusable backend data-loading services for the
curriculum and candidate profile data.

The implementation included:

- JSON file loading for `curriculum.json`
- JSON file loading for `candidate_profiles.json`
- Data validation using the project's Pydantic models
- A service for retrieving the curriculum
- A service for retrieving a candidate by ID
- Appropriate error handling for missing or invalid data
- Clean separation between data loading and the rest of the application

### Where It Was Used

The data loader services were integrated into the backend so that
curriculum and candidate profile data could be accessed through
reusable service-layer functionality.

These services provide the data required by later interview and
candidate-related features.

### Human Review

The generated implementation was reviewed using Cursor's Changes panel
and Git diff.

The JSON loading logic, validation, service structure, file paths and
error handling were checked to ensure they followed the existing
backend architecture.

The implementation was then tested and committed to Git.

### Commit

`Implement curriculum and candidate data loaders`

---


---

## Prompt 5 — Session Management

### AI Tool

Cursor Agent

### Prompt

Implement interview session management.

Requirements:

- Use sessionId
- Store conversation history
- Store questions asked
- Store curriculum days covered
- Store candidate profile
- Store interview progress

Use an in-memory session manager.

Keep code modular.

### AI Response / Output

Cursor implemented an in-memory interview session management system.

The implementation included:

- Unique `sessionId` based session handling
- Storage for conversation history
- Tracking of questions asked during the interview
- Tracking of curriculum days covered
- Storage of the candidate profile associated with the session
- Tracking of interview progress
- Session creation and retrieval functionality
- Modular session management service structure

The session manager was designed to keep interview state available
throughout an active interview without requiring persistent database
storage.

### Where It Was Used

The session management system was integrated into the backend interview
flow to maintain state across multiple interactions within an
interview session.

It provides the foundation for maintaining conversation context,
candidate information and interview progress in later milestones.

### Human Review

The generated implementation was reviewed using Cursor's Changes panel
and Git diff.

The session model, stored fields, session ID handling, in-memory
storage and service structure were checked to ensure the implementation
matched the milestone requirements and existing backend architecture.

The implementation was then tested and committed to Git.

### Commit

`Add interview session management`

---

## Prompt 6 — API Endpoint

### AI Tool

Cursor Agent

### Prompt

Implement the POST /api/interview endpoint according to the provided technical specification.

Requirements:

- Accept the request body exactly as specified.
- Handle the first request differently from follow-up requests.
- Validate input.
- Return the response in the required format.
- Keep interview state using sessionId.

Before making changes:
- Inspect the existing backend architecture and the implementations from previous milestones.
- Reuse the existing models, services, session management, and exception handling where appropriate.
- Do not introduce unnecessary architectural changes.
- Keep the implementation modular and consistent with the existing project structure.

Implement the endpoint and update any related service/model files only when required.

After implementation:
- Run the existing test suite.
- Add or update tests for the new API endpoint and its validation/state-handling behavior.
- Ensure all existing tests continue to pass.
- Do not modify unrelated functionality.

### Commit

Implement interview API endpoint