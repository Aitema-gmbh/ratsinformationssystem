'use client';

import { useState } from 'react';

interface SearchResult {
  type: string;
  id: string;
  name: string;
  reference?: string;
  start?: string;
}

const typeLabels: Record<string, string> = {
  paper: 'Vorlage',
  meeting: 'Sitzung',
  person: 'Person',
  organization: 'Gremium',
};

const typeColors: Record<string, string> = {
  paper: '#3b82f6',
  meeting: '#8b5cf6',
  person: '#f59e0b',
  organization: '#16a34a',
};

export default function SuchePage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (query.length < 2) return;
    setLoading(true);
    setSearched(true);

    try {
      const resp = await fetch(
        `${process.env.NEXT_PUBLIC_OPARL_URL}/search?q=${encodeURIComponent(query)}`
      );
      const data = await resp.json();
      setResults(data.data || []);
    } catch {
      setResults([]);
    }
    setLoading(false);
  };

  const getLink = (r: SearchResult) => {
    switch (r.type) {
      case 'paper': return `/vorlagen/${r.id.split('/').pop()}`;
      case 'meeting': return `/sitzungen/${r.id.split('/').pop()}`;
      case 'person': return `/personen/${r.id.split('/').pop()}`;
      default: return '#';
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>Suche</h1>

      <form
        role="search"
        aria-label="Ratsinformationssystem durchsuchen"
        onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
        style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem' }}
      >
        <label htmlFor="search-input" className="sr-only">Suchbegriff</label>
        <input
          id="search-input"
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Vorlagen, Sitzungen, Personen durchsuchen..."
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '1rem',
            minHeight: '48px',
          }}
          aria-describedby="search-hint"
        />
        <button
          type="submit"
          disabled={query.length < 2 || loading}
          style={{
            padding: '0.75rem 2rem',
            background: '#1e3a5f',
            color: '#fff',
            border: 'none',
            borderRadius: '0.375rem',
            fontSize: '1rem',
            fontWeight: 600,
            cursor: 'pointer',
            minHeight: '48px',
            opacity: query.length < 2 ? 0.5 : 1,
          }}
        >
          {loading ? 'Suche...' : 'Suchen'}
        </button>
      </form>
      <p id="search-hint" style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '-1.5rem', marginBottom: '1.5rem' }}>
        Mindestens 2 Zeichen eingeben
      </p>

      <div role="status" aria-live="polite">
        {searched && !loading && (
          <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1rem' }}>
            {results.length} Ergebnis(se) gefunden
          </p>
        )}
      </div>

      {results.length > 0 && (
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {results.map((r, i) => (
            <li key={i}>
              <a
                href={getLink(r)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '1rem',
                  background: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.375rem',
                  textDecoration: 'none',
                  color: 'inherit',
                }}
              >
                <span
                  style={{
                    padding: '0.25rem 0.5rem',
                    borderRadius: '0.25rem',
                    fontSize: '0.625rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: '#fff',
                    background: typeColors[r.type] || '#6b7280',
                    minWidth: '60px',
                    textAlign: 'center',
                  }}
                >
                  {typeLabels[r.type] || r.type}
                </span>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{r.name}</div>
                  {r.reference && (
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{r.reference}</div>
                  )}
                </div>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
