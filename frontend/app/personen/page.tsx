'use client';

import { useEffect, useState, useMemo } from 'react';

interface Person {
  id: string;
  name: string;
  familyName: string;
  givenName: string;
  formOfAddress?: string;
  title?: string[];
  email?: string[];
  phone?: string[];
  status?: string[];
  membership?: Membership[];
}

interface Membership {
  id: string;
  organization: string;
  organizationName?: string;
  role?: string;
  startDate?: string;
  endDate?: string;
}

interface Organization {
  id: string;
  name: string;
  organizationType?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

const fraktionColors = [
  'rgba(59,130,246,0.12)', 'rgba(139,92,246,0.12)',
  'rgba(16,185,129,0.12)', 'rgba(245,158,11,0.12)',
  'rgba(239,68,68,0.12)',
];
const fraktionBorders = [
  '#93c5fd', '#c4b5fd', '#6ee7b7', '#fcd34d', '#fca5a5',
];
const fraktionText = [
  '#1e40af', '#5b21b6', '#065f46', '#92400e', '#991b1b',
];

function PersonCard({ person, fraktionen, gremien }: {
  person: Person;
  fraktionen: Organization[];
  gremien: Organization[];
}) {
  const initials = (
    (person.givenName?.[0] || '').toUpperCase() +
    (person.familyName?.[0] || '').toUpperCase()
  );

  const fraktion = person.membership?.find(
    mb => fraktionen.some(f => f.id === mb.organization)
  );
  const fraktionName = fraktion?.organizationName || 'Parteilos';

  const personGremien = person.membership
    ?.filter(mb => gremien.some(g => g.id === mb.organization))
    .map(mb => mb.organizationName || '')
    .filter(Boolean) || [];

  const colorIdx = fraktionName.length % fraktionColors.length;

  return (
    <li>
      <a
        href={'/personen/' + (person.id.split('/').pop() || person.id)}
        style={{
          display: 'block',
          background: '#fff',
          border: '1px solid #e2e8f0',
          borderRadius: '0.625rem',
          padding: '1.25rem',
          textDecoration: 'none',
          color: 'inherit',
          height: '100%',
          transition: 'border-color 0.2s, box-shadow 0.2s, transform 0.2s',
          outline: 'none',
        }}
        onMouseEnter={e => {
          (e.currentTarget as HTMLElement).style.borderColor = '#3b82f6';
          (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 16px rgba(59,130,246,0.1)';
          (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
        }}
        onMouseLeave={e => {
          (e.currentTarget as HTMLElement).style.borderColor = '#e2e8f0';
          (e.currentTarget as HTMLElement).style.boxShadow = 'none';
          (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
        }}
        onFocus={e => {
          (e.currentTarget as HTMLElement).style.boxShadow = '0 0 0 3px rgba(59,130,246,0.2)';
        }}
        onBlur={e => {
          (e.currentTarget as HTMLElement).style.boxShadow = 'none';
        }}
      >
        {/* Avatar */}
        <div style={{
          width: '52px', height: '52px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #1e3a5f, #1e40af)',
          color: '#fff',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.0625rem', fontWeight: 700,
          marginBottom: '0.875rem',
          flexShrink: 0,
          boxShadow: '0 2px 8px rgba(30,58,95,0.25)',
          letterSpacing: '0.02em',
        }} aria-hidden="true">
          {initials}
        </div>

        {/* Name */}
        <h2 style={{
          fontSize: '0.9375rem', fontWeight: 700,
          color: '#0f172a', margin: '0 0 0.25rem',
          letterSpacing: '-0.01em', lineHeight: 1.3,
        }}>
          {person.formOfAddress ? person.formOfAddress + ' ' : ''}
          {person.name}
        </h2>

        {/* Fraktion */}
        <div style={{ marginBottom: '0.75rem' }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            padding: '0.2rem 0.6rem',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: 600,
            background: fraktionColors[colorIdx],
            color: fraktionText[colorIdx],
            border: '1px solid ' + fraktionBorders[colorIdx],
          }}>
            {fraktionName}
          </span>
        </div>

        {/* Gremien */}
        {personGremien.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
            {personGremien.slice(0, 3).map((g, i) => (
              <span key={i} style={{
                padding: '0.2rem 0.5rem',
                borderRadius: '4px',
                fontSize: '0.6875rem',
                background: '#f1f5f9',
                color: '#475569',
                border: '1px solid #e2e8f0',
                fontWeight: 500,
              }}>
                {g}
              </span>
            ))}
            {personGremien.length > 3 && (
              <span style={{ fontSize: '0.6875rem', color: '#94a3b8', padding: '0.2rem 0.25rem' }}>
                +{personGremien.length - 3} weitere
              </span>
            )}
          </div>
        )}
      </a>
    </li>
  );
}

function SkeletonCard() {
  return (
    <li>
      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '0.625rem', padding: '1.25rem' }}>
        <div className="skeleton" style={{ width: '52px', height: '52px', borderRadius: '50%', marginBottom: '0.875rem' }} />
        <div className="skeleton" style={{ height: '0.9375rem', width: '65%', marginBottom: '0.375rem' }} />
        <div className="skeleton" style={{ height: '1.25rem', width: '45%', borderRadius: '9999px', marginBottom: '0.75rem' }} />
        <div style={{ display: 'flex', gap: '0.25rem' }}>
          <div className="skeleton" style={{ height: '1.25rem', width: '60px', borderRadius: '4px' }} />
          <div className="skeleton" style={{ height: '1.25rem', width: '80px', borderRadius: '4px' }} />
        </div>
      </div>
    </li>
  );
}

