'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

// ============================================================
// Typen
// ============================================================

interface SearchItem {
  id: string;
  type: string;
  name: string;
  reference?: string;
  date?: string;
  paper_type?: string;
  meeting_state?: string;
  organization_name?: string;
  score: number;
  highlight?: Record<string, string[]>;
}

interface FacetBucket {
  key: string;
  count: number;
}

interface SearchResponse {
  data: SearchItem[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  facets: {
    by_type?: FacetBucket[];
    by_paper_type?: FacetBucket[];
    by_organization?: FacetBucket[];
    by_meeting_state?: FacetBucket[];
    by_year?: FacetBucket[];
  };
  query: string;
}

interface AutocompleteSuggestion {
  id: string;
  type: string;
  name: string;
  reference?: string;
  score: number;
}

// ============================================================
// Hilfskonstanten
// ============================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

const TYPE_LABELS: Record<string, string> = {
  paper: 'Vorlage',
  meeting: 'Sitzung',
  person: 'Person',
  organization: 'Gremium',
};

const TYPE_COLORS: Record<string, string> = {
  paper: '#3b82f6',
  meeting: '#8b5cf6',
  person: '#f59e0b',
  organization: '#16a34a',
};

const MEETING_STATE_LABELS: Record<string, string> = {
  scheduled: 'Geplant',
  invited: 'Eingeladen',
  running: 'Laufend',
  completed: 'Abgeschlossen',
  cancelled: 'Abgesagt',
};

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = Array.from({ length: 10 }, (_, i) => CURRENT_YEAR - i);

// ============================================================
// Hilfsfunktionen
// ============================================================

function getItemLink(item: SearchItem): string {
  const slug = item.id?.split('/').pop() || item.id;
  switch (item.type) {
    case 'paper':   return `/vorlagen/${slug}`;
    case 'meeting': return `/sitzungen/${slug}`;
    case 'person':  return `/personen/${slug}`;
    default:        return '#';
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '';
  try {
    return new Date(dateStr).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function HighlightedText({ html }: { html: string }) {
  return (
    <span
      dangerouslySetInnerHTML={{ __html: html }}
      style={{ lineHeight: 1.6 }}
    />
  );
}

// ============================================================
// Haupt-Komponente
// ============================================================

export default function SuchePage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // State aus URL lesen
  const [query, setQuery]       = useState(searchParams.get('q') || '');
  const [inputValue, setInputValue] = useState(searchParams.get('q') || '');
  const [typeFilter, setTypeFilter] = useState(searchParams.get('type') || '');
  const [gremiumFilter, setGremiumFilter] = useState(searchParams.get('gremium') || '');
  const [yearFilter, setYearFilter] = useState(searchParams.get('year') || '');
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10));

  // Ergebnisse
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Autocomplete
  const [suggestions, setSuggestions] = useState<AutocompleteSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestion, setActiveSuggestion] = useState(-1);

  // Mobile-Filter-Drawer
  const [drawerOpen, setDrawerOpen] = useState(false);

  const autocompleteTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // ----------------------------------------
  // URL-Sync
  // ----------------------------------------

  const updateURL = useCallback((params: {
    q?: string; type?: string; gremium?: string;
    year?: string; status?: string; page?: number;
  }) => {
    const p = new URLSearchParams();
    const q       = params.q       !== undefined ? params.q       : query;
    const type    = params.type    !== undefined ? params.type    : typeFilter;
    const gremium = params.gremium !== undefined ? params.gremium : gremiumFilter;
    const year    = params.year    !== undefined ? params.year    : yearFilter;
    const status  = params.status  !== undefined ? params.status  : statusFilter;
    const pg      = params.page    !== undefined ? params.page    : page;

    if (q)       p.set('q', q);
    if (type)    p.set('type', type);
    if (gremium) p.set('gremium', gremium);
    if (year)    p.set('year', year);
    if (status)  p.set('status', status);
    if (pg > 1)  p.set('page', String(pg));

    router.replace(`/suche?${p.toString()}`, { scroll: false });
  }, [query, typeFilter, gremiumFilter, yearFilter, statusFilter, page, router]);

