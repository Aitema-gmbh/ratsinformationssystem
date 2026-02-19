'use client';

import { useEffect, useState } from 'react';

interface Meeting {
  id: string;
  name: string;
  start: string;
  end?: string;
  meeting_state: string;
  cancelled: boolean;
  organization?: string;
}

export default function SitzungenPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'upcoming' | 'past'>('upcoming');

  useEffect(() => {
    // Fetch from OParl API
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/meetings?` + new URLSearchParams({
      view,
      page: '1',
    }))
      .then(r => r.json())
      .then(data => {
        setMeetings(data.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [view]);

  const formatDate = (iso: string) => {
    return new Intl.DateTimeFormat('de-DE', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(iso));
  };

  const stateLabels: Record<string, string> = {
    scheduled: 'Geplant',
    invited: 'Eingeladen',
    running: 'Laufend',
    completed: 'Abgeschlossen',
    cancelled: 'Abgesagt',
  };

  const stateColors: Record<string, string> = {
    scheduled: '#3b82f6',
    invited: '#8b5cf6',
    running: '#f59e0b',
    completed: '#16a34a',
    cancelled: '#dc2626',
  };

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>Sitzungen</h1>
      
      <div role="tablist" aria-label="Sitzungsansicht" style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <button
          role="tab"
          aria-selected={view === 'upcoming'}
          onClick={() => setView('upcoming')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '0.375rem',
            border: '1px solid #d1d5db',
            background: view === 'upcoming' ? '#1e3a5f' : '#fff',
            color: view === 'upcoming' ? '#fff' : '#374151',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '0.875rem',
            minHeight: '44px',
          }}
        >
          Anstehend
        </button>
        <button
          role="tab"
          aria-selected={view === 'past'}
          onClick={() => setView('past')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '0.375rem',
            border: '1px solid #d1d5db',
            background: view === 'past' ? '#1e3a5f' : '#fff',
            color: view === 'past' ? '#fff' : '#374151',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '0.875rem',
            minHeight: '44px',
          }}
        >
          Vergangen
        </button>
      </div>

      {loading ? (
        <p role="status" style={{ color: '#6b7280', textAlign: 'center', padding: '3rem' }}>Laden...</p>
      ) : meetings.length === 0 ? (
        <p style={{ color: '#9ca3af', textAlign: 'center', padding: '3rem' }}>
          Keine Sitzungen gefunden.
        </p>
      ) : (
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {meetings.map(m => (
            <li key={m.id}>
              <a
                href={`/sitzungen/${m.id}`}
                style={{
                  display: 'block',
                  background: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  padding: '1.25rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  borderLeft: `4px solid ${stateColors[m.meeting_state] || '#6b7280'}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h2 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0 }}>{m.name}</h2>
                    <time style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {formatDate(m.start)}
                    </time>
                  </div>
                  <span
                    style={{
                      padding: '0.25rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: '#fff',
                      background: stateColors[m.meeting_state] || '#6b7280',
                    }}
                    aria-label={`Status: ${stateLabels[m.meeting_state] || m.meeting_state}`}
                  >
                    {stateLabels[m.meeting_state] || m.meeting_state}
                  </span>
                </div>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
