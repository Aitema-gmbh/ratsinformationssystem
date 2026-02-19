"""
aitema|RIS - Elasticsearch Volltextsuche

Erweiterte Suche mit:
- index_document() - Paper, Meeting, Person in Elasticsearch indexieren
- search() - Multi-Index Suche mit Highlighting und Facetten
- suggest() - Autocomplete Suggestions
- reindex_all() - Vollstaendiger Reindex aller Objekte
- German Analyzer mit Stemming, Decompounding und Synonymen
"""
from __future__ import annotations

from typing import Any, Optional

import structlog
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

# ============================================================
# Index-Mapping fuer deutsche Sprache
# ============================================================
GERMAN_INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "analyzer": {
                "german_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "german_normalization",
                        "german_decompounder",
                        "german_stemmer",
                        "german_stop",
                    ],
                },
                "german_exact": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase"],
                },
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "german_normalization",
                        "autocomplete_filter",
                    ],
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
                "german_decompounder": {
                    "type": "dictionary_decompounder",
                    "word_list": [
                        "rat", "information", "system", "sitzung",
                        "beschluss", "vorlage", "antrag", "fraktion",
                        "ausschuss", "gemeinde", "verwaltung", "haushalt",
                        "buerger", "stadt", "bau", "planung", "umwelt",
                        "verkehr", "schule", "jugend", "sozial", "kultur",
                    ],
                },
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15,
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
                "analyzer": "german_analyzer",
                "fields": {
                    "exact": {"type": "text", "analyzer": "german_exact"},
                    "keyword": {"type": "keyword"},
                    "suggest": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "german_exact",
                    },
                },
            },
            "reference": {"type": "keyword"},
            "content": {
                "type": "text",
                "analyzer": "german_analyzer",
            },
            "paper_type": {"type": "keyword"},
            "organization_type": {"type": "keyword"},
            "meeting_state": {"type": "keyword"},
            "date": {"type": "date"},
            "start": {"type": "date"},
            "end": {"type": "date"},
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
    Elasticsearch-basierte Volltextsuche fuer alle OParl-Objekte.
    Unterstuetzt Multi-Index-Suche, Highlighting, Facetten und Autocomplete.
    """

    def __init__(self) -> None:
        auth_kwargs = {}
        if settings.es_password:
            auth_kwargs["basic_auth"] = ("elastic", settings.es_password)

        self.client = AsyncElasticsearch(
            settings.elasticsearch_url,
            **auth_kwargs,
        )
        self.index_name = f"{settings.es_index_prefix}-oparl"

    async def ensure_index(self) -> None:
        """Index anlegen falls nicht vorhanden."""
        exists = await self.client.indices.exists(index=self.index_name)
        if not exists:
            await self.client.indices.create(
                index=self.index_name,
                body=GERMAN_INDEX_SETTINGS,
            )
            logger.info("ES-Index erstellt", index=self.index_name)

    # ========================================
    # Indexierung
    # ========================================

    async def index_document(
        self,
        doc_id: str,
        oparl_type: str,
        body: dict[str, Any],
        tenant: str = "public",
    ) -> None:
        """Einzelnes OParl-Objekt (Paper, Meeting, Person) indexieren."""
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
        logger.debug("Dokument indexiert", doc_id=doc_id, type=oparl_type)

    async def delete_document(self, doc_id: str) -> None:
        """Dokument aus dem Index entfernen."""
        try:
            await self.client.delete(index=self.index_name, id=doc_id)
        except Exception:
            logger.warning("Loeschen aus Index fehlgeschlagen", doc_id=doc_id)

    # ========================================
    # Suche
    # ========================================

    async def search(
        self,
        query: str,
        object_type: Optional[str] = None,
        body_id: Optional[str] = None,
        tenant: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict:
        """
        Multi-Index Volltextsuche mit Highlighting und Facetten.

        Args:
            query: Suchbegriff
            object_type: Filter auf OParl-Typ (paper, meeting, person, organization)
            body_id: Filter auf Koerperschaft
            tenant: Mandanten-Filter
            date_from: Datum ab (ISO-Format)
            date_to: Datum bis (ISO-Format)
            page: Seite (1-basiert)
            per_page: Ergebnisse pro Seite

        Returns:
            Dict mit data, total, page, facets, etc.
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
                        "keywords^2",
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

        # Datumsfilter
        if date_from or date_to:
            date_range: dict[str, str] = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            filter_clauses.append({"range": {"date": date_range}})

        es_query = {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        }

        # Facetten (Aggregationen)
        aggs = {
            "by_type": {
                "terms": {"field": "oparl_type", "size": 10}
            },
            "by_paper_type": {
                "terms": {"field": "paper_type", "size": 20}
            },
            "by_organization": {
                "terms": {"field": "organizations", "size": 20}
            },
            "by_year": {
                "date_histogram": {
                    "field": "date",
                    "calendar_interval": "year",
                    "format": "yyyy",
                    "min_doc_count": 1,
                }
            },
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
                        "content": {
                            "number_of_fragments": 3,
                            "fragment_size": 200,
                        },
                    },
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"],
                },
                aggregations=aggs,
                sort=[
                    "_score",
                    {"modified": {"order": "desc", "missing": "_last"}},
                ],
            )
        except Exception as e:
            logger.error("Suche fehlgeschlagen", error=str(e), query=query)
            return {
                "data": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "facets": {},
            }

        hits = result["hits"]
        total = (
            hits["total"]["value"]
            if isinstance(hits["total"], dict)
            else hits["total"]
        )

        data = []
        for hit in hits["hits"]:
            src = hit["_source"]
            item = {
                "id": src.get("oparl_id"),
                "type": src.get("oparl_type"),
                "name": src.get("name"),
                "reference": src.get("reference"),
                "date": src.get("date"),
                "score": hit["_score"],
            }
            if "highlight" in hit:
                item["highlight"] = hit["highlight"]
            data.append(item)

        # Facetten aufbereiten
        facets = {}
        if "aggregations" in result:
            for agg_name, agg_result in result["aggregations"].items():
                if "buckets" in agg_result:
                    facets[agg_name] = [
                        {
                            "key": b.get("key_as_string", b["key"]),
                            "count": b["doc_count"],
                        }
                        for b in agg_result["buckets"]
                    ]

        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "facets": facets,
        }

    # ========================================
    # Autocomplete / Suggestions
    # ========================================

    async def suggest(
        self,
        prefix: str,
        tenant: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """
        Autocomplete-Vorschlaege basierend auf Praefix.

        Sucht ueber name.suggest Feld mit Edge-NGram-Analyse.
        """
        filter_clauses = []
        if tenant:
            filter_clauses.append({"term": {"tenant": tenant}})

        es_query: dict[str, Any] = {
            "bool": {
                "must": [
                    {
                        "match": {
                            "name.suggest": {
                                "query": prefix,
                                "operator": "and",
                            }
                        }
                    }
                ],
                "filter": filter_clauses,
            }
        }

        try:
            result = await self.client.search(
                index=self.index_name,
                query=es_query,
                size=limit,
                _source=["oparl_id", "oparl_type", "name", "reference"],
            )
        except Exception as e:
            logger.error("Suggest fehlgeschlagen", error=str(e))
            return []

        suggestions = []
        for hit in result["hits"]["hits"]:
            src = hit["_source"]
            suggestions.append({
                "id": src.get("oparl_id"),
                "type": src.get("oparl_type"),
                "name": src.get("name"),
                "reference": src.get("reference"),
                "score": hit["_score"],
            })
        return suggestions

    # ========================================
    # Reindex
    # ========================================

    async def reindex_all(self, objects: list[dict]) -> int:
        """
        Vollstaendiger Reindex aller OParl-Objekte.

        Loescht den bestehenden Index und erstellt ihn mit allen
        Objekten neu. Verwendet Bulk-API fuer Performance.
        """
        # Index loeschen und neu erstellen
        exists = await self.client.indices.exists(index=self.index_name)
        if exists:
            await self.client.indices.delete(index=self.index_name)
            logger.info("Alter Index geloescht", index=self.index_name)

        await self.client.indices.create(
            index=self.index_name,
            body=GERMAN_INDEX_SETTINGS,
        )
        logger.info("Neuer Index erstellt", index=self.index_name)

        if not objects:
            return 0

        # Bulk-Indexierung
        actions = [
            {
                "_index": self.index_name,
                "_id": obj.get("oparl_id", obj.get("id")),
                "_source": obj,
            }
            for obj in objects
        ]

        success, errors = await async_bulk(self.client, actions)
        logger.info(
            "Reindex abgeschlossen",
            success=success,
            errors=len(errors) if errors else 0,
        )
        return success

    async def close(self) -> None:
        """Elasticsearch-Client schliessen."""
        await self.client.close()
