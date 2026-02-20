"""
aitema|RIS - Elasticsearch Volltextsuche (v2)

Vollstaendige Elasticsearch 8.x Integration:
- index_all_papers(), index_all_meetings(), index_all_persons() - Bulk-Indexer
- search(query, types, filters, page, size) -> SearchResult mit Highlighting
- autocomplete(prefix, type, limit) -> Suggestions[]
- search_with_facets(query) -> {results, facets}
- Tenant-Isolation via tenant_id Filter
- German Analyzer mit Decompound-Filter
- NGram-Analyzer fuer Autocomplete (min 3, max 15)
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
# Index-Mapping fuer ris_papers
# ============================================================
PAPERS_INDEX_SETTINGS: dict[str, Any] = {
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
                        "buerger", "buergerinnen", "stadt", "bau", "planung",
                        "umwelt", "verkehr", "schule", "jugend", "sozial",
                        "kultur", "gesundheit", "sport", "wohnen", "energie",
                        "digital", "finanzen", "personal", "recht", "ordnung",
                    ],
                },
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 15,
                },
            },
        },
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "tenant_id": {"type": "keyword"},
            "body_id": {"type": "keyword"},
            "oparl_id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "german_analyzer",
                "fields": {
                    "exact": {"type": "text", "analyzer": "german_exact"},
                    "keyword": {"type": "keyword", "ignore_above": 512},
                    "suggest": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "german_exact",
                    },
                },
            },
            "reference": {
                "type": "keyword",
                "fields": {
                    "text": {"type": "text", "analyzer": "german_exact"},
                },
            },
            "content": {
                "type": "text",
                "analyzer": "german_analyzer",
            },
            "paper_type": {"type": "keyword"},
            "date": {"type": "date"},
            "created": {"type": "date"},
            "modified": {"type": "date"},
            "keywords": {"type": "keyword"},
            "organizations": {"type": "keyword"},
            "persons": {"type": "keyword"},
        }
    },
}

# ============================================================
# Index-Mapping fuer ris_meetings
# ============================================================
MEETINGS_INDEX_SETTINGS: dict[str, Any] = {
    "settings": PAPERS_INDEX_SETTINGS["settings"],
    "mappings": {
        "properties": {
            "tenant_id": {"type": "keyword"},
            "body_id": {"type": "keyword"},
            "oparl_id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "german_analyzer",
                "fields": {
                    "exact": {"type": "text", "analyzer": "german_exact"},
                    "keyword": {"type": "keyword", "ignore_above": 512},
                    "suggest": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "german_exact",
                    },
                },
            },
            "content": {
                "type": "text",
                "analyzer": "german_analyzer",
            },
            "meeting_state": {"type": "keyword"},
            "organization_name": {"type": "keyword"},
            "organization_id": {"type": "keyword"},
            "start": {"type": "date"},
            "end": {"type": "date"},
            "created": {"type": "date"},
            "modified": {"type": "date"},
        }
    },
}

# ============================================================
# Index-Mapping fuer ris_persons
# ============================================================
PERSONS_INDEX_SETTINGS: dict[str, Any] = {
    "settings": PAPERS_INDEX_SETTINGS["settings"],
    "mappings": {
        "properties": {
            "tenant_id": {"type": "keyword"},
            "body_id": {"type": "keyword"},
            "oparl_id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "german_analyzer",
                "fields": {
                    "exact": {"type": "text", "analyzer": "german_exact"},
                    "keyword": {"type": "keyword", "ignore_above": 512},
                    "suggest": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "german_exact",
                    },
                },
            },
            "family_name": {"type": "text", "analyzer": "german_exact"},
            "given_name": {"type": "text", "analyzer": "german_exact"},
            "content": {
                "type": "text",
                "analyzer": "german_analyzer",
            },
            "organizations": {"type": "keyword"},
            "created": {"type": "date"},
            "modified": {"type": "date"},
        }
    },
}

INDEX_CONFIGS = {
    "papers": PAPERS_INDEX_SETTINGS,
    "meetings": MEETINGS_INDEX_SETTINGS,
    "persons": PERSONS_INDEX_SETTINGS,
}

# ============================================================
# Hilfstypen
# ============================================================

class SearchResult:
    """Ergebnis einer Volltextsuche."""

    def __init__(
        self,
        data: list[dict],
        total: int,
        page: int,
        per_page: int,
        facets: dict,
    ) -> None:
        self.data = data
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = (total + per_page - 1) // per_page if per_page else 0
        self.facets = facets

    def to_dict(self) -> dict:
        return {
            "data": self.data,
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "total_pages": self.total_pages,
            "facets": self.facets,
        }


# ============================================================
# SearchService
# ============================================================

class SearchService:
    """
    Elasticsearch 8.x basierte Volltextsuche.

    Drei dedizierte Indizes:
    - {prefix}_ris_papers
    - {prefix}_ris_meetings
    - {prefix}_ris_persons

    Unterstuetzt:
    - Highlighting mit <mark> Tags
    - Facetten (Aggregationen)
    - Autocomplete via Edge-NGram
    - Tenant-Isolation
    - Bulk-Indexierung aller OParl-Objekte
    """

    def __init__(self) -> None:
        auth_kwargs: dict[str, Any] = {}
        if settings.es_password:
            auth_kwargs["basic_auth"] = ("elastic", settings.es_password)

        self.client = AsyncElasticsearch(
            settings.elasticsearch_url,
            **auth_kwargs,
        )
        prefix = settings.es_index_prefix
        self.idx_papers = f"{prefix}_ris_papers"
        self.idx_meetings = f"{prefix}_ris_meetings"
        self.idx_persons = f"{prefix}_ris_persons"

        self._index_map = {
            "paper": self.idx_papers,
            "meeting": self.idx_meetings,
            "person": self.idx_persons,
        }

    # ----------------------------------------
    # Index-Verwaltung
    # ----------------------------------------

    async def ensure_indices(self) -> None:
        """Alle drei Indizes anlegen falls nicht vorhanden."""
        for name, cfg in [
            (self.idx_papers, PAPERS_INDEX_SETTINGS),
            (self.idx_meetings, MEETINGS_INDEX_SETTINGS),
            (self.idx_persons, PERSONS_INDEX_SETTINGS),
        ]:
            exists = await self.client.indices.exists(index=name)
            if not exists:
                await self.client.indices.create(index=name, body=cfg)
                logger.info("ES-Index erstellt", index=name)

    async def _recreate_index(self, index_name: str, cfg: dict) -> None:
        """Index loeschen und neu erstellen."""
        exists = await self.client.indices.exists(index=index_name)
        if exists:
            await self.client.indices.delete(index=index_name)
            logger.info("Alter Index geloescht", index=index_name)
        await self.client.indices.create(index=index_name, body=cfg)
        logger.info("Neuer Index erstellt", index=index_name)

    # ----------------------------------------
    # Bulk-Indexierung
    # ----------------------------------------

    async def index_all_papers(self, papers: list[dict]) -> int:
        """Alle Vorlagen (Papers) in ris_papers indexieren."""
        await self._recreate_index(self.idx_papers, PAPERS_INDEX_SETTINGS)
        if not papers:
            return 0

        actions = [
            {
                "_index": self.idx_papers,
                "_id": p.get("oparl_id", p.get("id")),
                "_source": {**p, "oparl_type": "paper"},
            }
            for p in papers
        ]
        success, errors = await async_bulk(self.client, actions, raise_on_error=False)
        logger.info("Papers indexiert", success=success, errors=len(errors) if errors else 0)
        return success

    async def index_all_meetings(self, meetings: list[dict]) -> int:
        """Alle Sitzungen (Meetings) in ris_meetings indexieren."""
        await self._recreate_index(self.idx_meetings, MEETINGS_INDEX_SETTINGS)
        if not meetings:
            return 0

        actions = [
            {
                "_index": self.idx_meetings,
                "_id": m.get("oparl_id", m.get("id")),
                "_source": {**m, "oparl_type": "meeting"},
            }
            for m in meetings
        ]
        success, errors = await async_bulk(self.client, actions, raise_on_error=False)
        logger.info("Meetings indexiert", success=success, errors=len(errors) if errors else 0)
        return success

    async def index_all_persons(self, persons: list[dict]) -> int:
        """Alle Personen in ris_persons indexieren."""
        await self._recreate_index(self.idx_persons, PERSONS_INDEX_SETTINGS)
        if not persons:
            return 0

        actions = [
            {
                "_index": self.idx_persons,
                "_id": p.get("oparl_id", p.get("id")),
                "_source": {**p, "oparl_type": "person"},
            }
            for p in persons
        ]
        success, errors = await async_bulk(self.client, actions, raise_on_error=False)
        logger.info("Persons indexiert", success=success, errors=len(errors) if errors else 0)
        return success

    async def reindex_all(self, objects: list[dict]) -> int:
        """
        Vollstaendiger Reindex aller OParl-Objekte (kompatibel mit Admin-Router).
        Verteilt Objekte nach oparl_type auf die drei Indizes.
        """
        papers = [o for o in objects if o.get("oparl_type") == "paper"]
        meetings = [o for o in objects if o.get("oparl_type") == "meeting"]
        persons = [o for o in objects if o.get("oparl_type") == "person"]

        total = 0
        total += await self.index_all_papers(papers)
        total += await self.index_all_meetings(meetings)
        total += await self.index_all_persons(persons)
        return total

    async def index_document(
        self,
        doc_id: str,
        oparl_type: str,
        body: dict[str, Any],
        tenant: str = "public",
    ) -> None:
        """Einzelnes OParl-Objekt indexieren (fuer inkrementelle Updates)."""
        await self.ensure_indices()
        index = self._index_map.get(oparl_type, self.idx_papers)
        doc = {"oparl_id": doc_id, "oparl_type": oparl_type, "tenant_id": tenant, **body}
        await self.client.index(index=index, id=doc_id, document=doc)
        logger.debug("Dokument indexiert", doc_id=doc_id, type=oparl_type)

    async def delete_document(self, doc_id: str, oparl_type: str = "paper") -> None:
        """Dokument aus dem Index entfernen."""
        index = self._index_map.get(oparl_type, self.idx_papers)
        try:
            await self.client.delete(index=index, id=doc_id)
        except Exception:
            logger.warning("Loeschen aus Index fehlgeschlagen", doc_id=doc_id)

    # ----------------------------------------
    # Suche
    # ----------------------------------------

    def _build_filter_clauses(
        self,
        tenant_id: Optional[str],
        body_id: Optional[str],
        gremium: Optional[str],
        year: Optional[int],
        status: Optional[str],
        oparl_type: Optional[str],
    ) -> list[dict]:
        """Filter-Klauseln fuer den ES-Query aufbauen."""
        filters: list[dict] = []
        if tenant_id:
            filters.append({"term": {"tenant_id": tenant_id}})
        if body_id:
            filters.append({"term": {"body_id": body_id}})
        if gremium:
            filters.append({"term": {"organization_name": gremium}})
        if status:
            filters.append({"bool": {"should": [
                {"term": {"meeting_state": status}},
                {"term": {"paper_type": status}},
            ]}})
        if year:
            filters.append({"bool": {"should": [
                {"range": {"date": {
                    "gte": f"{year}-01-01",
                    "lte": f"{year}-12-31",
                }}},
                {"range": {"start": {
                    "gte": f"{year}-01-01",
                    "lte": f"{year}-12-31",
                }}},
            ]}})
        return filters

    def _determine_indices(self, types: Optional[list[str]]) -> list[str]:
        """Welche Indizes durchsuchen?"""
        all_indices = [self.idx_papers, self.idx_meetings, self.idx_persons]
        if not types:
            return all_indices
        result = []
        for t in types:
            idx = self._index_map.get(t)
            if idx:
                result.append(idx)
        return result or all_indices

    async def search(
        self,
        query: str,
        types: Optional[list[str]] = None,
        tenant_id: Optional[str] = None,
        body_id: Optional[str] = None,
        gremium: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        # Rueckwaertskompatibilitaet mit altem Interface
        object_type: Optional[str] = None,
        per_page: Optional[int] = None,
        tenant: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> SearchResult:
        """
        Multi-Index Volltextsuche mit Highlighting und Facetten.

        Args:
            query:     Suchbegriff
            types:     ['paper', 'meeting', 'person'] - welche Typen
            tenant_id: Mandanten-Filter (Tenant-Isolation)
            body_id:   Filter auf Koerperschaft
            gremium:   Gremiumsname-Filter
            year:      Jahres-Filter
            status:    Statusfilter (meeting_state oder paper_type)
            page:      Seite (1-basiert)
            size:      Ergebnisse pro Seite

        Returns:
            SearchResult mit data, total, facets
        """
        # Rueckwaertskompatibilitaet
        if per_page is not None:
            size = per_page
        if tenant and not tenant_id:
            tenant_id = tenant
        if object_type and not types:
            types = [object_type]

        indices = self._determine_indices(types)
        filter_clauses = self._build_filter_clauses(
            tenant_id, body_id, gremium, year, status, object_type
        )

        # Datumsfilter (alt)
        if date_from or date_to:
            date_range: dict[str, str] = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            filter_clauses.append({"range": {"date": date_range}})

        if not query or query.strip() == "*":
            must_clauses: list[dict] = [{"match_all": {}}]
        else:
            must_clauses = [
                {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "name^4",
                            "name.exact^3",
                            "reference^5",
                            "content^1",
                            "keywords^2",
                            "family_name^3",
                            "given_name^3",
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                        "operator": "or",
                    }
                }
            ]

        es_query = {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        }

        aggs = {
            "by_type": {"terms": {"field": "oparl_type", "size": 10}},
            "by_paper_type": {"terms": {"field": "paper_type", "size": 20}},
            "by_organization": {"terms": {"field": "organization_name", "size": 20}},
            "by_meeting_state": {"terms": {"field": "meeting_state", "size": 10}},
            "by_year": {
                "date_histogram": {
                    "field": "date",
                    "calendar_interval": "year",
                    "format": "yyyy",
                    "min_doc_count": 1,
                }
            },
        }

        highlight_cfg = {
            "fields": {
                "name": {"number_of_fragments": 1},
                "content": {
                    "number_of_fragments": 3,
                    "fragment_size": 200,
                },
                "reference": {"number_of_fragments": 1},
            },
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
        }

        try:
            result = await self.client.search(
                index=indices,
                query=es_query,
                from_=(page - 1) * size,
                size=size,
                highlight=highlight_cfg,
                aggregations=aggs,
                sort=["_score", {"modified": {"order": "desc", "missing": "_last"}}],
            )
        except Exception as e:
            logger.error("Suche fehlgeschlagen", error=str(e), query=query)
            return SearchResult(data=[], total=0, page=page, per_page=size, facets={})

        hits = result["hits"]
        total_val = hits["total"]
        total = total_val["value"] if isinstance(total_val, dict) else int(total_val)

        data = []
        for hit in hits["hits"]:
            src = hit["_source"]
            item: dict[str, Any] = {
                "id": src.get("oparl_id"),
                "type": src.get("oparl_type"),
                "name": src.get("name"),
                "reference": src.get("reference"),
                "date": src.get("date") or src.get("start"),
                "paper_type": src.get("paper_type"),
                "meeting_state": src.get("meeting_state"),
                "organization_name": src.get("organization_name"),
                "score": hit.get("_score", 0),
            }
            if "highlight" in hit:
                item["highlight"] = hit["highlight"]
            data.append(item)

        # Facetten aufbereiten
        facets: dict[str, Any] = {}
        if "aggregations" in result:
            for agg_name, agg_result in result["aggregations"].items():
                if "buckets" in agg_result:
                    facets[agg_name] = [
                        {
                            "key": b.get("key_as_string", b["key"]),
                            "count": b["doc_count"],
                        }
                        for b in agg_result["buckets"]
                        if b["doc_count"] > 0
                    ]

        return SearchResult(data=data, total=total, page=page, per_page=size, facets=facets)

    # ----------------------------------------
    # Autocomplete
    # ----------------------------------------

    async def autocomplete(
        self,
        prefix: str,
        type: Optional[str] = None,
        limit: int = 8,
        tenant_id: Optional[str] = None,
    ) -> list[dict]:
        """
        Typeahead-Vorschlaege basierend auf Praefix (Edge-NGram).

        Args:
            prefix:    Eingabe-Praefix (mind. 3 Zeichen)
            type:      'paper', 'meeting', 'person' oder None (alle)
            limit:     Max. Anzahl Vorschlaege
            tenant_id: Tenant-Isolation

        Returns:
            Liste von {id, type, name, reference, score}
        """
        if len(prefix) < 3:
            return []

        indices = self._determine_indices([type] if type else None)
        filter_clauses: list[dict] = []
        if tenant_id:
            filter_clauses.append({"term": {"tenant_id": tenant_id}})

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
                index=indices,
                query=es_query,
                size=limit,
                _source=["oparl_id", "oparl_type", "name", "reference", "paper_type", "meeting_state"],
            )
        except Exception as e:
            logger.error("Autocomplete fehlgeschlagen", error=str(e))
            return []

        suggestions = []
        for hit in result["hits"]["hits"]:
            src = hit["_source"]
            suggestions.append({
                "id": src.get("oparl_id"),
                "type": src.get("oparl_type"),
                "name": src.get("name"),
                "reference": src.get("reference"),
                "paper_type": src.get("paper_type"),
                "meeting_state": src.get("meeting_state"),
                "score": hit.get("_score", 0),
            })
        return suggestions

    # Alias fuer Rueckwaertskompatibilitaet
    async def suggest(
        self,
        prefix: str,
        tenant: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        return await self.autocomplete(prefix=prefix, limit=limit, tenant_id=tenant)

    # ----------------------------------------
    # Suche mit Facetten (separate Methode)
    # ----------------------------------------

    async def search_with_facets(
        self,
        query: str,
        tenant_id: Optional[str] = None,
        body_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Volltext-Suche ueber alle Typen mit aggregierten Facetten.

        Returns:
            {results: SearchResult, facets: {by_type, by_paper_type, ...}}
        """
        sr = await self.search(
            query=query,
            tenant_id=tenant_id,
            body_id=body_id,
            size=25,
        )
        return {
            "results": sr.to_dict(),
            "facets": sr.facets,
        }

    # ----------------------------------------
    # Hilfsmethoden
    # ----------------------------------------

    async def close(self) -> None:
        """Elasticsearch-Client schliessen."""
        await self.client.close()
