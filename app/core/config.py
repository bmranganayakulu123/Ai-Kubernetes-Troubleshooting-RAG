"""
Configuration management for the LangChain RAG Chatbot application.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# Project Configuration
# ============================================================

# Get the project root directory
# Parent of the app/ directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

ENV_FILE = PROJECT_ROOT / ".env"


# ============================================================
# Load Environment Variables
# ============================================================

if ENV_FILE.exists():
    load_dotenv(
        dotenv_path=ENV_FILE,
        override=True
    )


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        """Initialize settings from environment variables."""

        # ====================================================
        # OpenAI Configuration
        # ====================================================

        self.openai_api_key = self._get_required("OPENAI_API_KEY")


        # ====================================================
        # Database Configuration
        # ====================================================

        # PostgreSQL database for PGVector
        self.vector_db_url = self._get_required(
            "VECTOR_DB_CONNECTION_STRING"
        )

        # PostgreSQL database for LangGraph state/checkpoints
        self.state_db_url = self._get_required(
            "CONVERSATION_DB_CONNECTION_STRING"
        )


        # ====================================================
        # AWS S3 Configuration
        # ====================================================

        # AWS Region
        self.aws_region = os.getenv(
            "AWS_REGION",
            "ap-south-1"
        )

        # AWS S3 Bucket
        self.aws_s3_bucket = self._get_required(
            "AWS_S3_BUCKET_NAME"
        )

        # Optional AWS credentials.
        #
        # Recommended:
        # Use IAM Role when running on EC2/ECS/EKS.
        #
        # For local development, boto3 can use these
        # credentials from the .env file.

        self.aws_access_key_id = os.getenv(
            "AWS_ACCESS_KEY_ID"
        )

        self.aws_secret_access_key = os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        )


        # ====================================================
        # Application Configuration
        # ====================================================

        self.app_host = os.getenv(
            "APP_HOST",
            "0.0.0.0"
        )

        self.app_port = int(
            os.getenv(
                "APP_PORT",
                "8000"
            )
        )


        # ====================================================
        # Logging Configuration
        # ====================================================

        self.log_level = os.getenv(
            "LOG_LEVEL",
            "INFO"
        )


        # ====================================================
        # RAG Configuration
        # ====================================================

        self.chunk_size = int(
            os.getenv(
                "CHUNK_SIZE",
                "1000"
            )
        )

        self.chunk_overlap = int(
            os.getenv(
                "CHUNK_OVERLAP",
                "200"
            )
        )

        self.retrieval_k = int(
            os.getenv(
                "RETRIEVAL_K",
                "10"
            )
        )


        # ====================================================
        # OpenAI Model Configuration
        # ====================================================

        self.llm_model = os.getenv(
            "LLM_MODEL", 
            "gpt-4.1-mini",
        )
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "text-embedding-3-small",
        )


        # ====================================================
        # Admin API Configuration
        # ====================================================

        self.admin_api_key = self._get_required(
            "ADMIN_API_KEY"
        )


    # ========================================================
    # Helper Methods
    # ========================================================

    def _get_required(
        self,
        env_var: str
    ) -> str:
        """
        Get a required environment variable.

        Raises:
            ValueError:
                If the environment variable is not set.
        """

        value = os.getenv(
            env_var
        )

        if not value:
            raise ValueError(
                f"Required environment variable "
                f"{env_var} is not set"
            )

        return value


# ============================================================
# Global Settings Instance
# ============================================================

settings = Settings()


def get_settings() -> Settings:
    """Get the application settings instance."""

    return settings


# ============================================================
# Environment Validation
# ============================================================

def validate_environment() -> bool:
    """
    Validate that all required environment variables
    are set.
    """

    import logging

    logger = logging.getLogger(
        __name__
    )

    required_vars = [

        # OpenAI
        "OPENAI_API_KEY",

        # PostgreSQL
        "VECTOR_DB_CONNECTION_STRING",
        "CONVERSATION_DB_CONNECTION_STRING",

        # AWS S3
        "AWS_REGION",
        "AWS_S3_BUCKET_NAME",

        # Admin API
        "ADMIN_API_KEY"

    ]

    logger.info(
        "Validating environment variables..."
    )

    logger.debug(
        f"Checking for "
        f"{len(required_vars)} "
        f"required environment variables"
    )

    missing_vars = []
    found_vars = []

    for var in required_vars:

        value = os.getenv(
            var
        )

        if value:

            found_vars.append(
                var
            )

            # Mask sensitive values
            if (
                "KEY" in var
                or "SECRET" in var
                or "PASSWORD" in var
                or "CONNECTION_STRING" in var
            ):

                masked = (
                    value[:20] + "..."
                    if len(value) > 20
                    else "***"
                )

                logger.debug(
                    f"✓ {var}: "
                    f"{masked} "
                    f"(length: {len(value)})"
                )

            else:

                logger.debug(
                    f"✓ {var}: "
                    f"{value}"
                )

        else:

            missing_vars.append(
                var
            )

            logger.warning(
                f"✗ {var}: NOT SET"
            )

    logger.info(
        f"Found "
        f"{len(found_vars)}/"
        f"{len(required_vars)} "
        f"required environment variables"
    )

    if missing_vars:

        logger.error(
            "Missing required environment variables: "
            + ", ".join(
                missing_vars
            )
        )

        return False

    logger.info(
        "All required environment variables "
        "are set"
    )

    return True