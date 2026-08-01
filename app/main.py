"""
Main FastAPI application for the LangChain RAG Chatbot.

Application stack:
- FastAPI
- LangChain / LangGraph
- OpenAI
- AWS S3
- PostgreSQL + PGVector
- Persistent conversation memory
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, chat, health
from app.core.config import get_settings, validate_environment
from app.core.memory import initialize_conversation_memory
from app.core.rag import initialize_rag_pipeline


# -------------------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

settings = get_settings()


# -------------------------------------------------------------------
# Project Paths
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "app" / "static"
INDEX_FILE = STATIC_DIR / "index.html"


# -------------------------------------------------------------------
# Application Lifespan
# -------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
    1. Validate environment variables.
    2. Initialize RAG pipeline.
    3. Initialize conversation memory.

    Shutdown:
    1. Log application shutdown.
    """

    logger.info("=" * 60)
    logger.info("Starting LangChain RAG Chatbot application")
    logger.info("=" * 60)

    # ---------------------------------------------------------------
    # Step 1: Validate Environment
    # ---------------------------------------------------------------

    logger.info("Validating environment variables...")

    if not validate_environment():
        logger.error(
            "Environment validation failed. "
            "Please check your .env configuration."
        )
        raise RuntimeError(
            "Missing required environment variables."
        )

    logger.info("Environment validation completed successfully.")

    # ---------------------------------------------------------------
    # Step 2: Initialize RAG Pipeline
    # ---------------------------------------------------------------

    try:
        logger.info("Initializing RAG pipeline...")

        initialize_rag_pipeline()

        logger.info(
            "RAG pipeline initialized successfully."
        )

    except Exception as exc:
        logger.exception(
            "Failed to initialize RAG pipeline: %s",
            exc,
        )
        raise

    # ---------------------------------------------------------------
    # Step 3: Initialize Conversation Memory
    # ---------------------------------------------------------------

    try:
        logger.info(
            "Initializing conversation memory..."
        )

        initialize_conversation_memory()

        logger.info(
            "Conversation memory initialized successfully."
        )

    except Exception as exc:
        logger.exception(
            "Failed to initialize conversation memory: %s",
            exc,
        )
        raise

    logger.info("=" * 60)
    logger.info(
        "Application startup completed successfully."
    )
    logger.info(
        "Server: http://%s:%s",
        settings.app_host,
        settings.app_port,
    )
    logger.info("=" * 60)

    yield

    # ---------------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------------

    logger.info(
        "Shutting down LangChain RAG Chatbot application..."
    )

    logger.info(
        "Application shutdown completed."
    )


# -------------------------------------------------------------------
# Create FastAPI Application
# -------------------------------------------------------------------

app = FastAPI(
    title="Devops Operations RAG Chatbot",
    description=(
        "Production-ready RAG chatbot using "
        "LangChain, LangGraph, OpenAI, "
        "AWS S3, and PostgreSQL PGVector."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# -------------------------------------------------------------------
# CORS Configuration
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    # For development.
    # In production, replace "*" with your frontend domain.
    allow_origins=["*"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Exception Handlers
# -------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Handle FastAPI request validation errors.
    """

    logger.error(
        "Request validation error on %s: %s",
        request.url.path,
        exc,
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Invalid request data.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    """
    Handle HTTP exceptions.
    """

    logger.error(
        "HTTP error %s on %s: %s",
        exc.status_code,
        request.url.path,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Handle unexpected application exceptions.
    """

    logger.exception(
        "Unhandled exception on %s: %s",
        request.url.path,
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": (
                "An unexpected error occurred."
            ),
        },
    )


# -------------------------------------------------------------------
# API Routers
# -------------------------------------------------------------------

app.include_router(
    chat.router,
    prefix="/api",
    tags=["Chat"],
)

app.include_router(
    health.router,
    prefix="/api",
    tags=["Health"],
)

app.include_router(
    admin.router,
    prefix="/api",
    tags=["Admin"],
)


# -------------------------------------------------------------------
# Static Files
# -------------------------------------------------------------------

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )

    logger.info(
        "Static files mounted from: %s",
        STATIC_DIR,
    )
else:
    logger.warning(
        "Static directory not found: %s",
        STATIC_DIR,
    )


# -------------------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def root():
    """
    Serve the main Devops Operations RAG Chatbot interface.
    """

    try:
        if INDEX_FILE.exists():
            return HTMLResponse(
                content=INDEX_FILE.read_text(
                    encoding="utf-8"
                )
            )

        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Devops Operations RAG Chatbot</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        background: #f8fafc;
                    }

                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: white;
                        padding: 30px;
                        border-radius: 12px;
                    }

                    h1 {
                        color: #017ac6;
                    }

                    .status {
                        background: #f0f8ff;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }

                    .endpoints {
                        background: #f9f9f9;
                        padding: 20px;
                        border-radius: 8px;
                    }

                    .endpoint {
                        margin: 10px 0;
                    }

                    code {
                        background: #e8e8e8;
                        padding: 2px 6px;
                        border-radius: 4px;
                    }
                </style>
            </head>

            <body>
                <div class="container">

                    <h1>
                        Devops Operations RAG Chatbot
                    </h1>

                    <div class="status">
                        <h2>
                            Application Status
                        </h2>

                        <p>
                            Application is running successfully.
                        </p>

                        <p>
                            OpenAI RAG pipeline initialized.
                        </p>

                        <p>
                            Conversation memory enabled.
                        </p>

                        <p>
                            AWS S3 document storage configured.
                        </p>

                        <p>
                            PostgreSQL PGVector configured.
                        </p>
                    </div>

                    <div class="endpoints">

                        <h2>
                            Available Endpoints
                        </h2>

                        <div class="endpoint">
                            <strong>POST</strong>
                            <code>/api/chat</code>
                            - Send a chat message
                        </div>

                        <div class="endpoint">
                            <strong>GET</strong>
                            <code>/api/health</code>
                            - Check application health
                        </div>

                        <div class="endpoint">
                            <strong>GET</strong>
                            <code>/api/conversation/{thread_id}</code>
                            - Get conversation history
                        </div>

                        <div class="endpoint">
                            <strong>DELETE</strong>
                            <code>/api/conversation/{thread_id}</code>
                            - Clear conversation history
                        </div>

                        <div class="endpoint">
                            <strong>GET</strong>
                            <code>/docs</code>
                            - Open Swagger API documentation
                        </div>

                    </div>

                    <p>
                        Open the chatbot at:
                        <a href="/">
                            Devops Operations RAG Chatbot
                        </a>
                    </p>

                </div>
            </body>
            </html>
            """,
        )

    except Exception as exc:

        logger.exception(
            "Failed to serve root page: %s",
            exc,
        )

        return HTMLResponse(
            content=(
                "<h1>Error loading application</h1>"
            ),
            status_code=500,
        )


# -------------------------------------------------------------------
# Server Startup
# -------------------------------------------------------------------

def main():
    """
    Main entry point for running the FastAPI application.
    """

    logger.info(
        "Starting server on %s:%s",
        settings.app_host,
        settings.app_port,
    )

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,
        log_level=settings.log_level.lower(),
    )


# -------------------------------------------------------------------
# Run Application
# -------------------------------------------------------------------

if __name__ == "__main__":
    main()