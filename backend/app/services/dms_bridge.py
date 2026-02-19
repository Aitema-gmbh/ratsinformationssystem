"""
aitema|RIS - DMS Bridge
Abstract interface for Document Management System integration.
Includes a d.velop adapter for d.velop d.3 / d.velop documents.
"""
from __future__ import annotations

import abc
from typing import Any, BinaryIO, Optional

import httpx
import structlog

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


class DMSDocument:
    """Represents a document in the external DMS."""

    def __init__(
        self,
        dms_id: str,
        title: str,
        category: str | None = None,
        mime_type: str | None = None,
        size: int | None = None,
        url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.dms_id = dms_id
        self.title = title
        self.category = category
        self.mime_type = mime_type
        self.size = size
        self.url = url
        self.metadata = metadata or {}


class DMSBridge(abc.ABC):
    """
    Abstract DMS bridge interface.
    Implement this for each supported DMS system.
    """

    @abc.abstractmethod
    async def search(
        self, query: str, category: str | None = None, max_results: int = 50
    ) -> list[DMSDocument]:
        """Search for documents in the DMS."""
        ...

    @abc.abstractmethod
    async def get_document(self, dms_id: str) -> DMSDocument | None:
        """Get document metadata by DMS ID."""
        ...

    @abc.abstractmethod
    async def download_document(self, dms_id: str) -> tuple[BinaryIO, str, int] | None:
        """Download document content. Returns (data, mime_type, size) or None."""
        ...

    @abc.abstractmethod
    async def upload_document(
        self,
        file_data: BinaryIO,
        file_name: str,
        mime_type: str,
        metadata: dict[str, Any],
    ) -> DMSDocument:
        """Upload a document to the DMS."""
        ...

    @abc.abstractmethod
    async def link_document(self, dms_id: str, oparl_file_id: str) -> bool:
        """Create a bidirectional link between DMS doc and OParl file."""
        ...

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Check if the DMS connection is healthy."""
        ...


class NullDMSBridge(DMSBridge):
    """No-op DMS bridge when no DMS is configured."""

    async def search(self, query: str, category: str | None = None, max_results: int = 50) -> list[DMSDocument]:
        return []

    async def get_document(self, dms_id: str) -> DMSDocument | None:
        return None

    async def download_document(self, dms_id: str) -> tuple[BinaryIO, str, int] | None:
        return None

    async def upload_document(self, file_data: BinaryIO, file_name: str, mime_type: str, metadata: dict[str, Any]) -> DMSDocument:
        raise NotImplementedError("No DMS configured")

    async def link_document(self, dms_id: str, oparl_file_id: str) -> bool:
        return False

    async def health_check(self) -> bool:
        return True


class DvelopDMSBridge(DMSBridge):
    """
    d.velop DMS adapter.
    Integrates with d.velop d.3 / d.velop documents REST API.
    https://developer.d-velop.de/documentation/dmsapi
    """

    def __init__(self) -> None:
        self.base_url = settings.dms_dvelop_base_url.rstrip("/")
        self.api_key = settings.dms_dvelop_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/hal+json",
        }

    async def _request(
        self, method: str, path: str, **kwargs
    ) -> httpx.Response:
        """Make an authenticated request to the d.velop API."""
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method,
                f"{self.base_url}{path}",
                headers=self.headers,
                timeout=30.0,
                **kwargs,
            )
            resp.raise_for_status()
            return resp

    async def search(
        self, query: str, category: str | None = None, max_results: int = 50
    ) -> list[DMSDocument]:
        """Search documents in d.velop DMS."""
        params = {
            "searchexpression": query,
            "maxresults": max_results,
        }
        if category:
            params["category"] = category

        try:
            resp = await self._request(
                "GET", "/dms/r/search", params=params
            )
            data = resp.json()

            documents = []
            for item in data.get("items", []):
                props = item.get("sourceProperties", {})
                doc = DMSDocument(
                    dms_id=item.get("id", ""),
                    title=props.get("property_filename", ""),
                    category=props.get("property_category", ""),
                    mime_type=props.get("property_filetype", ""),
                    url=item.get("_links", {}).get("mainblobcontent", {}).get("href"),
                    metadata=props,
                )
                documents.append(doc)

            return documents
        except Exception as e:
            logger.error("d.velop search failed", error=str(e))
            return []

    async def get_document(self, dms_id: str) -> DMSDocument | None:
        """Get document metadata from d.velop."""
        try:
            resp = await self._request("GET", f"/dms/r/{dms_id}")
            data = resp.json()
            props = data.get("sourceProperties", {})

            return DMSDocument(
                dms_id=dms_id,
                title=props.get("property_filename", ""),
                category=props.get("property_category", ""),
                mime_type=props.get("property_filetype", ""),
                url=data.get("_links", {}).get("mainblobcontent", {}).get("href"),
                metadata=props,
            )
        except Exception as e:
            logger.error("d.velop get_document failed", dms_id=dms_id, error=str(e))
            return None

    async def download_document(self, dms_id: str) -> tuple[BinaryIO, str, int] | None:
        """Download document content from d.velop."""
        import io

        doc = await self.get_document(dms_id)
        if not doc or not doc.url:
            return None

        try:
            resp = await self._request("GET", doc.url)
            data = resp.content
            mime_type = resp.headers.get("content-type", "application/octet-stream")
            return io.BytesIO(data), mime_type, len(data)
        except Exception as e:
            logger.error("d.velop download failed", dms_id=dms_id, error=str(e))
            return None

    async def upload_document(
        self,
        file_data: BinaryIO,
        file_name: str,
        mime_type: str,
        metadata: dict[str, Any],
    ) -> DMSDocument:
        """Upload a document to d.velop DMS."""
        try:
            # Create document entry
            create_resp = await self._request(
                "POST",
                "/dms/r",
                json={
                    "sourceProperties": {
                        "property_filename": file_name,
                        **metadata,
                    }
                },
            )
            doc_data = create_resp.json()
            dms_id = doc_data.get("id", "")

            # Upload blob
            blob_url = doc_data.get("_links", {}).get("mainblobcontent", {}).get("href", "")
            if blob_url:
                await self._request(
                    "PUT",
                    blob_url,
                    content=file_data.read(),
                    headers={**self.headers, "Content-Type": mime_type},
                )

            return DMSDocument(
                dms_id=dms_id,
                title=file_name,
                mime_type=mime_type,
                metadata=metadata,
            )
        except Exception as e:
            logger.error("d.velop upload failed", error=str(e))
            raise

    async def link_document(self, dms_id: str, oparl_file_id: str) -> bool:
        """Store a link between d.velop doc and OParl file in both systems."""
        try:
            await self._request(
                "PATCH",
                f"/dms/r/{dms_id}",
                json={
                    "sourceProperties": {
                        "property_custom_oparl_id": oparl_file_id,
                    }
                },
            )
            return True
        except Exception as e:
            logger.error("d.velop link failed", dms_id=dms_id, error=str(e))
            return False

    async def health_check(self) -> bool:
        """Check d.velop API connectivity."""
        try:
            resp = await self._request("GET", "/dms")
            return resp.status_code == 200
        except Exception:
            return False


def get_dms_bridge() -> DMSBridge:
    """Factory function to get the configured DMS bridge."""
    if settings.dms_type == "dvelop":
        return DvelopDMSBridge()
    return NullDMSBridge()
