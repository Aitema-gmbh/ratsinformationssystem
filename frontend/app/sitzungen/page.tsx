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

const stateConfig: Record<string, {
  label: string;
  badgeClass: string;
  accentColor: string;
  dotColor: string;
}> = {
  scheduled: {
    label: 'Geplant',
    badgeClass: 'badge-blue',
    accentColor: '#3b82f6',
    dotColor: '#3b82f6',
  },
  invited: {
    label: 'Eingeladen',
    badgeClass: 'badge-indigo',
    accentColor: '#6366f1',
    dotColor: '#6366f1',
  },
  running: {
    label: 'Laufend',
    badgeClass: 'badge-amber',
    accentColor: '#d97706',
    dotColor: '#d97706',
  },
  completed: {
    label: 'Abgeschlossen',
    badgeClass: 'badge-green',
    accentColor: '#059669',
    dotColor: '#059669',
  },
  cancelled: {
    label: 'Abgesagt',
    badgeClass: 'badge-red',
    accentColor: '#dc2626',
    dotColor: '#dc2626',
  },
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

function SkeletonRow() {
  return (
    <li aria-hidden="true">
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '1rem 1.25rem',
        background: '#fff',
        border: '1px solid #e2e8f0',
        borderRadius: '0.75rem',
      }}>
        {/* Date blob */}
        <div className="skeleton" style={{ width: '3.25rem', height: '3.25rem', borderRadius: '0.75rem', flexShrink: 0 }} />
        {/* Text */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div className="skeleton" style={{ height: '1rem', width: '55%' }} />
          <div className="skeleton" style={{ height: '0.75rem', width: '35%' }} />
        </div>
        {/* Badge */}
        <div className="skeleton" style={{ height: '1.5rem', width: '5.5rem', borderRadius: '9999px', flexShrink: 0 }} />
      </div>
    </li>
  );
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return new Intl.DateTimeFormat('de-DE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d);
}

function getDateParts(iso: string) {
  const d = new Date(iso);
  return {
    day: d.getDate().toString(),
    month: d.toLocaleString('de-DE', { month: 'short' }).toUpperCase(),
    time: d.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' }) + ' Uhr',
  };
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

  return (
    <div>
      {/* ── Page Header ── */}
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', marginBottom: '0.5rem' }}>
          <div style={{
            width: '44px',
            height: '44px',
            background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            boxShadow: '0 2px 8px rgba(59,130,246,0.15)',
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e40af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div>
            <h1 className="page-title" style={{ marginBottom: 0 }}>Sitzungen</h1>
          </div>
        </div>
        <p className="page-subtitle">Alle Sitzungen der kommunalen Gremien im Überblick</p>
      </div>

      {/* ── View Toggle ── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div
          role="tablist"
          aria-label="Sitzungsansicht wählen"
          style={{
            display: 'inline-flex',
            background: '#f1f5f9',
            border: '1px solid #e2e8f0',
            borderRadius: '0.625rem',
            padding: '3px',
            gap: '2px',
          }}
        >
          {([
            { value: 'upcoming', label: 'Anstehend', icon: '→' },
            { value: 'past',     label: 'Vergangen',  icon: '←' },
          ] as const).map(({ value, label }) => (
            <button
              key={value}
              role="tab"
              aria-selected={view === value}
              onClick={() => setView(value)}
              style={{
                padding: '0.5rem 1.25rem',
                borderRadius: '0.4375rem',
                border: 'none',
                background: view === value ? '#fff' : 'transparent',
                color: view === value ? '#0f172a' : '#64748b',
                cursor: 'pointer',
                fontWeight: view === value ? 600 : 500,
                fontSize: '0.875rem',
                minHeight: '40px',
                fontFamily: 'inherit',
                boxShadow: view === value ? '0 1px 4px rgba(0,0,0,0.10), 0 0 0 1px rgba(0,0,0,0.04)' : 'none',
                transition: 'all 0.15s',
                letterSpacing: '-0.01em',
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {!loading && meetings.length > 0 && (
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
            {meetings.length} Sitzung{meetings.length !== 1 ? 'en' : ''}
          </span>
        )}
      </div>

      {/* Accessibility live region */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {!loading && `${meetings.length} Sitzungen geladen`}
      </div>

      {/* ── Content ── */}
      {loading ? (
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.625rem' }} aria-label="Lade Sitzungen...">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonRow key={i} />)}
        </ul>
      ) : meetings.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <p className="empty-state-title">Keine Sitzungen gefunden</p>
          <p className="empty-state-desc">
            {view === 'upcoming'
              ? 'Aktuell sind keine kommenden Sitzungen geplant.'
              : 'Es liegen keine vergangenen Sitzungen vor.'}
          </p>
        </div>
      ) : (
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }} aria-label="Sitzungsliste">
          {meetings.map(m => {
            const state = stateConfig[m.meeting_state] || {
              label: m.meeting_state,
              badgeClass: 'badge-slate',
              accentColor: '#64748b',
              dotColor: '#64748b',
            };
            const slug = m.id.split('/').pop() || m.id;
            const { day, month, time } = getDateParts(m.start);

            return (
              <li key={m.id}>
                <a
                  href={`/sitzungen/${slug}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '1rem 1.25rem',
                    background: '#fff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.75rem',
                    textDecoration: 'none',
                    color: 'inherit',
                    transition: 'border-color 0.2s, box-shadow 0.2s, transform 0.2s',
                    borderLeft: `3px solid ${state.accentColor}`,
                    outline: 'none',
                  }}
                  onMouseEnter={e => {
                    const el = e.currentTarget as HTMLElement;
                    el.style.borderColor = state.accentColor;
                    el.style.boxShadow = '0 4px 16px rgba(0,0,0,0.07)';
                    el.style.transform = 'translateY(-1px)';
                  }}
                  onMouseLeave={e => {
                    const el = e.currentTarget as HTMLElement;
                    el.style.borderColor = '#e2e8f0';
                    el.style.boxShadow = 'none';
                    el.style.transform = 'translateY(0)';
                    el.style.borderLeftColor = state.accentColor;
                  }}
                  onFocus={e => {
                    (e.currentTarget as HTMLElement).style.boxShadow = '0 0 0 3px rgba(59,130,246,0.2)';
                  }}
                  onBlur={e => {
                    (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                  }}
                >
                  {/* Date Badge */}
                  <div className="meeting-date" aria-hidden="true">
                    <span className="day">{day}</span>
                    <span className="month">{month}</span>
                  </div>

                  {/* Content */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h2 style={{
                      fontSize: '0.9375rem',
                      fontWeight: 600,
                      color: '#0f172a',
                      margin: '0 0 0.3rem',
                      letterSpacing: '-0.01em',
                      lineHeight: 1.35,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}>
                      {m.name}
                    </h2>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4375rem' }}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12 6 12 12 16 14"/>
                      </svg>
                      <time dateTime={m.start} style={{ fontSize: '0.8125rem', color: '#64748b' }}>
                        {time} &mdash; {formatDate(m.start).split(',').slice(0, 2).join(',')}
                      </time>
                    </div>
                  </div>

                  {/* Status + Arrow */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', flexShrink: 0 }}>
                    <span className={`badge ${state.badgeClass}`} aria-label={`Status: ${state.label}`}>
                      <span className="status-dot" style={{ background: state.dotColor }} aria-hidden="true" />
                      {state.label}
                    </span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <polyline points="9 18 15 12 9 6"/>
                    </svg>
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
