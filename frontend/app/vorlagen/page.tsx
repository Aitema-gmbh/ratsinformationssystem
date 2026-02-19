'use client';

import { useEffect, useState } from 'react';

interface Paper {
  id: string;
  name: string;
  reference: string;
  date: string;
  paper_type: string;
}

export default function VorlagenPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [paperType, setPaperType] = useState('');

  useEffect(() => {
    const params = new URLSearchParams({ page: '1' });
    if (search) params.set('q', search);
    if (paperType) params.set('paper_type', paperType);

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/papers?${params}`)
      .then(r => r.json())
      .then(data => {
        setPapers(data.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [search, paperType]);

  const paperTypes = [
    'Vorlage', 'Antrag', 'Anfrage', 'Beschlussvorlage',
    'Mitteilung', 'Stellungnahme', 'Bericht',
  ];

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>Vorlagen &amp; Drucksachen</h1>
      
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div>
          <label htmlFor="search-papers" className="sr-only">Suche</label>
          <input
            id="search-papers"
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Vorlagen durchsuchen..."
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              fontSize: '0.875rem',
              minHeight: '44px',
              minWidth: '280px',
            }}
          />
        </div>
        <div>
          <label htmlFor="filter-type" className="sr-only">Typ</label>
          <select
            id="filter-type"
            value={paperType}
            onChange={(e) => setPaperType(e.target.value)}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              fontSize: '0.875rem',
              minHeight: '44px',
              background: '#fff',
            }}
          >
            <option value="">Alle Typen</option>
            {paperTypes.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <p role="status" style={{ color: '#6b7280', textAlign: 'center', padding: '3rem' }}>Laden...</p>
      ) : papers.length === 0 ? (
        <p style={{ color: '#9ca3af', textAlign: 'center', padding: '3rem' }}>
          Keine Vorlagen gefunden.
        </p>
      ) : (
        <div style={{
          background: '#fff',
          borderRadius: '0.5rem',
          border: '1px solid #e5e7eb',
          overflow: 'hidden',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }} aria-label="Vorlagen und Drucksachen">
            <thead>
              <tr>
                <th scope="col" style={thStyle}>Drucksachennr.</th>
                <th scope="col" style={thStyle}>Titel</th>
                <th scope="col" style={thStyle}>Typ</th>
                <th scope="col" style={thStyle}>Datum</th>
              </tr>
            </thead>
            <tbody>
              {papers.map(p => (
                <tr key={p.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={tdStyle}>
                    <a href={`/vorlagen/${p.id}`} style={{ color: '#1d4ed8', textDecoration: 'none' }}>
                      {p.reference}
                    </a>
                  </td>
                  <td style={tdStyle}>{p.name}</td>
                  <td style={tdStyle}>
                    <span style={{
                      padding: '0.125rem 0.5rem',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                      background: '#f3f4f6',
                      color: '#374151',
                    }}>
                      {p.paper_type}
                    </span>
                  </td>
                  <td style={tdStyle}>
                    {new Intl.DateTimeFormat('de-DE').format(new Date(p.date))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const thStyle: React.CSSProperties = {
  background: '#f9fafb',
  padding: '0.75rem 1rem',
  textAlign: 'left',
  fontWeight: 600,
  fontSize: '0.875rem',
  color: '#374151',
  borderBottom: '2px solid #e5e7eb',
};

const tdStyle: React.CSSProperties = {
  padding: '0.75rem 1rem',
  fontSize: '0.875rem',
};
