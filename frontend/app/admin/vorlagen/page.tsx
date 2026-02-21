'use client';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface Paper {
  id: string;
  name: string;
  reference?: string;
  paperType?: string;
  date?: string;
  underDirectionOf?: string[];
  mainFile?: { id: string; name: string; accessUrl?: string };
}

interface PaperListResponse {
  data: Paper[];
  pagination: {
    totalElements: number;
    currentPage: number;
    totalPages: number;
  };
}

const paperTypeLabels: Record<string, string> = {
  Antrag: 'Antrag',
  Anfrage: 'Anfrage',
  Beschlussvorlage: 'Beschlussvorlage',
  Informationsvorlage: 'Informationsvorlage',
  Mitteilungsvorlage: 'Mitteilungsvorlage',
};

export default function VorlagenAdmin() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState('');

  const loadPapers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(page), per_page: '20' });
      if (filterType) params.set('paper_type', filterType);
      const res = await fetch(`/api/admin/papers?${params}`);
      if (res.ok) {
        const data: PaperListResponse = await res.json();
        setPapers(data.data || []);
        setTotal(data.pagination?.totalElements || 0);
      } else {
        setError(`Fehler ${res.status}`);
      }
    } catch {
      setError('Verbindungsfehler');
    } finally {
      setLoading(false);
    }
  }, [page, filterType]);

  useEffect(() => { loadPapers(); }, [loadPapers]);

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('de-DE', {
      day: '2-digit', month: '2-digit', year: 'numeric',
    });
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>Vorlagen</h1>
          <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            {total} Vorlagen gesamt
          </p>
        </div>
        <Link
          href="/vorlagen"
          style={{
            background: '#f1f5f9', color: '#374151', border: '1px solid #e2e8f0',
            padding: '0.5rem 1rem', borderRadius: '0.375rem',
            textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500,
          }}
        >
          Oeffentliche Ansicht →
        </Link>
      </div>

      {/* Filter */}
      <div style={{ marginBottom: '1rem' }}>
        <select
          value={filterType}
          onChange={(e) => { setFilterType(e.target.value); setPage(1); }}
          style={{
            border: '1px solid #e2e8f0', borderRadius: '0.375rem',
            padding: '0.5rem 0.75rem', fontSize: '0.875rem', minWidth: '200px',
          }}
        >
          <option value="">Alle Typen</option>
          {Object.entries(paperTypeLabels).map(([val, label]) => (
            <option key={val} value={val}>{label}</option>
          ))}
        </select>
      </div>

      {error && (
        <div style={{
          background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.375rem',
          padding: '0.75rem 1rem', color: '#991b1b', fontSize: '0.875rem', marginBottom: '1rem',
        }}>
          {error}
        </div>
      )}

      <div style={{ background: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f8fafc' }}>
              {['Referenz / Name', 'Typ', 'Datum', 'Hauptdatei', 'Aktionen'].map((h) => (
                <th key={h} style={{
                  padding: '0.75rem 1rem', textAlign: 'left',
                  fontSize: '0.75rem', fontWeight: 600, color: '#64748b',
                  textTransform: 'uppercase', letterSpacing: '0.05em',
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>Lade...</td></tr>
            ) : papers.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>Keine Vorlagen gefunden</td></tr>
            ) : (
              papers.map((paper, i) => (
                <tr key={paper.id} style={{ borderTop: i > 0 ? '1px solid #f1f5f9' : undefined }}>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    {paper.reference && (
                      <div style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace', marginBottom: '0.125rem' }}>
                        {paper.reference}
                      </div>
                    )}
                    <div style={{ fontWeight: 500, color: '#0f172a' }}>{paper.name}</div>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    {paper.paperType && (
                      <span style={{
                        background: '#eff6ff', color: '#1d4ed8',
                        padding: '0.125rem 0.5rem', borderRadius: '9999px',
                        fontSize: '0.75rem', fontWeight: 500,
                      }}>
                        {paperTypeLabels[paper.paperType] || paper.paperType}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '0.875rem 1rem', fontSize: '0.875rem', color: '#374151' }}>
                    {paper.date ? formatDate(paper.date) : '–'}
                  </td>
                  <td style={{ padding: '0.875rem 1rem', fontSize: '0.875rem' }}>
                    {paper.mainFile?.accessUrl ? (
                      <a
                        href={paper.mainFile.accessUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: '#3b82f6', textDecoration: 'none' }}
                      >
                        📄 {paper.mainFile.name || 'Datei'}
                      </a>
                    ) : '–'}
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <Link
                      href={`/vorlagen/${paper.id}`}
                      style={{ color: '#3b82f6', textDecoration: 'none', fontSize: '0.875rem' }}
                    >
                      Details →
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {total > 20 && (
          <div style={{
            padding: '1rem', borderTop: '1px solid #f1f5f9',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
              Seite {page} von {Math.ceil(total / 20)}
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                style={{
                  background: '#f1f5f9', border: '1px solid #e2e8f0',
                  padding: '0.375rem 0.75rem', borderRadius: '0.25rem',
                  cursor: page === 1 ? 'not-allowed' : 'pointer', fontSize: '0.875rem',
                  opacity: page === 1 ? 0.5 : 1,
                }}
              >
                Zurueck
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(total / 20)}
                style={{
                  background: '#3b82f6', color: 'white', border: 'none',
                  padding: '0.375rem 0.75rem', borderRadius: '0.25rem',
                  cursor: page >= Math.ceil(total / 20) ? 'not-allowed' : 'pointer',
                  fontSize: '0.875rem', opacity: page >= Math.ceil(total / 20) ? 0.5 : 1,
                }}
              >
                Weiter
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
