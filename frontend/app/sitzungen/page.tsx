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

const stateConfig: Record<string, { label: string; color: string; dot: string; badgeClass: string }> = {
  scheduled: { label: 'Geplant',       color: '#3b82f6', dot: '#3b82f6', badgeClass: 'badge-blue' },
  invited:   { label: 'Eingeladen',    color: '#8b5cf6', dot: '#8b5cf6', badgeClass: 'badge-purple' },
  running:   { label: 'Laufend',       color: '#d97706', dot: '#d97706', badgeClass: 'badge-amber' },
  completed: { label: 'Abgeschlossen', color: '#059669', dot: '#059669', badgeClass: 'badge-green' },
  cancelled: { label: 'Abgesagt',      color: '#dc2626', dot: '#dc2626', badgeClass: 'badge-red' },
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

function SkeletonCard() {
  return (
    <li>
      <div className="aitema-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div className="skeleton" style={{ height: '1.125rem', width: '55%' }} />
          <div className="skeleton" style={{ height: '0.875rem', width: '35%' }} />
        </div>
        <div className="skeleton" style={{ height: '1.5rem', width: '5rem', borderRadius: '9999px' }} />
      </div>
    </li>
  );
}

export default function SitzungenPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'upcoming' | 'past'>('upcoming');

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ view, page: '1' });
    fetch(API_BASE + '/api/meetings?' + params.toString())
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

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.375rem' }}>
          <div style={{
            width: '40px', height: '40px',
            background: 'linear-gradient(135deg, #dbeafe, #bfdbfe)',
            borderRadius: '10px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1e40af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <h1 className="page-title" style={{ marginBottom: 0 }}>Sitzungen</h1>
        </div>
        <p className="page-subtitle">Alle Sitzungen der kommunalen Gremien im Ueberblick</p>
      </div>

      {/* Tab Switch */}
      <div
        role="tablist"
        aria-label="Sitzungsansicht"
        style={{
          display: 'inline-flex',
          background: '#f1f5f9',
          border: '1px solid #e2e8f0',
          borderRadius: '0.5rem',
          padding: '3px',
          gap: '2px',
          marginBottom: '1.75rem',
        }}
      >
        {(['upcoming', 'past'] as const).map((v) => (
          <button
            key={v}
            role="tab"
            aria-selected={view === v}
            onClick={() => setView(v)}
            style={{
              padding: '0.5rem 1.125rem',
              borderRadius: '0.375rem',
              border: 'none',
              background: view === v ? '#fff' : 'transparent',
              color: view === v ? '#0f172a' : '#64748b',
              cursor: 'pointer',
              fontWeight: view === v ? 600 : 500,
              fontSize: '0.875rem',
              minHeight: '40px',
              fontFamily: 'inherit',
              boxShadow: view === v ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.15s',
              letterSpacing: '-0.01em',
            }}
          >
            {v === 'upcoming' ? 'Anstehend' : 'Vergangen'}
          </button>
        ))}
      </div>

      {/* Live region for screen readers */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {!loading && (meetings.length + ' Sitzungen geladen')}
      </div>

      {/* Skeleton or Content */}
      {loading ? (
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
          {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)}
        </ul>
      ) : meetings.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '5rem 2rem',
          background: '#fff',
          borderRadius: '0.75rem',
          border: '1px solid #e2e8f0',
        }}>
          <div style={{
            width: '64px', height: '64px',
            background: '#f1f5f9',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 1rem',
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <p style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: '0.375rem' }}>
            Keine Sitzungen gefunden
          </p>
          <p style={{ fontSize: '0.875rem', color: '#64748b' }}>
            {view === 'upcoming' ? 'Aktuell sind keine Sitzungen geplant.' : 'Es liegen keine vergangenen Sitzungen vor.'}
          </p>
        </div>
      ) : (
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
          {meetings.map(m => {
            const state = stateConfig[m.meeting_state] || { label: m.meeting_state, color: '#64748b', dot: '#64748b', badgeClass: 'badge-slate' };
            const slug = m.id.split('/').pop() || m.id;
            return (
              <li key={m.id}>
                <a
                  href={'/sitzungen/' + slug}
                  style={{
                    display: 'block',
                    background: '#fff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.5rem',
                    padding: '1rem 1.25rem',
                    textDecoration: 'none',
                    color: 'inherit',
                    transition: 'border-color 0.2s, box-shadow 0.2s, transform 0.2s',
                    borderLeft: '3px solid ' + state.color,
                    outline: 'none',
                  }}
                  onMouseEnter={e => {
                    const el = e.currentTarget as HTMLElement;
                    el.style.borderColor = state.color;
                    el.style.boxShadow = '0 4px 16px rgba(0,0,0,0.08)';
                    el.style.transform = 'translateY(-1px)';
                  }}
                  onMouseLeave={e => {
                    const el = e.currentTarget as HTMLElement;
                    el.style.borderColor = '#e2e8f0';
                    el.style.boxShadow = 'none';
                    el.style.transform = 'translateY(0)';
                    el.style.borderLeftColor = state.color;
                  }}
                  onFocus={e => {
                    (e.currentTarget as HTMLElement).style.boxShadow = '0 0 0 3px rgba(59,130,246,0.2)';
                  }}
                  onBlur={e => {
                    (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h2 style={{
                        fontSize: '0.9375rem',
                        fontWeight: 600,
                        color: '#0f172a',
                        margin: '0 0 0.25rem',
                        letterSpacing: '-0.01em',
                        lineHeight: 1.4,
                      }}>
                        {m.name}
                      </h2>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                          <circle cx="12" cy="12" r="10"/>
                          <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        <time dateTime={m.start} style={{ fontSize: '0.8125rem', color: '#64748b' }}>
                          {formatDate(m.start)}
                        </time>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
                      <span
                        className={'badge ' + state.badgeClass}
                        aria-label={'Status: ' + state.label}
                      >
                        <span
                          className="status-dot"
                          style={{ background: state.dot, marginRight: '0.375rem' }}
                          aria-hidden="true"
                        />
                        {state.label}
                      </span>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <polyline points="9 18 15 12 9 6"/>
                      </svg>
                    </div>
                  </div>
                </a>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
