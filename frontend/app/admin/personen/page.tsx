'use client';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface Person {
  id: string;
  name: string;
  givenName?: string;
  familyName?: string;
  email?: string;
  phone?: string;
  status?: string;
}

interface PersonListResponse {
  data: Person[];
  pagination: {
    totalElements: number;
    currentPage: number;
    totalPages: number;
  };
}

export default function PersonenAdmin() {
  const [persons, setPersons] = useState<Person[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const loadPersons = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(page), per_page: '20' });
      if (search) params.set('search', search);
      const res = await fetch(`/api/admin/persons?${params}`);
      if (res.ok) {
        const data: PersonListResponse = await res.json();
        setPersons(data.data || []);
        setTotal(data.pagination?.totalElements || 0);
      } else {
        setError(`Fehler ${res.status}`);
      }
    } catch {
      setError('Verbindungsfehler');
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => { loadPersons(); }, [loadPersons]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>Personen</h1>
          <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            {total} Personen gesamt
          </p>
        </div>
        <Link
          href="/personen"
          style={{
            background: '#f1f5f9', color: '#374151', border: '1px solid #e2e8f0',
            padding: '0.5rem 1rem', borderRadius: '0.375rem',
            textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500,
          }}
        >
          Oeffentliche Ansicht →
        </Link>
      </div>

      {/* Search */}
      <div style={{ marginBottom: '1rem' }}>
        <input
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          placeholder="Personen suchen..."
          style={{
            width: '300px',
            border: '1px solid #e2e8f0', borderRadius: '0.375rem',
            padding: '0.5rem 0.75rem', fontSize: '0.875rem',
          }}
        />
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
              {['Name', 'E-Mail', 'Telefon', 'Status', 'Aktionen'].map((h) => (
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
            ) : persons.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>Keine Personen gefunden</td></tr>
            ) : (
              persons.map((person, i) => (
                <tr key={person.id} style={{ borderTop: i > 0 ? '1px solid #f1f5f9' : undefined }}>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <div style={{ fontWeight: 500, color: '#0f172a' }}>
                      {person.name || `${person.givenName || ''} ${person.familyName || ''}`.trim() || '–'}
                    </div>
                  </td>
                  <td style={{ padding: '0.875rem 1rem', fontSize: '0.875rem', color: '#374151' }}>
                    {person.email ? (
                      <a href={`mailto:${person.email}`} style={{ color: '#3b82f6' }}>{person.email}</a>
                    ) : '–'}
                  </td>
                  <td style={{ padding: '0.875rem 1rem', fontSize: '0.875rem', color: '#64748b' }}>
                    {person.phone || '–'}
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    {person.status && (
                      <span style={{
                        background: '#f1f5f9', color: '#374151',
                        padding: '0.125rem 0.5rem', borderRadius: '9999px',
                        fontSize: '0.75rem', fontWeight: 500,
                      }}>
                        {person.status}
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <Link
                      href={`/personen/${person.id}`}
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