  // ----------------------------------------
  // Suche ausfuehren
  // ----------------------------------------

  const executeSearch = useCallback(async (
    q: string,
    type: string,
    gremium: string,
    year: string,
    status: string,
    pg: number,
  ) => {
    if (!q || q.trim().length < 2) {
      setResults(null);
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({ q: q.trim(), page: String(pg), size: '20' });
      if (type)    params.set('type', type);
      if (gremium) params.set('gremium', gremium);
      if (year)    params.set('year', year);
      if (status)  params.set('status', status);

      const resp = await fetch(`${API_URL}/api/v1/search?${params}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: SearchResponse = await resp.json();
      setResults(data);
    } catch (err) {
      console.error('Suche fehlgeschlagen:', err);
      setResults(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Wenn URL-Parameter sich aendern → Suche
  useEffect(() => {
    if (query.trim().length >= 2) {
      executeSearch(query, typeFilter, gremiumFilter, yearFilter, statusFilter, page);
    }
  }, [query, typeFilter, gremiumFilter, yearFilter, statusFilter, page, executeSearch]);

  // ----------------------------------------
  // Autocomplete (debounced 300ms)
  // ----------------------------------------

  const fetchAutocomplete = useCallback(async (val: string) => {
    if (val.trim().length < 3) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    try {
      const params = new URLSearchParams({ q: val.trim() });
      if (typeFilter) params.set('type', typeFilter);
      const resp = await fetch(`${API_URL}/api/v1/search/autocomplete?${params}`);
      if (!resp.ok) return;
      const data = await resp.json();
      setSuggestions(data.suggestions || []);
      setShowSuggestions((data.suggestions || []).length > 0);
    } catch {
      setSuggestions([]);
    }
  }, [typeFilter]);

  const handleInputChange = (val: string) => {
    setInputValue(val);
    setActiveSuggestion(-1);
    if (autocompleteTimer.current) clearTimeout(autocompleteTimer.current);
    autocompleteTimer.current = setTimeout(() => fetchAutocomplete(val), 300);
  };

  // Keyboard-Navigation fuer Autocomplete
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions) {
      if (e.key === 'Enter') submitSearch();
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveSuggestion(prev => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveSuggestion(prev => Math.max(prev - 1, -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeSuggestion >= 0 && suggestions[activeSuggestion]) {
        selectSuggestion(suggestions[activeSuggestion]);
      } else {
        setShowSuggestions(false);
        submitSearch();
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const selectSuggestion = (s: AutocompleteSuggestion) => {
    setInputValue(s.name);
    setShowSuggestions(false);
    setSuggestions([]);
    const newPage = 1;
    setQuery(s.name);
    setPage(newPage);
    updateURL({ q: s.name, page: newPage });
  };

  const submitSearch = () => {
    setShowSuggestions(false);
    const newPage = 1;
    setQuery(inputValue);
    setPage(newPage);
    updateURL({ q: inputValue, page: newPage });
  };

  // Click-Outside fuer Suggestions
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ----------------------------------------
  // Filter-Aenderungen
  // ----------------------------------------

  const applyFilter = (key: string, value: string) => {
    const newPage = 1;
    setPage(newPage);
    if (key === 'type')    { setTypeFilter(value);    updateURL({ type: value,    page: newPage }); }
    if (key === 'gremium') { setGremiumFilter(value); updateURL({ gremium: value, page: newPage }); }
    if (key === 'year')    { setYearFilter(value);    updateURL({ year: value,    page: newPage }); }
    if (key === 'status')  { setStatusFilter(value);  updateURL({ status: value,  page: newPage }); }
  };

  const clearAllFilters = () => {
    setTypeFilter('');
    setGremiumFilter('');
    setYearFilter('');
    setStatusFilter('');
    setPage(1);
    updateURL({ type: '', gremium: '', year: '', status: '', page: 1 });
  };

  const hasFilters = !!(typeFilter || gremiumFilter || yearFilter || statusFilter);

  // ----------------------------------------
  // Gremien aus Facetten extrahieren
  // ----------------------------------------

  const gremienOptions: string[] = results?.facets?.by_organization?.map(f => f.key) || [];

  // ----------------------------------------
  // Filter-Sidebar Inhalt
  // ----------------------------------------

  const FilterContent = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Typ */}
      <div>
        <label style={labelStyle}>Typ</label>
        <select
          value={typeFilter}
          onChange={e => applyFilter('type', e.target.value)}
          style={selectStyle}
          aria-label="Nach Typ filtern"
        >
          <option value="">Alle Typen</option>
          {Object.entries(TYPE_LABELS).map(([val, label]) => (
            <option key={val} value={val}>{label}</option>
          ))}
        </select>
        {results?.facets?.by_type && (
          <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            {results.facets.by_type.map(f => (
              <button
                key={f.key}
                onClick={() => applyFilter('type', typeFilter === f.key ? '' : f.key)}
                style={{
                  ...facetBtnStyle,
                  background: typeFilter === f.key ? TYPE_COLORS[f.key] || '#1e3a5f' : 'transparent',
                  color: typeFilter === f.key ? '#fff' : '#374151',
                  borderColor: TYPE_COLORS[f.key] || '#d1d5db',
                }}
              >
                <span>{TYPE_LABELS[f.key] || f.key}</span>
                <span style={facetCountStyle}>{f.count}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Jahr */}
      <div>
        <label style={labelStyle}>Jahr</label>
        <select
          value={yearFilter}
          onChange={e => applyFilter('year', e.target.value)}
          style={selectStyle}
          aria-label="Nach Jahr filtern"
        >
          <option value="">Alle Jahre</option>
          {results?.facets?.by_year
            ? results.facets.by_year.map(f => (
                <option key={f.key} value={f.key}>{f.key} ({f.count})</option>
              ))
            : YEARS.map(y => (
                <option key={y} value={String(y)}>{y}</option>
              ))
          }
        </select>
      </div>

      {/* Gremium */}
      {gremienOptions.length > 0 && (
        <div>
          <label style={labelStyle}>Gremium</label>
          <select
            value={gremiumFilter}
            onChange={e => applyFilter('gremium', e.target.value)}
            style={selectStyle}
            aria-label="Nach Gremium filtern"
          >
            <option value="">Alle Gremien</option>
            {gremienOptions.map(g => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </div>
      )}

      {/* Status */}
      {results?.facets?.by_meeting_state && results.facets.by_meeting_state.length > 0 && (
        <div>
          <label style={labelStyle}>Status</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.25rem' }}>
            {results.facets.by_meeting_state.map(f => (
              <button
                key={f.key}
                onClick={() => applyFilter('status', statusFilter === f.key ? '' : f.key)}
                style={{
                  ...facetBtnStyle,
                  background: statusFilter === f.key ? '#1e3a5f' : 'transparent',
                  color: statusFilter === f.key ? '#fff' : '#374151',
                }}
              >
                <span>{MEETING_STATE_LABELS[f.key] || f.key}</span>
                <span style={facetCountStyle}>{f.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Filter zuruecksetzen */}
      {hasFilters && (
        <button
          onClick={clearAllFilters}
          style={{
            padding: '0.5rem 1rem',
            background: '#fee2e2',
            color: '#b91c1c',
            border: '1px solid #fca5a5',
            borderRadius: '0.375rem',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: 500,
          }}
        >
          Filter zuruecksetzen
        </button>
      )}
    </div>
  );

  // ----------------------------------------
  // Render
  // ----------------------------------------

  return (
    <>
      {/* Mobile Filter-Drawer Overlay */}
      {drawerOpen && (
        <div
          onClick={() => setDrawerOpen(false)}
          style={{
            position: 'fixed', inset: 0,
            background: 'rgba(0,0,0,0.4)',
            zIndex: 40,
          }}
          aria-hidden="true"
        />
      )}

      {/* Mobile Filter-Drawer */}
      <div
        role="dialog"
        aria-label="Suchfilter"
        aria-modal="true"
        style={{
          position: 'fixed',
          left: drawerOpen ? 0 : '-320px',
          top: 0,
          bottom: 0,
          width: '300px',
          background: '#fff',
          zIndex: 50,
          padding: '1.5rem',
          overflowY: 'auto',
          boxShadow: '4px 0 16px rgba(0,0,0,0.12)',
          transition: 'left 0.25s ease',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 700 }}>Filter</h2>
          <button
            onClick={() => setDrawerOpen(false)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.5rem', lineHeight: 1 }}
            aria-label="Filter schliessen"
          >
            &times;
          </button>
        </div>
        <FilterContent />
      </div>

      {/* Hauptinhalt */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '1.5rem' }}>
          Volltextsuche
        </h1>

        {/* Suchleiste */}
        <div style={{ position: 'relative', marginBottom: '2rem' }}>
          <form
            role="search"
            aria-label="Ratsinformationssystem durchsuchen"
            onSubmit={e => { e.preventDefault(); submitSearch(); }}
            style={{ display: 'flex', gap: '0.75rem' }}
          >
            <label htmlFor="main-search" className="sr-only">Suchbegriff</label>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                id="main-search"
                ref={inputRef}
                type="search"
                value={inputValue}
                onChange={e => handleInputChange(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                placeholder="Vorlagen, Sitzungen, Personen durchsuchen..."
                autoComplete="off"
                aria-autocomplete="list"
                aria-controls="autocomplete-list"
                aria-expanded={showSuggestions}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  border: '2px solid #d1d5db',
                  borderRadius: '0.375rem',
                  fontSize: '1rem',
                  minHeight: '48px',
                  boxSizing: 'border-box',
                  outline: 'none',
                  transition: 'border-color 0.15s',
                }}
                onFocusCapture={e => (e.target.style.borderColor = '#1e3a5f')}
                onBlurCapture={e => (e.target.style.borderColor = '#d1d5db')}
              />

              {/* Autocomplete-Dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div
                  id="autocomplete-list"
                  ref={suggestionsRef}
                  role="listbox"
                  aria-label="Suchvorschlaege"
                  style={{
                    position: 'absolute',
                    top: 'calc(100% + 4px)',
                    left: 0,
                    right: 0,
                    background: '#fff',
                    border: '1px solid #d1d5db',
                    borderRadius: '0.375rem',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
                    zIndex: 30,
                    maxHeight: '320px',
                    overflowY: 'auto',
                  }}
                >
                  {suggestions.map((s, i) => (
                    <button
                      key={s.id || i}
                      role="option"
                      aria-selected={i === activeSuggestion}
                      onClick={() => selectSuggestion(s)}
                      onMouseEnter={() => setActiveSuggestion(i)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        width: '100%',
                        padding: '0.625rem 1rem',
                        background: i === activeSuggestion ? '#f0f4ff' : 'transparent',
                        border: 'none',
                        borderBottom: '1px solid #f3f4f6',
                        cursor: 'pointer',
                        textAlign: 'left',
                      }}
                    >
                      <span style={{
                        padding: '0.125rem 0.375rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.625rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        color: '#fff',
                        background: TYPE_COLORS[s.type] || '#6b7280',
                        whiteSpace: 'nowrap',
                      }}>
                        {TYPE_LABELS[s.type] || s.type}
                      </span>
                      <span style={{ fontSize: '0.875rem', color: '#111827' }}>{s.name}</span>
                      {s.reference && (
                        <span style={{ fontSize: '0.75rem', color: '#9ca3af', marginLeft: 'auto' }}>{s.reference}</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Mobile Filter-Button */}
            <button
              type="button"
              onClick={() => setDrawerOpen(true)}
              aria-label="Filter oeffnen"
              style={{
                padding: '0.75rem 1rem',
                background: hasFilters ? '#1e3a5f' : '#f9fafb',
                color: hasFilters ? '#fff' : '#374151',
                border: '2px solid',
                borderColor: hasFilters ? '#1e3a5f' : '#d1d5db',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                minHeight: '48px',
                fontSize: '0.875rem',
                fontWeight: 500,
                display: 'none',
              }}
              className="mobile-filter-btn"
            >
              Filter {hasFilters && `(${[typeFilter, gremiumFilter, yearFilter, statusFilter].filter(Boolean).length})`}
            </button>

            <button
              type="submit"
              disabled={inputValue.trim().length < 2 || loading}
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
                opacity: inputValue.trim().length < 2 ? 0.5 : 1,
                whiteSpace: 'nowrap',
              }}
            >
              {loading ? 'Suche...' : 'Suchen'}
            </button>
          </form>

          <p style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.375rem' }}>
            Mindestens 2 Zeichen eingeben &bull; Autocomplete ab 3 Zeichen
          </p>
        </div>

        {/* Layout: Filter-Sidebar + Ergebnisse */}
        <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>

          {/* Filter-Sidebar (Desktop) */}
          <aside
            aria-label="Suchfilter"
            style={{
              width: '220px',
              flexShrink: 0,
              background: '#f9fafb',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              padding: '1.25rem',
            }}
            className="filter-sidebar"
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ margin: 0, fontSize: '0.875rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#6b7280' }}>
                Filter
              </h2>
              {hasFilters && (
                <button
                  onClick={clearAllFilters}
                  style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.75rem' }}
                >
                  Alle loeschen
                </button>
              )}
            </div>
            <FilterContent />
          </aside>

          {/* Ergebnis-Bereich */}
          <main id="search-results" style={{ flex: 1, minWidth: 0 }} aria-live="polite" aria-busy={loading}>

            {/* Loading State */}
            {loading && (
              <div style={{ textAlign: 'center', padding: '3rem 0', color: '#6b7280' }}>
                <div style={spinnerStyle} aria-hidden="true" />
                <p style={{ marginTop: '1rem' }}>Suche laeuft...</p>
              </div>
            )}

            {/* Ergebnis-Header */}
            {!loading && results && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#6b7280' }} role="status">
                  <strong>{results.total.toLocaleString('de-DE')}</strong> Ergebnis{results.total !== 1 ? 'se' : ''} fuer &bdquo;{results.query}&ldquo;
                  {hasFilters && ' (gefiltert)'}
                </p>
                {results.total > 0 && (
                  <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                    Seite {results.page} von {results.total_pages}
                  </span>
                )}
              </div>
            )}

            {/* Aktive Filter als Tags */}
            {hasFilters && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                {typeFilter && (
                  <FilterTag label={`Typ: ${TYPE_LABELS[typeFilter] || typeFilter}`} onRemove={() => applyFilter('type', '')} />
                )}
                {gremiumFilter && (
                  <FilterTag label={`Gremium: ${gremiumFilter}`} onRemove={() => applyFilter('gremium', '')} />
                )}
                {yearFilter && (
                  <FilterTag label={`Jahr: ${yearFilter}`} onRemove={() => applyFilter('year', '')} />
                )}
                {statusFilter && (
                  <FilterTag label={`Status: ${MEETING_STATE_LABELS[statusFilter] || statusFilter}`} onRemove={() => applyFilter('status', '')} />
                )}
              </div>
            )}

            {/* Empty State */}
            {!loading && results && results.total === 0 && (
              <div style={{ textAlign: 'center', padding: '4rem 2rem', color: '#6b7280' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>?</div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem', color: '#374151' }}>
                  Keine Ergebnisse
                </h2>
                <p style={{ maxWidth: '400px', margin: '0 auto' }}>
                  Fuer &bdquo;{results.query}&ldquo; wurden keine Dokumente gefunden.
                  Versuche andere Begriffe oder entferne Filter.
                </p>
                {hasFilters && (
                  <button
                    onClick={clearAllFilters}
                    style={{ marginTop: '1rem', padding: '0.5rem 1.5rem', background: '#1e3a5f', color: '#fff', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' }}
                  >
                    Filter zuruecksetzen
                  </button>
                )}
              </div>
            )}

            {/* Noch keine Suche */}
            {!loading && !results && !query && (
              <div style={{ textAlign: 'center', padding: '4rem 2rem', color: '#9ca3af' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>&#128269;</div>
                <p style={{ fontSize: '1rem' }}>
                  Gib einen Suchbegriff ein, um Vorlagen, Sitzungen und Personen zu durchsuchen.
                </p>
              </div>
            )}

            {/* Ergebnis-Liste */}
            {!loading && results && results.data.length > 0 && (
              <>
                <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {results.data.map((item, i) => (
                    <li key={item.id || i}>
                      <Link
                        href={getItemLink(item)}
                        style={{
                          display: 'block',
                          padding: '1rem 1.25rem',
                          background: '#fff',
                          border: '1px solid #e5e7eb',
                          borderRadius: '0.5rem',
                          textDecoration: 'none',
                          color: 'inherit',
                          transition: 'border-color 0.15s, box-shadow 0.15s',
                        }}
                        onMouseEnter={e => {
                          (e.currentTarget as HTMLElement).style.borderColor = '#1e3a5f';
                          (e.currentTarget as HTMLElement).style.boxShadow = '0 2px 8px rgba(30,58,95,0.1)';
                        }}
                        onMouseLeave={e => {
                          (e.currentTarget as HTMLElement).style.borderColor = '#e5e7eb';
                          (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                        }}
                      >
                        {/* Header-Zeile */}
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.5rem' }}>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '0.25rem',
                            fontSize: '0.625rem',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            color: '#fff',
                            background: TYPE_COLORS[item.type] || '#6b7280',
                            whiteSpace: 'nowrap',
                            flexShrink: 0,
                            marginTop: '2px',
                          }}>
                            {TYPE_LABELS[item.type] || item.type}
                          </span>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ fontWeight: 600, fontSize: '0.9375rem', color: '#111827', lineHeight: 1.4 }}>
                              {item.highlight?.name ? (
                                <HighlightedText html={item.highlight.name[0]} />
                              ) : (
                                item.name
                              )}
                            </div>
                            {/* Meta-Zeile */}
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', marginTop: '0.25rem', fontSize: '0.75rem', color: '#6b7280' }}>
                              {item.reference && (
                                <span>
                                  {item.highlight?.reference ? (
                                    <HighlightedText html={item.highlight.reference[0]} />
                                  ) : item.reference}
                                </span>
                              )}
                              {item.date && <span>{formatDate(item.date)}</span>}
                              {item.paper_type && <span>{item.paper_type}</span>}
                              {item.meeting_state && (
                                <span style={{
                                  padding: '0.1rem 0.4rem',
                                  borderRadius: '0.25rem',
                                  background: '#f3f4f6',
                                  fontSize: '0.7rem',
                                }}>
                                  {MEETING_STATE_LABELS[item.meeting_state] || item.meeting_state}
                                </span>
                              )}
                              {item.organization_name && <span>{item.organization_name}</span>}
                            </div>
                          </div>
                        </div>

                        {/* Highlight-Snippets */}
                        {item.highlight?.content && (
                          <div style={{
                            marginTop: '0.5rem',
                            paddingTop: '0.5rem',
                            borderTop: '1px solid #f3f4f6',
                            fontSize: '0.8125rem',
                            color: '#4b5563',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.25rem',
                          }}>
                            {item.highlight.content.slice(0, 2).map((snippet, si) => (
                              <p key={si} style={{ margin: 0 }}>
                                &hellip;<HighlightedText html={snippet} />&hellip;
                              </p>
                            ))}
                          </div>
                        )}
                      </Link>
                    </li>
                  ))}
                </ul>

                {/* Pagination */}
                {results.total_pages > 1 && (
                  <Pagination
                    currentPage={results.page}
                    totalPages={results.total_pages}
                    onPageChange={newPage => {
                      setPage(newPage);
                      updateURL({ page: newPage });
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                  />
                )}
              </>
            )}
          </main>
        </div>
      </div>

      {/* Responsive Styles */}
      <style>{`
        mark {
          background: #fef08a;
          color: inherit;
          padding: 0 2px;
          border-radius: 2px;
        }
        .sr-only {
          position: absolute;
          width: 1px;
          height: 1px;
          padding: 0;
          margin: -1px;
          overflow: hidden;
          clip: rect(0,0,0,0);
          white-space: nowrap;
          border: 0;
        }
        @media (max-width: 768px) {
          .filter-sidebar { display: none !important; }
          .mobile-filter-btn { display: flex !important; }
        }
      `}</style>
    </>
  );
}

// ============================================================
// Teilkomponenten
// ============================================================

function FilterTag({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.375rem',
      padding: '0.25rem 0.5rem',
      background: '#e0e7ff',
      color: '#3730a3',
      borderRadius: '0.375rem',
      fontSize: '0.75rem',
      fontWeight: 500,
    }}>
      {label}
      <button
        onClick={onRemove}
        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6366f1', lineHeight: 1, padding: 0, fontSize: '0.875rem' }}
        aria-label={`${label} entfernen`}
      >
        &times;
      </button>
    </span>
  );
}

function Pagination({ currentPage, totalPages, onPageChange }: {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) {
  const pages: (number | '...')[] = [];
  const delta = 2;

  for (let i = 1; i <= totalPages; i++) {
    if (
      i === 1 ||
      i === totalPages ||
      (i >= currentPage - delta && i <= currentPage + delta)
    ) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== '...') {
      pages.push('...');
    }
  }

  return (
    <nav aria-label="Seitennavigation" style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '0.375rem', flexWrap: 'wrap' }}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        style={paginationBtnStyle(false, currentPage === 1)}
        aria-label="Vorherige Seite"
      >
        &lsaquo;
      </button>
      {pages.map((p, i) =>
        p === '...' ? (
          <span key={`ellipsis-${i}`} style={{ padding: '0.5rem 0.25rem', color: '#9ca3af' }}>...</span>
        ) : (
          <button
            key={p}
            onClick={() => onPageChange(p as number)}
            style={paginationBtnStyle(p === currentPage, false)}
            aria-label={`Seite ${p}`}
            aria-current={p === currentPage ? 'page' : undefined}
          >
            {p}
          </button>
        )
      )}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        style={paginationBtnStyle(false, currentPage === totalPages)}
        aria-label="Naechste Seite"
      >
        &rsaquo;
      </button>
    </nav>
  );
}

// ============================================================
// Styles
// ============================================================

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.75rem',
  fontWeight: 600,
  color: '#374151',
  marginBottom: '0.375rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

const selectStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.375rem 0.5rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.25rem',
  fontSize: '0.875rem',
  background: '#fff',
  cursor: 'pointer',
};

const facetBtnStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  width: '100%',
  padding: '0.375rem 0.5rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.25rem',
  cursor: 'pointer',
  fontSize: '0.8125rem',
  fontWeight: 500,
  transition: 'all 0.1s',
};

const facetCountStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  background: 'rgba(0,0,0,0.1)',
  padding: '0.1rem 0.35rem',
  borderRadius: '0.75rem',
};

const spinnerStyle: React.CSSProperties = {
  width: '40px',
  height: '40px',
  border: '3px solid #e5e7eb',
  borderTopColor: '#1e3a5f',
  borderRadius: '50%',
  animation: 'spin 0.8s linear infinite',
  margin: '0 auto',
};

function paginationBtnStyle(active: boolean, disabled: boolean): React.CSSProperties {
  return {
    minWidth: '36px',
    height: '36px',
    padding: '0 0.5rem',
    border: '1px solid',
    borderColor: active ? '#1e3a5f' : '#d1d5db',
    borderRadius: '0.375rem',
    background: active ? '#1e3a5f' : disabled ? '#f9fafb' : '#fff',
    color: active ? '#fff' : disabled ? '#9ca3af' : '#374151',
    fontWeight: active ? 700 : 400,
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: '0.875rem',
  };
}
