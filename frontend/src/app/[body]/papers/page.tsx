/**
 * aitema|RIS - Vorlagensuche Page
 * Search and browse papers (Vorlagen/Drucksachen) for a body.
 */
"use client";

import { useState, useEffect } from "react";
import { apiClient, type OParlPaper } from "@/lib/api";

interface PapersPageProps {
  params: { body: string };
}

const PAPER_TYPES = [
  "Beschlussvorlage",
  "Antrag",
  "Anfrage",
  "Mitteilung",
  "Bericht",
  "Stellungnahme",
];

export default function PapersPage({ params }: PapersPageProps) {
  const [papers, setPapers] = useState<OParlPaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    async function loadPapers() {
      setLoading(true);
      try {
        const data = await apiClient.getPapers(params.body, {
          page,
          paperType: selectedType || undefined,
          q: searchQuery || undefined,
        });
        setPapers(data.data || []);
        setTotalPages(data.pagination?.totalPages || 1);
      } catch (error) {
        console.error("Failed to load papers:", error);
      } finally {
        setLoading(false);
      }
    }
    loadPapers();
  }, [params.body, page, selectedType, searchQuery]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Vorlagensuche</h1>

      {/* Search & Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="paper-search" className="sr-only">
              Vorlagen durchsuchen
            </label>
            <input
              id="paper-search"
              type="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Titel oder Vorlagennummer eingeben..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="paper-type-filter" className="sr-only">
              Vorlagentyp filtern
            </label>
            <select
              id="paper-type-filter"
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.target.value);
                setPage(1);
              }}
              className="w-full sm:w-48 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Alle Typen</option>
              {PAPER_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Suchen
          </button>
        </form>
      </div>

      {/* Results */}
      {loading ? (
        <div className="text-center py-12 text-gray-500" role="status">
          <p>Vorlagen werden geladen...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {papers.map((paper) => (
            <article
              key={paper.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <a
                    href={`/${params.body}/papers/${encodeURIComponent(paper.id)}`}
                    className="text-lg font-medium text-blue-600 hover:text-blue-800"
                  >
                    {paper.name}
                  </a>
                  <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                    {paper.reference && (
                      <span className="font-mono">{paper.reference}</span>
                    )}
                    {paper.date && (
                      <time dateTime={paper.date}>
                        {new Date(paper.date).toLocaleDateString("de-DE")}
                      </time>
                    )}
                  </div>
                </div>
                {paper.paperType && (
                  <span className="ml-4 px-3 py-1 text-xs rounded-full bg-blue-100 text-blue-700 whitespace-nowrap">
                    {paper.paperType}
                  </span>
                )}
              </div>
            </article>
          ))}

          {papers.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <p>Keine Vorlagen gefunden.</p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <nav className="flex items-center justify-center gap-4 pt-6" aria-label="Seitennavigation">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Zurueck
              </button>
              <span className="text-sm text-gray-600">
                Seite {page} von {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Weiter
              </button>
            </nav>
          )}
        </div>
      )}
    </div>
  );
}
