"""
Lightweight document loader for AWS S3.

Supported document types:
- PDF: pypdf
- HTML: BeautifulSoup4
- TXT: Direct reading
"""

import io
import logging
from typing import List

import boto3
from botocore.exceptions import ClientError

from langchain_core.documents import Document
from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.core.config import get_settings


logger = logging.getLogger(__name__)


class S3DocumentLoader:
    """
    Lightweight document loader for AWS S3.

    Downloads documents from an AWS S3 bucket and parses:
    - PDF files using pypdf
    - HTML files using BeautifulSoup4
    - TXT files using UTF-8 decoding
    """

    def __init__(self):
        """
        Initialize the AWS S3 client.

        AWS credentials are automatically discovered by boto3.

        For local development:
            AWS_ACCESS_KEY_ID
            AWS_SECRET_ACCESS_KEY

        For AWS EC2/ECS/EKS:
            Use an IAM Role instead of hardcoded credentials.
        """

        self.settings = get_settings()

        # --------------------------------------------------
        # AWS S3 Client
        # --------------------------------------------------

        self.s3_client = boto3.client(
            "s3",
            region_name=self.settings.aws_region
        )

        # --------------------------------------------------
        # S3 Bucket
        # --------------------------------------------------

        self.bucket = self.settings.aws_s3_bucket

        logger.info(
            f"AWS S3 Document Loader initialized "
            f"for bucket: {self.bucket}"
        )


    def load(
        self,
        key: str
    ) -> List[Document]:
        """
        Download and parse a document from AWS S3.

        Args:
            key:
                S3 object key, for example:
                "document.pdf"

        Returns:
            List of LangChain Document objects.
        """

        try:

            logger.info(
                f"Downloading document from AWS S3: {key}"
            )

            # --------------------------------------------------
            # Download file from AWS S3
            # --------------------------------------------------

            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=key
            )

            file_content = (
                response["Body"].read()
            )

            logger.info(
                f"Successfully downloaded "
                f"{key} from AWS S3"
            )

            # --------------------------------------------------
            # Determine file extension
            # --------------------------------------------------

            file_ext = ""

            if "." in key:
                file_ext = (
                    key.rsplit(
                        ".",
                        1
                    )[1]
                    .lower()
                )

            # --------------------------------------------------
            # Parse document based on type
            # --------------------------------------------------

            if file_ext == "pdf":

                return self._parse_pdf(
                    file_content,
                    key
                )

            elif file_ext in (
                "html",
                "htm"
            ):

                return self._parse_html(
                    file_content,
                    key
                )

            elif file_ext == "txt":

                return self._parse_text(
                    file_content,
                    key
                )

            else:

                logger.warning(
                    f"Unsupported file type "
                    f"for {key}. "
                    f"Attempting to parse as text."
                )

                return self._parse_text(
                    file_content,
                    key
                )

        except ClientError as e:

            error_code = (
                e.response
                .get("Error", {})
                .get(
                    "Code",
                    "Unknown"
                )
            )

            logger.error(
                f"Failed to download "
                f"{key} from AWS S3. "
                f"Error: {error_code}. "
                f"Details: {e}"
            )

            raise

        except Exception as e:

            logger.error(
                f"Failed to load and parse "
                f"{key}: {e}",
                exc_info=True
            )

            raise


    def _parse_pdf(
        self,
        content: bytes,
        source: str
    ) -> List[Document]:
        """
        Parse PDF content using pypdf.

        Args:
            content:
                PDF file content as bytes.

            source:
                S3 object key.

        Returns:
            List containing a LangChain Document.
        """

        try:

            logger.info(
                f"Parsing PDF: {source}"
            )

            pdf_file = io.BytesIO(
                content
            )

            pdf_reader = PdfReader(
                pdf_file
            )

            full_text = []

            # --------------------------------------------------
            # Extract text from every page
            # --------------------------------------------------

            for page_num, page in enumerate(
                pdf_reader.pages,
                start=1
            ):

                try:

                    page_text = (
                        page.extract_text()
                    )

                    if (
                        page_text
                        and page_text.strip()
                    ):

                        full_text.append(
                            page_text.strip()
                        )

                except Exception as e:

                    logger.warning(
                        f"Failed to extract "
                        f"text from page "
                        f"{page_num} of "
                        f"{source}: {e}"
                    )

                    continue

            # --------------------------------------------------
            # Create LangChain Document
            # --------------------------------------------------

            if full_text:

                combined_text = (
                    "\n\n".join(
                        full_text
                    )
                )

                document = Document(

                    page_content=
                        combined_text,

                    metadata={

                        "source":
                            source,

                        "file_type":
                            "pdf",

                        "page_count":
                            len(
                                pdf_reader.pages
                            )

                    }
                )

                logger.info(
                    f"Successfully parsed PDF: "
                    f"{source}"
                )

                return [
                    document
                ]

            # --------------------------------------------------
            # No text found
            # --------------------------------------------------

            logger.warning(
                f"No text extracted "
                f"from PDF: {source}"
            )

            return [
                Document(

                    page_content="",

                    metadata={

                        "source":
                            source,

                        "file_type":
                            "pdf",

                        "page_count":
                            len(
                                pdf_reader.pages
                            )

                    }
                )
            ]

        except Exception as e:

            logger.error(
                f"Failed to parse PDF "
                f"{source}: {e}",
                exc_info=True
            )

            raise


    def _parse_html(
        self,
        content: bytes,
        source: str
    ) -> List[Document]:
        """
        Parse HTML content using BeautifulSoup4.

        Args:
            content:
                HTML file content as bytes.

            source:
                S3 object key.

        Returns:
            List containing a LangChain Document.
        """

        try:

            logger.info(
                f"Parsing HTML: {source}"
            )

            # --------------------------------------------------
            # Decode HTML
            # --------------------------------------------------

            html_content = content.decode(
                "utf-8",
                errors="ignore"
            )

            # --------------------------------------------------
            # Parse HTML
            # --------------------------------------------------

            soup = BeautifulSoup(
                html_content,
                "html.parser"
            )

            # --------------------------------------------------
            # Remove scripts and styles
            # --------------------------------------------------

            for element in soup(
                [
                    "script",
                    "style"
                ]
            ):

                element.decompose()

            # --------------------------------------------------
            # Extract text
            # --------------------------------------------------

            text = soup.get_text(
                separator="\n",
                strip=True
            )

            # --------------------------------------------------
            # Clean empty lines
            # --------------------------------------------------

            lines = [

                line.strip()

                for line
                in text.split("\n")

                if line.strip()

            ]

            cleaned_text = "\n".join(
                lines
            )

            if not cleaned_text:

                logger.warning(
                    f"No text extracted "
                    f"from HTML: {source}"
                )

            return [

                Document(

                    page_content=
                        cleaned_text,

                    metadata={

                        "source":
                            source,

                        "file_type":
                            "html"

                    }

                )

            ]

        except Exception as e:

            logger.error(
                f"Failed to parse HTML "
                f"{source}: {e}",
                exc_info=True
            )

            raise


    def _parse_text(
        self,
        content: bytes,
        source: str
    ) -> List[Document]:
        """
        Parse plain text content.

        Args:
            content:
                Text file content as bytes.

            source:
                S3 object key.

        Returns:
            List containing a LangChain Document.
        """

        try:

            logger.info(
                f"Parsing text file: {source}"
            )

            # --------------------------------------------------
            # Decode text
            # --------------------------------------------------

            text = content.decode(
                "utf-8",
                errors="ignore"
            )

            # --------------------------------------------------
            # Check empty file
            # --------------------------------------------------

            if not text.strip():

                logger.warning(
                    f"Empty text file: {source}"
                )

            return [

                Document(

                    page_content=
                        text,

                    metadata={

                        "source":
                            source,

                        "file_type":
                            "txt"

                    }

                )

            ]

        except Exception as e:

            logger.error(
                f"Failed to parse text "
                f"{source}: {e}",
                exc_info=True
            )

            raise