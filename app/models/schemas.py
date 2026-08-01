"""
Pydantic models for API request and response schemas.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        description="The user's message",
        min_length=1,
        max_length=4000
    )

    thread_id: Optional[str] = Field(
        None,
        description="Conversation thread ID for context"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(
        ...,
        description="The assistant's response"
    )

    thread_id: str = Field(
        ...,
        description="The conversation thread ID"
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(
        ...,
        description="Overall application status"
    )

    vector_db: str = Field(
        ...,
        description="Vector database connection status"
    )

    state_db: str = Field(
        ...,
        description="State database connection status"
    )

    openai_api: str = Field(
        ...,
        description="OpenAI API availability status"
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Health check timestamp"
    )