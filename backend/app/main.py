from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import LLMConfigurationError, LLMServiceError, SessionNotFoundError
from app.routes import api_router
from app.routes.interviews import router as interview_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health and other v1 routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Interview endpoint at POST /api/interview (per technical specification)
    app.include_router(interview_router, prefix="/api")

    # Register exception handlers
    app.add_exception_handler(SessionNotFoundError, _session_not_found_handler)
    app.add_exception_handler(LLMConfigurationError, _llm_configuration_handler)
    app.add_exception_handler(LLMServiceError, _llm_service_handler)
    app.add_exception_handler(ValueError, _value_error_handler)

    return app


async def _session_not_found_handler(
    request: Request,
    exc: SessionNotFoundError,
) -> JSONResponse:
    """Return 404 for unknown session IDs."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


async def _llm_configuration_handler(
    request: Request,
    exc: LLMConfigurationError,
) -> JSONResponse:
    """Return 503 when the LLM service is misconfigured."""
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc)},
    )


async def _llm_service_handler(
    request: Request,
    exc: LLMServiceError,
) -> JSONResponse:
    """Return 502 when an LLM API call fails."""
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc)},
    )


async def _value_error_handler(
    request: Request,
    exc: ValueError,
) -> JSONResponse:
    """Return 409 for invalid state transitions (e.g. continuing a completed session)."""
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


app = create_app()
