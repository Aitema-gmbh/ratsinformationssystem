"""
aitema|RIS - Search Service
Elasticsearch integration for full-text search across all OParl objects.
"""
from __future__ import annotations

from typing import Any, Optional

import structlog
from elasticsearch import AsyncElasticsearch

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

# Index mappings for German-language full-text search
OPARL_INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "analyzer": {
                "german_custom": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "german_normalization",
                        "german_stemmer",
                        "german_stop",
                    ],
                },
                "german_exact": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                },
            },
            "filter": {
                "german_stemmer": {
                    "type": "stemmer",
                    "language": "light_german",
                },
                "german_stop": {
                    "type": "stop",
                    "stopwords": "_german_",
                },
            },
        },
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "oparl_type": {"type": "keyword"},
            "oparl_id": {"type": "keyword"},
            "body_id": {"type": "keyword"},
            "tenant": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "german_custom",
                "fields": {
                    "exact": {"type": "text", "analyzer": "german_exact"},
                    "keyword": {"type": "keyword"},
                },
            },
            "reference": {"type": "keyword"},
            "content": {
                "type": "text",
                "analyzer": "german_custom",
            },
            "paper_type": {"type": "keyword"},
            "organization_type": {"type": "keyword"},
            "date": {"type": "date"},
            "start": {"type": "date"},
            "created": {"type": "date"},
            "modified": {"type": "date"},
            "keywords": {"type": "keyword"},
            "persons": {"type": "keyword"},
            "organizations": {"type": "keyword"},
        }
    },
}


class SearchService:
    """
    Full-text search service using Elasticsearch.
    Indexes and searches all OParl objects with German language analysis.
    """

    def __init__(self) -> None:
        auth_kwargs = {}
        if settings.es_password:
            auth_kwargs["basic_auth"] = ("elastic", settings.es_password)

        self.client = AsyncElasticsearch(
            settings.elasticsearch_url,
            **auth_kwargs,
        )
        self.index_prefix = settings.es_index_prefix

    @property
    def index_name(self) -> str:
        return f"{self.index_prefix}-oparl"

    async def ensure_index(self) -> None:
        """Create the search index if it doesn't exist."""
        exists = await self.client.indices.exists(index=self.index_name)
        if not exists:
            await self.client.indices.create(
                index=self.index_name,
                body=OPARL_INDEX_SETTINGS,
            )
            logger.info("Created ES index", index=self.index_name)

    async def index_document(
        self,
        doc_id: str,
        oparl_type: str,
        body: dict[str, Any],
        tenant: str = "public",
    ) -> None:
        """Index a single OParl document for search."""
        await self.ensure_index()

        doc = {
            "oparl_type": oparl_type,
            "oparl_id": doc_id,
            "tenant": tenant,
            **body,
        }

        await self.client.index(
            index=self.index_name,
            id=doc_id,
            document=doc,
        )

    async def delete_document(self, doc_id: str) -> None:
        """Remove a document from the search index."""
        try:
            await self.client.delete(index=self.index_name, id=doc_id)
        except Exception:
            logger.warning("Failed to delete from index", doc_id=doc_id)

    async def search(
        self,
        query: str,
        object_type: Optional[str] = None,
        body_id: Optional[str] = None,
        tenant: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict:
        """
        Perform a full-text search across all OParl objects.

        Supports filtering by object type, body, and tenant.
        Returns ranked results with highlights.
        """
        must_clauses = [
            {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^3",
                        "name.exact^2",
                        "reference^4",
                        "content",
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            }
        ]

        filter_clauses = []
        if object_type:
            filter_clauses.append({"term": {"oparl_type": object_type}})
        if body_id:
            filter_clauses.append({"term": {"body_id": body_id}})
        if tenant:
            filter_clauses.append({"term": {"tenant": tenant}})

        es_query = {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        }

        try:
            result = await self.client.search(
                index=self.index_name,
                query=es_query,
                from_=(page - 1) * per_page,
                size=per_page,
                highlight={
                    "fields": {
                        "name": {"number_of_fragments": 1},
                        "content": {"number_of_fragments": 3, "fragment_size": 200},
                    },
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"],
                },
                sort=[
                    "_score",
                    {"modified": {"order": "desc", "missing": "_last"}},
                ],
            )
        except Exception as e:
            logger.error("Search failed", error=str(e), query=query)
            return {"data": [], "total": 0, "page": page, "per_page": per_page}

        hits = result["hits"]
        total = hits["total"]["value"] if isinstance(hits["total"], dict) else hits["total"]

        data = []
        for hit in hits["hits"]:
            item = {
                "id": hit["_source"].get("oparl_id"),
                "type": hit["_source"].get("oparl_type"),
                "name": hit["_source"].get("name"),
                "reference": hit["_source"].get("reference"),
                "score": hit["_score"],
            }
            if "highlight" in hit:
                item["highlight"] = hit["highlight"]
            data.append(item)

        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    async def reindex_all(self, objects: list[dict]) -> int:
        """Bulk reindex all OParl objects."""
        from elasticsearch.helpers import async_bulk

        await self.ensure_index()

        actions = []
        for obj in objects:
            actions.append({
                "_index": self.index_name,
                "_id": obj["oparl_id"],
                "_source": obj,
            })

        success, errors = await async_bulk(self.client, actions)
        logger.info("Reindex complete", success=success, errors=len(errors))
        return success

    async def close(self) -> None:
        """Close the Elasticsearch client."""
        await self.client.close()