export default function PersonenPage() {
  const [persons, setPersons] = useState<Person[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterGremium, setFilterGremium] = useState('');
  const [filterFraktion, setFilterFraktion] = useState('');
  const [filterFunktion, setFilterFunktion] = useState('');

  useEffect(() => {
    const params = new URLSearchParams({ page: '1' });
    if (searchQuery) params.set('q', searchQuery);
    if (filterGremium) params.set('organization', filterGremium);
    if (filterFraktion) params.set('faction', filterFraktion);
    if (filterFunktion) params.set('role', filterFunktion);

    Promise.all([
      fetch(API_BASE + '/api/persons?' + params.toString()).then(r => r.json()),
      fetch(API_BASE + '/api/organizations?page=1').then(r => r.json()),
    ])
      .then(([personsData, orgsData]) => {
        setPersons(personsData.data || []);
        setOrganizations(orgsData.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [searchQuery, filterGremium, filterFraktion, filterFunktion]);

  const fraktionen = useMemo(
    () => organizations.filter(o => o.organizationType === 'Fraktion'),
    [organizations]
  );

  const gremien = useMemo(
    () => organizations.filter(o => o.organizationType !== 'Fraktion'),
    [organizations]
  );

  const funktionen = ['Vorsitz', 'Stellvertretung', 'Mitglied', 'Beratendes Mitglied'];
  const hasFilters = !!(searchQuery || filterGremium || filterFraktion || filterFunktion);

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.375rem' }}>
          <div style={{
            width: '40px', height: '40px',
            background: 'linear-gradient(135deg, #d1fae5, #a7f3d0)',
            borderRadius: '10px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#065f46" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h1 className="page-title" style={{ marginBottom: 0 }}>Personen &amp; Mandatstraeger</h1>
        </div>
        <p className="page-subtitle">Verzeichnis aller Mandatstraeger und Mitglieder kommunaler Gremien</p>
      </div>

      {/* Filter Bar */}
      <fieldset style={{ border: 'none', padding: 0, marginBottom: '1.75rem' }} aria-label="Personen filtern">
        <div style={{
          background: '#fff',
          border: '1px solid #e2e8f0',
          borderRadius: '0.625rem',
          padding: '1.125rem 1.25rem',
          display: 'flex',
          gap: '0.875rem',
          flexWrap: 'wrap',
          alignItems: 'flex-end',
        }}>
          <div style={{ flex: '1 1 200px' }}>
            <label htmlFor="search-persons" className="form-label">Name suchen</label>
            <div style={{ position: 'relative' }}>
              <svg
                style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}
                width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
              >
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                id="search-persons"
                type="search"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Name eingeben..."
                className="form-input"
                style={{ paddingLeft: '2.25rem' }}
              />
            </div>
          </div>
          <div style={{ flex: '0 1 180px' }}>
            <label htmlFor="filter-gremium" className="form-label">Gremium</label>
            <select id="filter-gremium" value={filterGremium} onChange={e => setFilterGremium(e.target.value)} className="form-select">
              <option value="">Alle Gremien</option>
              {gremien.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
          </div>
          <div style={{ flex: '0 1 180px' }}>
            <label htmlFor="filter-fraktion" className="form-label">Fraktion</label>
            <select id="filter-fraktion" value={filterFraktion} onChange={e => setFilterFraktion(e.target.value)} className="form-select">
              <option value="">Alle Fraktionen</option>
              {fraktionen.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
          </div>
          <div style={{ flex: '0 1 180px' }}>
            <label htmlFor="filter-funktion" className="form-label">Funktion</label>
            <select id="filter-funktion" value={filterFunktion} onChange={e => setFilterFunktion(e.target.value)} className="form-select">
              <option value="">Alle Funktionen</option>
              {funktionen.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
          {hasFilters && (
            <button
              onClick={() => { setSearchQuery(''); setFilterGremium(''); setFilterFraktion(''); setFilterFunktion(''); }}
              className="btn-secondary"
              style={{ flexShrink: 0, fontSize: '0.875rem', padding: '0.5rem 1rem', minHeight: '44px' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
              Zuruecksetzen
            </button>
          )}
        </div>
      </fieldset>

      {/* Count */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {!loading && (persons.length + ' Personen gefunden')}
      </div>
      {!loading && persons.length > 0 && (
        <p style={{ fontSize: '0.8125rem', color: '#64748b', marginBottom: '1rem', fontWeight: 500 }}>
          {persons.length} {persons.length === 1 ? 'Person' : 'Personen'} gefunden
        </p>
      )}

      {/* Grid */}
      {loading ? (
        <ul style={{ listStyle: 'none', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
          {Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)}
        </ul>
      ) : persons.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '5rem 2rem',
          background: '#fff', borderRadius: '0.75rem', border: '1px solid #e2e8f0',
        }}>
          <div style={{
            width: '64px', height: '64px', background: '#f1f5f9', borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem',
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
            </svg>
          </div>
          <p style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: '0.375rem' }}>Keine Personen gefunden</p>
          <p style={{ fontSize: '0.875rem', color: '#64748b' }}>Versuche andere Filter oder Suchbegriffe.</p>
        </div>
      ) : (
        <ul style={{ listStyle: 'none', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
          {persons.map(person => (
            <PersonCard
              key={person.id}
              person={person}
              fraktionen={fraktionen}
              gremien={gremien}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
