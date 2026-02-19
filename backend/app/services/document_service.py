"""
aitema|RIS - Document Management Service
Handles file upload, download, versioning via MinIO.
"""
from __future__ import annotations

import hashlib
import io
import uuid
from datetime import date, datetime, timezone
from typing import BinaryIO, Optional

import structlog
from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


class DocumentService:
    """
    Service for managing documents stored in MinIO.
    Handles uploads, downloads, versioning, and checksum verification.
    """

    def __init__(self) -> None:
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    async def ensure_bucket(self) -> None:
        """Create the storage bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("Created MinIO bucket", bucket=self.bucket)
        except S3Error as e:
            logger.error("Failed to ensure bucket", error=str(e))
            raise

    def _generate_storage_key(
        self, tenant_schema: str, file_name: str, version: int = 1
    ) -> str:
        """Generate a structured storage key for a file."""
        unique_id = uuid.uuid4().hex[:12]
        return f"{tenant_schema}/{date.today().isoformat()}/{unique_id}/v{version}/{file_name}"

    def _compute_checksums(self, data: bytes) -> tuple[str, str]:
        """Compute SHA-1 and SHA-512 checksums."""
        sha1 = hashlib.sha1(data).hexdigest()
        sha512 = hashlib.sha512(data).hexdigest()
        return sha1, sha512

    async def upload_file(
        self,
        file_data: BinaryIO,
        file_name: str,
        mime_type: str,
        tenant_schema: str,
        size: int,
    ) -> dict:
        """
        Upload a file to MinIO storage.

        Returns a dict with storage_key, checksums, and size.
        """
        await self.ensure_bucket()

        # Read data for checksum computation
        data = file_data.read()
        actual_size = len(data)
        sha1, sha512 = self._compute_checksums(data)

        storage_key = self._generate_storage_key(tenant_schema, file_name)

        try:
            self.client.put_object(
                self.bucket,
                storage_key,
                io.BytesIO(data),
                length=actual_size,
                content_type=mime_type,
                metadata={
                    "original-filename": file_name,
                    "tenant": tenant_schema,
                    "uploaded-at": datetime.now(timezone.utc).isoformat(),
                    "sha512": sha512,
                },
            )
            logger.info(
                "File uploaded",
                storage_key=storage_key,
                size=actual_size,
                mime_type=mime_type,
            )
        except S3Error as e:
            logger.error("File upload failed", error=str(e))
            raise

        return {
            "storage_key": storage_key,
            "file_name": file_name,
            "mime_type": mime_type,
            "size": actual_size,
            "sha1_checksum": sha1,
            "sha512_checksum": sha512,
        }

    async def download_file(self, storage_key: str) -> tuple[BinaryIO, str, int]:
        """
        Download a file from MinIO storage.

        Returns (file_data, content_type, size).
        """
        try:
            response = self.client.get_object(self.bucket, storage_key)
            data = response.read()
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            return io.BytesIO(data), content_type, len(data)
        except S3Error as e:
            logger.error("File download failed", storage_key=storage_key, error=str(e))
            raise
        finally:
            if "response" in locals():
                response.close()
                response.release_conn()

    async def delete_file(self, storage_key: str) -> None:
        """Delete a file from MinIO storage."""
        try:
            self.client.remove_object(self.bucket, storage_key)
            logger.info("File deleted", storage_key=storage_key)
        except S3Error as e:
            logger.error("File deletion failed", storage_key=storage_key, error=str(e))
            raise

    async def get_presigned_url(
        self, storage_key: str, expires_hours: int = 1
    ) -> str:
        """Generate a presigned URL for direct file download."""
        from datetime import timedelta
        try:
            url = self.client.presigned_get_object(
                self.bucket,
                storage_key,
                expires=timedelta(hours=expires_hours),
            )
            return url
        except S3Error as e:
            logger.error("Presigned URL generation failed", error=str(e))
            raise

    async def upload_version(
        self,
        file_data: BinaryIO,
        file_name: str,
        mime_type: str,
        tenant_schema: str,
        version: int,
        original_key: str,
    ) -> dict:
        """Upload a new version of an existing file."""
        await self.ensure_bucket()

        data = file_data.read()
        actual_size = len(data)
        sha1, sha512 = self._compute_checksums(data)

        # Use a versioned path based on the original key
        base_path = "/".join(original_key.split("/")[:-1])
        storage_key = f"{base_path}/v{version}/{file_name}"

        try:
            self.client.put_object(
                self.bucket,
                storage_key,
                io.BytesIO(data),
                length=actual_size,
                content_type=mime_type,
                metadata={
                    "original-filename": file_name,
                    "tenant": tenant_schema,
                    "version": str(version),
                    "uploaded-at": datetime.now(timezone.utc).isoformat(),
                    "sha512": sha512,
                },
            )
        except S3Error as e:
            logger.error("Version upload failed", error=str(e))
            raise

        return {
            "storage_key": storage_key,
            "file_name": file_name,
            "mime_type": mime_type,
            "size": actual_size,
            "sha1_checksum": sha1,
            "sha512_checksum": sha512,
            "version": version,
        }

    async def copy_file(self, source_key: str, dest_key: str) -> None:
        """Copy a file within MinIO."""
        from minio.commonconfig import CopySource
        try:
            self.client.copy_object(
                self.bucket,
                dest_key,
                CopySource(self.bucket, source_key),
            )
        except S3Error as e:
            logger.error("File copy failed", error=str(e))
            raise
