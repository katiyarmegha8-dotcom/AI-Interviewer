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


## Prompt 4 — Data Models & Services Implementation

### AI Tool

Arena Agent

### Prompt

Implement the data models and reusable data services for the AI Interviewer using the existing FastAPI project and the provided hackathon data.

Requirements:

* Use the provided `curriculum.json` and `candidates.json` files
* Store the curriculum data under `backend/app/data/curriculum.json`
* Store the candidate data under `backend/app/data/candidates.json`
* Create Pydantic models that accurately represent the provided JSON structures
* Create models for curriculum modules, curriculum days and supported day types
* Create models for candidates, candidate members, missions and candidate signals
* Create reusable data-loading functionality for reading and validating JSON files
* Handle missing files, malformed JSON and validation errors using appropriate exceptions
* Create a curriculum service for loading and validating curriculum data
* Create a candidate service for loading candidates and retrieving an individual candidate by ID
* Handle unknown candidate IDs with an appropriate domain-specific exception
* Keep data-loading paths configurable where practical to support testing
* Use caching for static curriculum and candidate data where appropriate
* Maintain a clean separation between models, services and application logic
* Update the relevant package exports for the newly created models and services
* Preserve the existing FastAPI functionality from the previous implementation
* Do not implement interview execution, LLM orchestration, adaptive questioning, scoring or real-time interview functionality
* Follow the existing project structure and coding conventions
* Avoid unnecessary dependencies

### AI Response / Output

Arena Agent inspected the existing repository and implemented the requested data models and reusable services.

The implementation included:

* Added `backend/app/data/curriculum.json`
* Added `backend/app/data/candidates.json`
* Added `backend/app/exceptions.py`
* Added `backend/app/models/curriculum.py`
* Added `backend/app/models/candidate.py`
* Added `backend/app/services/data_loader.py`
* Added `backend/app/services/curriculum_service.py`
* Added `backend/app/services/candidate_service.py`
* Updated `backend/app/models/__init__.py`
* Updated `backend/app/services/__init__.py`
* Added backend service tests under `backend/tests/test_services.py`

The Pydantic models were created to match the provided curriculum and candidate data structures, including curriculum modules, curriculum days, candidates, missions and candidate signals.

A reusable data loader was implemented to read JSON files and validate them through the corresponding Pydantic models.

Domain-specific exceptions were added for missing files, invalid JSON, validation failures and unknown candidate IDs.

The curriculum and candidate services were implemented with support for cached loading and injectable file paths for testing.

### Where It Was Used

The generated backend implementation provides the data layer for the AI Interviewer application.

The curriculum service provides validated curriculum information, while the candidate service provides access to candidate profiles and individual candidate records.

The reusable data-loading and validation layer provides the foundation for the interview functionality that will be connected in later development.

### Human Review

The generated changes were reviewed in Arena Agent and through the repository changes.

The newly created Pydantic models, data-loading utilities, services, exceptions, test files and package exports were reviewed before accepting the implementation.

The provided curriculum and candidate data were retained as the source data for the application.

The backend test suite was executed after implementation.

All **26 automated tests passed successfully**.

The existing FastAPI health endpoint was also tested and returned a successful response.

After verification, the changes were committed to Git using:

`git commit -m "feat: implement milestone 4 data models and services"`

The commit was then pushed to the GitHub repository.

### Vibe Coding Workflow

Arena Agent was used to generate the initial implementation from the defined requirements and existing project structure. The generated code was then reviewed and tested before being accepted into the project.

The workflow followed an iterative AI-assisted development process:

**Prompt → Repository inspection → AI-generated implementation → Human review → Automated testing → Git commit → GitHub push**

The developer remained responsible for reviewing the generated implementation, verifying the provided data and confirming that the backend tests passed before accepting the changes.



## Prompt 5 — Session Management Implementation

### AI Tool

Arena Agent

### Prompt

Implement interview session management for the existing AI Interviewer project.

Requirements:

- Use a unique `sessionId` for each interview session
- Store conversation history
- Store questions asked
- Store curriculum days covered
- Store the candidate profile associated with the session
- Store interview progress
- Use an in-memory session manager
- Keep the implementation modular
- Reuse the existing candidate and curriculum models and services
- Preserve the existing project functionality
- Use appropriate type-safe models and domain-specific exceptions
- Provide operations for creating, retrieving, updating and removing sessions
- Handle unknown session IDs appropriately
- Keep session data isolated between different interview sessions
- Add automated tests for the session management functionality
- Do not implement LLM generation, adaptive questioning, scoring or evaluation functionality at this stage

### AI Response / Output

Arena Agent inspected the existing backend architecture and implemented the requested interview session management functionality.

The implementation included:

- Added `backend/app/models/session.py`
- Added `backend/app/services/session_service.py`
- Added `backend/tests/test_session.py`
- Added `SessionNotFoundError` to `backend/app/exceptions.py`
- Updated `backend/app/models/__init__.py`
- Updated `backend/app/services/__init__.py`

The session models include:

- `InterviewSession`
- `ConversationMessage`
- `QuestionAsked`
- `InterviewProgress`
- `InterviewStatus`

The `SessionManager` provides an in-memory session store with session creation, retrieval, updates, completion, removal and clearing operations.

Each session receives a unique UUID-based `sessionId` by default.

The session manager stores the candidate profile, conversation history, questions asked, curriculum days covered and interview progress.

Adding questions automatically tracks the associated curriculum day, while session mutations update the session timestamp.

### Where It Was Used

The session management implementation provides the state-management layer for interview sessions in the AI Interviewer backend.

It maintains the state required to continue an interview session, including the candidate context, conversation history, questions asked, curriculum coverage and current interview progress.

The in-memory design keeps the implementation lightweight and modular while providing a foundation for connecting the interview API and AI functionality in later development.

### Human Review

The generated changes were reviewed in Arena Agent against the existing FastAPI architecture and the requirements for session management.

The newly created session models, session manager service, exception handling, package exports and automated tests were reviewed before accepting the implementation.

The complete backend test suite was executed after implementation.

All **72 automated tests passed successfully**, including:

- 26 existing data model and service tests
- 46 new session management tests

The tests covered session creation, unique session IDs, candidate association, session retrieval, conversation history, questions asked, curriculum day tracking, interview progress, session completion and removal, error handling and session isolation.

### Vibe Coding Workflow

Arena Agent was used to inspect the existing repository and generate the session management implementation from the defined requirements.

The generated code was then reviewed and tested before being accepted into the project.

The workflow followed an iterative AI-assisted development process:

**Prompt → Repository inspection → AI-generated implementation → Human review → Automated testing**

The implementation was accepted after the complete backend test suite passed successfully.
