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
      fetch().then(r => r.json()),
      fetch().then(r => r.json()),
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

  const getFraktion = (person: Person): string => {
    const m = person.membership?.find(
      mb => fraktionen.some(f => f.id === mb.organization)
    );
    return m?.organizationName || 'Parteilos';
  };

  const getGremien = (person: Person): string[] => {
    return (
      person.membership
        ?.filter(mb => gremien.some(g => g.id === mb.organization))
        .map(mb => mb.organizationName || '')
        .filter(Boolean) || []
    );
  };

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Personen &amp; Mandatstraeger</h1>
      <p style={{ color: '#6b7280', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
        Verzeichnis aller Mandatstraeger und Mitglieder kommunaler Gremien.
      </p>

      {/* Filter-Bereich */}
      <fieldset
        style={{ border: 'none', padding: 0, marginBottom: '1.5rem' }}
        aria-label=Personen filtern
      >
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 240px' }}>
            <label htmlFor=search-persons style={labelStyle}>
              Name suchen
            </label>
            <input
              id=search-persons
              type=search
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder=Name eingeben...
              aria-label=Nach Name suchen
              style={inputStyle}
            />
          </div>
          <div style={{ flex: '0 1 200px' }}>
            <label htmlFor=filter-gremium style={labelStyle}>
              Gremium
            </label>
            <select
              id=filter-gremium
              value={filterGremium}
              onChange={e => setFilterGremium(e.target.value)}
              style={selectStyle}
            >
              <option value=>Alle Gremien</option>
              {gremien.map(g => (
                <option key={g.id} value={g.id}>{g.name}</option>
              ))}
            </select>
          </div>
          <div style={{ flex: '0 1 200px' }}>
            <label htmlFor=filter-fraktion style={labelStyle}>
              Fraktion
            </label>
            <select
              id=filter-fraktion
              value={filterFraktion}
              onChange={e => setFilterFraktion(e.target.value)}
              style={selectStyle}
            >
              <option value=>Alle Fraktionen</option>
              {fraktionen.map(f => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          </div>
          <div style={{ flex: '0 1 200px' }}>
            <label htmlFor=filter-funktion style={labelStyle}>
              Funktion
            </label>
            <select
              id=filter-funktion
              value={filterFunktion}
              onChange={e => setFilterFunktion(e.target.value)}
              style={selectStyle}
            >
              <option value=>Alle Funktionen</option>
              {funktionen.map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>
        </div>
      </fieldset>

      {/* Ergebnisse */}
      <div aria-live=polite aria-atomic=true className=sr-only>
        {!loading && }
      </div>

      {loading ? (
        <p role=status style={{ color: '#6b7280', textAlign: 'center', padding: '3rem' }}>
          Laden...
        </p>
      ) : persons.length === 0 ? (
        <p style={{ color: '#9ca3af', textAlign: 'center', padding: '3rem' }}>
          Keine Personen gefunden.
        </p>
      ) : (
        <ul
          style={{
            listStyle: 'none',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '1rem',
          }}
        >
          {persons.map(person => (
            <li key={person.id}>
              <a
                href={}
                style={{
                  display: 'block',
                  background: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  padding: '1.25rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'box-shadow 0.15s ease',
                }}
                onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)')}
                onMouseLeave={e => (e.currentTarget.style.boxShadow = 'none')}
              >
                {/* Avatar Placeholder */}
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '50%',
                  background: '#1e3a5f',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.125rem',
                  fontWeight: 700,
                  marginBottom: '0.75rem',
                }} aria-hidden=true>
                  {(person.givenName?.[0] || '').toUpperCase()}
                  {(person.familyName?.[0] || '').toUpperCase()}
                </div>

                <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.25rem' }}>
                  {person.formOfAddress ?  : ''}
                  {person.name}
                </h2>

                <p style={{ fontSize: '0.8125rem', color: '#4b5563', margin: '0 0 0.5rem' }}>
                  {getFraktion(person)}
                </p>

                {getGremien(person).length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                    {getGremien(person).slice(0, 3).map((g, i) => (
                      <span
                        key={i}
                        style={{
                          padding: '0.125rem 0.5rem',
                          borderRadius: '9999px',
                          fontSize: '0.6875rem',
                          background: '#eff6ff',
                          color: '#1e3a5f',
                          border: '1px solid #bfdbfe',
                        }}
                      >
                        {g}
                      </span>
                    ))}
                    {getGremien(person).length > 3 && (
                      <span style={{
                        padding: '0.125rem 0.5rem',
                        fontSize: '0.6875rem',
                        color: '#6b7280',
                      }}>
                        +{getGremien(person).length - 3} weitere
                      </span>
                    )}
                  </div>
                )}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.75rem',
  fontWeight: 600,
  color: '#374151',
  marginBottom: '0.25rem',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.5rem 1rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  minHeight: '44px',
};

const selectStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.5rem 1rem',
  border: '1px solid #d1d5db',
  borderRadius: '0.375rem',
  fontSize: '0.875rem',
  minHeight: '44px',
  background: '#fff',
};
