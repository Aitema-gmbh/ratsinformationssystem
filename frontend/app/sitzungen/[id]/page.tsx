'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

// ============================================================
// Typen
// ============================================================

interface MeetingDetail {
  id: string;
  name: string;
  start: string;
  end?: string;
  meeting_state: string;
  cancelled: boolean;
  organization?: {
    id: string;
    name: string;
  };
  location?: {
    description?: string;
    streetAddress?: string;
    postalCode?: string;
    locality?: string;
    room?: string;
  };
  invitation?: {
    id: string;
    accessUrl?: string;
    name?: string;
  };
  resultsProtocol?: {
    id: string;
    accessUrl?: string;
    name?: string;
  };
  verbatimProtocol?: {
    id: string;
    accessUrl?: string;
    name?: string;
  };
}

interface AgendaItem {
  id: string;
  number?: string;
  order?: number;
  name: string;
  public: boolean;
  result?: string;
  resolutionText?: string;
  consultation?: {
    paper?: {
      id: string;
      name: string;
      reference: string;
    };
  };
}

interface Attendee {
  id: string;
  personName: string;
  personId: string;
  status: string;
}

// ============================================================
// Konfiguration
// ============================================================

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

const STATE_CONFIG: Record<string, {
  label: string;
  badgeClass: string;
  accent: string;
  dot: string;
  heroGradient: string;
  icon: React.ReactNode;
}> = {
  scheduled: {
    label: 'Geplant',
    badgeClass: 'badge-blue',
    accent: '#3b82f6',
    dot: '#3b82f6',
    heroGradient: 'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
    ),
  },
  invited: {
    label: 'Eingeladen',
    badgeClass: 'badge-indigo',
    accent: '#6366f1',
    dot: '#6366f1',
    heroGradient: 'linear-gradient(135deg, #1e1b4b 0%, #4338ca 100%)',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
        <polyline points="22,6 12,13 2,6"/>
      </svg>
    ),
  },
  running: {
    label: 'Laufend',
    badgeClass: 'badge-amber',
    accent: '#d97706',
    dot: '#d97706',
    heroGradient: 'linear-gradient(135deg, #451a03 0%, #b45309 100%)',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12 6 12 12 16 14"/>
      </svg>
    ),
  },
  completed: {
    label: 'Abgeschlossen',
    badgeClass: 'badge-green',
    accent: '#059669',
    dot: '#059669',
    heroGradient: 'linear-gradient(135deg, #064e3b 0%, #059669 100%)',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
    ),
  },
  cancelled: {
    label: 'Abgesagt',
    badgeClass: 'badge-red',
    accent: '#dc2626',
    dot: '#dc2626',
    heroGradient: 'linear-gradient(135deg, #450a0a 0%, #dc2626 100%)',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
    ),
  },
};

const ATTENDEE_STATUS: Record<string, { label: string; color: string; bg: string }> = {
  present:  { label: 'Anwesend',     color: '#065f46', bg: '#d1fae5' },
  absent:   { label: 'Abwesend',     color: '#991b1b', bg: '#fee2e2' },
  excused:  { label: 'Entschuldigt', color: '#92400e', bg: '#fef3c7' },
};

// ============================================================
// Hilfsfunktionen
// ============================================================

function formatDate(iso: string) {
  return new Intl.DateTimeFormat('de-DE', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(new Date(iso));
}

function formatTime(iso: string) {
  return new Intl.DateTimeFormat('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso));
}

function getDateParts(iso: string) {
  const d = new Date(iso);
  return {
    day: d.getDate().toString().padStart(2, '0'),
    month: d.toLocaleString('de-DE', { month: 'short' }).toUpperCase(),
    year: d.getFullYear().toString(),
  };
}

// ============================================================
// Skeleton-Loader
// ============================================================

function SkeletonHero() {
  return (
    <div
      aria-hidden="true"
      style={{
        background: 'linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%)',
        borderRadius: '1rem',
        padding: '2rem',
        marginBottom: '1.5rem',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div className="skeleton" style={{ height: '0.875rem', width: '15rem', opacity: 0.3 }} />
        <div className="skeleton" style={{ height: '2rem', width: '70%', opacity: 0.3 }} />
        <div className="skeleton" style={{ height: '1rem', width: '40%', opacity: 0.3 }} />
        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
          <div className="skeleton" style={{ height: '2.25rem', width: '8rem', borderRadius: '9999px', opacity: 0.3 }} />
          <div className="skeleton" style={{ height: '2.25rem', width: '8rem', borderRadius: '9999px', opacity: 0.3 }} />
        </div>
      </div>
    </div>
  );
}

function SkeletonAgendaItem() {
  return (
    <div aria-hidden="true" style={{ display: 'flex', gap: '0', position: 'relative' }}>
      {/* Timeline-Linie */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginRight: '1.25rem', flexShrink: 0 }}>
        <div className="skeleton" style={{ width: '2.5rem', height: '2.5rem', borderRadius: '50%' }} />
        <div className="skeleton" style={{ width: '2px', height: '3rem', borderRadius: '9999px', marginTop: '4px', opacity: 0.4 }} />
      </div>
      {/* Card */}
      <div style={{ flex: 1, paddingBottom: '1.25rem' }}>
        <div className="skeleton" style={{ height: '5rem', borderRadius: '0.75rem' }} />
      </div>
    </div>
  );
}

// ============================================================
// Dokument-Link Komponente
// ============================================================

function DocLink({ href, label, icon }: { href: string; label: string; icon: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.5rem 1rem',
        background: 'rgba(255,255,255,0.15)',
        border: '1px solid rgba(255,255,255,0.25)',
        borderRadius: '0.5rem',
        color: '#fff',
        textDecoration: 'none',
        fontSize: '0.8125rem',
        fontWeight: 600,
        backdropFilter: 'blur(4px)',
        transition: 'background 0.15s, border-color 0.15s',
        minHeight: '40px',
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.25)';
        (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.4)';
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.15)';
        (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255,255,255,0.25)';
      }}
    >
      {icon}
      {label}
    </a>
  );
}

// ============================================================
// Hauptkomponente
// ============================================================

export default function SitzungDetailPage() {
  const params = useParams();
  const meetingId = params.id as string;

  const [meeting, setMeeting] = useState<MeetingDetail | null>(null);
  const [agendaItems, setAgendaItems] = useState<AgendaItem[]>([]);
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!meetingId) return;
    setLoading(true);
    setError(false);

    Promise.all([
      fetch(API_BASE + '/api/meetings/' + meetingId).then(r => {
        if (!r.ok) throw new Error('Not found');
        return r.json();
      }),
      fetch(API_BASE + '/api/meetings/' + meetingId + '/agenda')
        .then(r => r.json())
        .catch(() => ({ data: [] })),
      fetch(API_BASE + '/api/meetings/' + meetingId + '/attendees')
        .then(r => r.json())
        .catch(() => ({ data: [] })),
    ])
      .then(([meetingData, agendaData, attendeesData]) => {
        setMeeting(meetingData);
        const items: AgendaItem[] = agendaData.data || [];
        items.sort((a, b) => (a.order || 0) - (b.order || 0));
        setAgendaItems(items);
        setAttendees(attendeesData.data || []);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [meetingId]);

  // ── Loading ──────────────────────────────────────────────
  if (loading) {
    return (
      <div>
        {/* Breadcrumb Skeleton */}
        <div aria-hidden="true" style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <div className="skeleton" style={{ height: '0.875rem', width: '5rem' }} />
          <div className="skeleton" style={{ height: '0.875rem', width: '1rem' }} />
          <div className="skeleton" style={{ height: '0.875rem', width: '5rem' }} />
          <div className="skeleton" style={{ height: '0.875rem', width: '1rem' }} />
          <div className="skeleton" style={{ height: '0.875rem', width: '12rem' }} />
        </div>
        <SkeletonHero />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {[0, 1, 2].map(i => <SkeletonAgendaItem key={i} />)}
        </div>
      </div>
    );
  }

  // ── Fehler ───────────────────────────────────────────────
  if (error || !meeting) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        </div>
        <p className="empty-state-title">Sitzung nicht gefunden</p>
        <p className="empty-state-desc">Die gesuchte Sitzung existiert nicht oder ist nicht verfuegbar.</p>
        <Link
          href="/sitzungen"
          style={{
            marginTop: '1rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.375rem',
            padding: '0.5rem 1.25rem',
            background: '#1e3a5f',
            color: '#fff',
            borderRadius: '0.5rem',
            textDecoration: 'none',
            fontSize: '0.875rem',
            fontWeight: 600,
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Zuruck zur Ubersicht
        </Link>
      </div>
    );
  }

  // ── Daten aufbereiten ────────────────────────────────────
  const state = STATE_CONFIG[meeting.meeting_state] || {
    label: meeting.meeting_state,
    badgeClass: 'badge-slate',
    accent: '#64748b',
    dot: '#64748b',
    heroGradient: 'linear-gradient(135deg, #1e293b 0%, #64748b 100%)',
    icon: null,
  };

  const dateParts = getDateParts(meeting.start);

  const locationParts: string[] = [];
  if (meeting.location?.room) locationParts.push(meeting.location.room);
  if (meeting.location?.description) locationParts.push(meeting.location.description);
  if (meeting.location?.streetAddress) locationParts.push(meeting.location.streetAddress);
  if (meeting.location?.postalCode || meeting.location?.locality) {
    locationParts.push([meeting.location.postalCode, meeting.location.locality].filter(Boolean).join(' '));
  }
  const locationStr = locationParts.join(', ');

  const hasDocs = !!(
    meeting.invitation?.accessUrl ||
    meeting.resultsProtocol?.accessUrl ||
    meeting.verbatimProtocol?.accessUrl
  );

  const presentCount   = attendees.filter(a => a.status === 'present').length;
  const absentCount    = attendees.filter(a => a.status === 'absent').length;
  const excusedCount   = attendees.filter(a => a.status === 'excused').length;

  // ── Render ───────────────────────────────────────────────
  return (
    <div>
      {/* ── Breadcrumb ─────────────────────────────────────── */}
      <nav aria-label="Breadcrumb" style={{ marginBottom: '1.5rem' }}>
        <ol style={{
          listStyle: 'none',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '0.25rem',
          fontSize: '0.8125rem',
          color: '#64748b',
          padding: 0,
          margin: 0,
        }}>
          <li>
            <Link href="/" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 500 }}>
              Startseite
            </Link>
          </li>
          <li aria-hidden="true" style={{ color: '#cbd5e1' }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </li>
          <li>
            <Link href="/sitzungen" style={{ color: '#3b82f6', textDecoration: 'none', fontWeight: 500 }}>
              Sitzungen
            </Link>
          </li>
          <li aria-hidden="true" style={{ color: '#cbd5e1' }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </li>
          <li aria-current="page" style={{ color: '#374151', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '20rem' }}>
            {meeting.name}
          </li>
        </ol>
      </nav>

      {/* ── Hero-Banner ─────────────────────────────────────── */}
      <div
        role="banner"
        style={{
          background: state.heroGradient,
          borderRadius: '1rem',
          padding: '2rem',
          marginBottom: '2rem',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: `0 8px 32px ${state.accent}30`,
        }}
      >
        {/* Dekoratives Hintergrund-Muster */}
        <div aria-hidden="true" style={{
          position: 'absolute',
          top: '-40px',
          right: '-40px',
          width: '200px',
          height: '200px',
          borderRadius: '50%',
          background: 'rgba(255,255,255,0.05)',
          pointerEvents: 'none',
        }} />
        <div aria-hidden="true" style={{
          position: 'absolute',
          bottom: '-60px',
          right: '80px',
          width: '150px',
          height: '150px',
          borderRadius: '50%',
          background: 'rgba(255,255,255,0.04)',
          pointerEvents: 'none',
        }} />

        {/* Inhalte */}
        <div style={{ position: 'relative', zIndex: 1 }}>
          {/* Status-Badge */}
          <div style={{ marginBottom: '1rem' }}>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              background: 'rgba(255,255,255,0.18)',
              border: '1px solid rgba(255,255,255,0.3)',
              color: '#fff',
              fontSize: '0.8125rem',
              fontWeight: 600,
            }}>
              <span style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#fff',
                display: 'inline-block',
                animation: meeting.meeting_state === 'running' ? 'pulse 2s ease-in-out infinite' : 'none',
              }} aria-hidden="true" />
              {state.label}
            </span>

            {meeting.cancelled && (
              <span style={{
                marginLeft: '0.5rem',
                display: 'inline-flex',
                alignItems: 'center',
                padding: '0.25rem 0.75rem',
                borderRadius: '9999px',
                background: 'rgba(220,38,38,0.3)',
                border: '1px solid rgba(220,38,38,0.5)',
                color: '#fecaca',
                fontSize: '0.8125rem',
                fontWeight: 600,
              }}>
                Abgesagt
              </span>
            )}
          </div>

          {/* Titel */}
          <h1 style={{
            fontSize: 'clamp(1.25rem, 3vw, 1.75rem)',
            fontWeight: 800,
            color: '#fff',
            margin: '0 0 1rem',
            lineHeight: 1.2,
            letterSpacing: '-0.02em',
            maxWidth: '40rem',
          }}>
            {meeting.name}
          </h1>

          {/* Meta-Infos */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
            {/* Datum + Zeit */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.85)', fontSize: '0.9375rem' }}>
              <div style={{
                width: '2.75rem',
                height: '2.75rem',
                background: 'rgba(255,255,255,0.15)',
                borderRadius: '0.625rem',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                border: '1px solid rgba(255,255,255,0.2)',
              }}>
                <span style={{ fontSize: '1.125rem', fontWeight: 800, color: '#fff', lineHeight: 1 }}>{dateParts.day}</span>
                <span style={{ fontSize: '0.5625rem', fontWeight: 600, color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{dateParts.month}</span>
              </div>
              <div>
                <div style={{ fontWeight: 600, color: '#fff' }}>
                  {formatDate(meeting.start)}
                </div>
                <div style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.7)' }}>
                  {formatTime(meeting.start)} Uhr
                  {meeting.end && ` \u2013 ${formatTime(meeting.end)} Uhr`}
                </div>
              </div>
            </div>

            {/* Gremium */}
            {meeting.organization && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.85)' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                <Link
                  href={`/gremien/${meeting.organization.id}`}
                  style={{ color: 'rgba(255,255,255,0.9)', textDecoration: 'none', fontWeight: 500, fontSize: '0.9375rem' }}
                >
                  {meeting.organization.name}
                </Link>
              </div>
            )}

            {/* Ort */}
            {locationStr && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255,255,255,0.75)', fontSize: '0.875rem' }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                <span>{locationStr}</span>
              </div>
            )}
          </div>

          {/* Statistik-Chips */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: hasDocs ? '1.5rem' : '0' }}>
            {agendaItems.length > 0 && (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.375rem',
                padding: '0.25rem 0.75rem',
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '9999px',
                color: 'rgba(255,255,255,0.9)',
                fontSize: '0.8125rem',
                fontWeight: 500,
              }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <line x1="8" y1="6" x2="21" y2="6"/>
                  <line x1="8" y1="12" x2="21" y2="12"/>
                  <line x1="8" y1="18" x2="21" y2="18"/>
                  <line x1="3" y1="6" x2="3.01" y2="6"/>
                  <line x1="3" y1="12" x2="3.01" y2="12"/>
                  <line x1="3" y1="18" x2="3.01" y2="18"/>
                </svg>
                {agendaItems.length} Tagesordnungspunkt{agendaItems.length !== 1 ? 'e' : ''}
              </span>
            )}
            {attendees.length > 0 && (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.375rem',
                padding: '0.25rem 0.75rem',
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '9999px',
                color: 'rgba(255,255,255,0.9)',
                fontSize: '0.8125rem',
                fontWeight: 500,
              }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                {attendees.length} Teilnehmer
              </span>
            )}
          </div>

          {/* Dokumente-Links */}
          {hasDocs && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.625rem' }}>
              {meeting.invitation?.accessUrl && (
                <DocLink
                  href={meeting.invitation.accessUrl}
                  label="Einladung"
                  icon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="12" y1="18" x2="12" y2="12"/>
                      <line x1="9" y1="15" x2="15" y2="15"/>
                    </svg>
                  }
                />
              )}
              {meeting.resultsProtocol?.accessUrl && (
                <DocLink
                  href={meeting.resultsProtocol.accessUrl}
                  label="Ergebnisprotokoll"
                  icon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                      <polyline points="10 9 9 9 8 9"/>
                    </svg>
                  }
                />
              )}
              {meeting.verbatimProtocol?.accessUrl && (
                <DocLink
                  href={meeting.verbatimProtocol.accessUrl}
                  label="Wortprotokoll"
                  icon={
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                    </svg>
                  }
                />
              )}
            </div>
          )}

          {/* Livestream-Banner */}
          {meeting.meeting_state === 'running' && (
            <div style={{
              marginTop: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.625rem',
              padding: '0.75rem 1rem',
              background: 'rgba(251,191,36,0.2)',
              border: '1px solid rgba(251,191,36,0.4)',
              borderRadius: '0.625rem',
              color: '#fef3c7',
              fontSize: '0.875rem',
              fontWeight: 500,
            }} role="status">
              <span style={{ animation: 'pulse 1.5s ease-in-out infinite', display: 'flex' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="#fbbf24" stroke="#fbbf24" strokeWidth="0" aria-hidden="true">
                  <circle cx="12" cy="12" r="8"/>
                </svg>
              </span>
              Diese Sitzung findet gerade statt. Livestream-Funktion wird in einer zukunftigen Version verfugbar sein.
            </div>
          )}
        </div>
      </div>

      {/* ── Zweispaltiges Layout ─────────────────────────────── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr min(320px, 35%)',
        gap: '1.5rem',
        alignItems: 'start',
      }}>
        {/* ── Linke Spalte: Tagesordnung ─────────────────────── */}
        <section aria-labelledby="agenda-heading">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '1.25rem' }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={state.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <line x1="8" y1="6" x2="21" y2="6"/>
              <line x1="8" y1="12" x2="21" y2="12"/>
              <line x1="8" y1="18" x2="21" y2="18"/>
              <line x1="3" y1="6" x2="3.01" y2="6"/>
              <line x1="3" y1="12" x2="3.01" y2="12"/>
              <line x1="3" y1="18" x2="3.01" y2="18"/>
            </svg>
            <h2 id="agenda-heading" style={{ fontSize: '1.125rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Tagesordnung
            </h2>
            {agendaItems.length > 0 && (
              <span style={{
                padding: '0.125rem 0.5rem',
                background: '#f1f5f9',
                color: '#64748b',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}>
                {agendaItems.length}
              </span>
            )}
          </div>

          {agendaItems.length === 0 ? (
            <div className="empty-state" style={{ padding: '2.5rem 1.5rem' }}>
              <div className="empty-state-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <line x1="8" y1="6" x2="21" y2="6"/>
                  <line x1="8" y1="12" x2="21" y2="12"/>
                  <line x1="8" y1="18" x2="21" y2="18"/>
                </svg>
              </div>
              <p className="empty-state-title">Keine Tagesordnung</p>
              <p className="empty-state-desc">Fuer diese Sitzung sind keine Tagesordnungspunkte hinterlegt.</p>
            </div>
          ) : (
            /* Timeline-Layout */
            <ol style={{ listStyle: 'none', margin: 0, padding: 0 }} aria-label="Tagesordnung">
              {agendaItems.map((item, idx) => {
                const isLast = idx === agendaItems.length - 1;
                const hasResult = !!(item.result || item.resolutionText);
                const itemNum = item.number || String(item.order || idx + 1);

                return (
                  <li key={item.id} style={{ display: 'flex', gap: '0', position: 'relative' }}>
                    {/* Timeline-Connector */}
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      marginRight: '1.25rem',
                      flexShrink: 0,
                    }}>
                      {/* Nummer-Kreis */}
                      <div
                        aria-label={`TOP ${itemNum}`}
                        style={{
                          width: '2.5rem',
                          height: '2.5rem',
                          borderRadius: '50%',
                          background: hasResult ? state.accent : '#f1f5f9',
                          border: `2px solid ${hasResult ? state.accent : '#e2e8f0'}`,
                          color: hasResult ? '#fff' : '#475569',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.8125rem',
                          fontWeight: 700,
                          flexShrink: 0,
                          transition: 'all 0.2s',
                          boxShadow: hasResult ? `0 0 0 4px ${state.accent}20` : 'none',
                        }}
                      >
                        {itemNum}
                      </div>

                      {/* Verbindungslinie */}
                      {!isLast && (
                        <div style={{
                          width: '2px',
                          flex: 1,
                          minHeight: '1.5rem',
                          background: hasResult
                            ? `linear-gradient(to bottom, ${state.accent}60, #e2e8f0)`
                            : '#e2e8f0',
                          margin: '4px 0',
                        }} aria-hidden="true" />
                      )}
                    </div>

                    {/* Karten-Inhalt */}
                    <div style={{ flex: 1, paddingBottom: isLast ? 0 : '1rem' }}>
                      <div style={{
                        background: '#fff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '0.75rem',
                        padding: '1rem 1.25rem',
                        borderLeft: hasResult ? `3px solid ${state.accent}` : '3px solid #e2e8f0',
                        transition: 'box-shadow 0.2s',
                      }}
                        onMouseEnter={e => {
                          (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 12px rgba(0,0,0,0.06)';
                        }}
                        onMouseLeave={e => {
                          (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                        }}
                      >
                        {/* TOP-Header */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.375rem' }}>
                          <h3 style={{
                            fontSize: '0.9375rem',
                            fontWeight: 600,
                            color: '#0f172a',
                            margin: 0,
                            lineHeight: 1.4,
                          }}>
                            {item.name}
                          </h3>
                          <div style={{ display: 'flex', gap: '0.375rem', flexShrink: 0 }}>
                            {!item.public && (
                              <span style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.25rem',
                                padding: '0.125rem 0.5rem',
                                background: '#fee2e2',
                                color: '#991b1b',
                                borderRadius: '9999px',
                                fontSize: '0.6875rem',
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em',
                              }}>
                                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                                </svg>
                                Nichtoeffentlich
                              </span>
                            )}
                            {hasResult && (
                              <span style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.25rem',
                                padding: '0.125rem 0.5rem',
                                background: `${state.accent}15`,
                                color: state.accent,
                                borderRadius: '9999px',
                                fontSize: '0.6875rem',
                                fontWeight: 700,
                              }}>
                                <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                                  <polyline points="20 6 9 17 4 12"/>
                                </svg>
                                Beschlossen
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Verlinktes Vorlage-Dokument */}
                        {item.consultation?.paper && (
                          <div style={{ marginBottom: '0.625rem' }}>
                            <Link
                              href={`/vorlagen/${item.consultation.paper.id}`}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.375rem',
                                color: '#2563eb',
                                textDecoration: 'none',
                                fontSize: '0.8125rem',
                                fontWeight: 500,
                              }}
                            >
                              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                <polyline points="14 2 14 8 20 8"/>
                              </svg>
                              {item.consultation.paper.reference}: {item.consultation.paper.name}
                            </Link>
                          </div>
                        )}

                        {/* Ergebnis */}
                        {item.result && (
                          <div style={{
                            padding: '0.5rem 0.75rem',
                            background: '#f0fdf4',
                            border: '1px solid #bbf7d0',
                            borderRadius: '0.5rem',
                            fontSize: '0.8125rem',
                            color: '#166534',
                            marginBottom: item.resolutionText ? '0.5rem' : 0,
                          }}>
                            <span style={{ fontWeight: 700 }}>Ergebnis: </span>{item.result}
                          </div>
                        )}

                        {/* Beschlusstext */}
                        {item.resolutionText && (
                          <div style={{
                            padding: '0.5rem 0.75rem',
                            background: '#f8fafc',
                            border: '1px solid #e2e8f0',
                            borderRadius: '0.5rem',
                            fontSize: '0.8125rem',
                            color: '#374151',
                            lineHeight: 1.6,
                          }}>
                            <span style={{ fontWeight: 700 }}>Beschluss: </span>{item.resolutionText}
                          </div>
                        )}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
        </section>

        {/* ── Rechte Spalte: Sidebar ──────────────────────────── */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Anwesenheitsstatistik */}
          {attendees.length > 0 && (
            <section aria-labelledby="attendees-heading">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={state.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                <h2 id="attendees-heading" style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                  Anwesenheit
                </h2>
                <span style={{
                  padding: '0.125rem 0.5rem',
                  background: '#f1f5f9',
                  color: '#64748b',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                }}>{attendees.length}</span>
              </div>

              {/* Statistik-Balken */}
              {(presentCount > 0 || absentCount > 0 || excusedCount > 0) && (
                <div style={{
                  background: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '0.75rem',
                  padding: '1rem',
                  marginBottom: '0.875rem',
                }}>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    {/* Fortschrittsbalken */}
                    <div style={{
                      height: '6px',
                      borderRadius: '9999px',
                      overflow: 'hidden',
                      background: '#f1f5f9',
                      flex: 1,
                      display: 'flex',
                    }}>
                      {presentCount > 0 && (
                        <div style={{ width: `${(presentCount / attendees.length) * 100}%`, background: '#059669' }} aria-hidden="true" />
                      )}
                      {excusedCount > 0 && (
                        <div style={{ width: `${(excusedCount / attendees.length) * 100}%`, background: '#d97706' }} aria-hidden="true" />
                      )}
                      {absentCount > 0 && (
                        <div style={{ width: `${(absentCount / attendees.length) * 100}%`, background: '#dc2626' }} aria-hidden="true" />
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    {[
                      { count: presentCount,  label: 'Anwesend',     color: '#059669', bg: '#d1fae5' },
                      { count: excusedCount,  label: 'Entschuldigt', color: '#d97706', bg: '#fef3c7' },
                      { count: absentCount,   label: 'Abwesend',     color: '#dc2626', bg: '#fee2e2' },
                    ].filter(s => s.count > 0).map(s => (
                      <div key={s.label} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.8125rem' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: s.color, flexShrink: 0 }} aria-hidden="true" />
                        <span style={{ fontWeight: 700, color: s.color }}>{s.count}</span>
                        <span style={{ color: '#64748b' }}>{s.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Teilnehmerliste */}
              <div style={{
                background: '#fff',
                border: '1px solid #e2e8f0',
                borderRadius: '0.75rem',
                overflow: 'hidden',
                maxHeight: '24rem',
                overflowY: 'auto',
              }}>
                <ul style={{ listStyle: 'none', margin: 0, padding: 0 }} aria-label="Teilnehmerliste">
                  {attendees.map((a, idx) => {
                    const statusConf = ATTENDEE_STATUS[a.status] || { label: a.status, color: '#64748b', bg: '#f1f5f9' };
                    return (
                      <li
                        key={a.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.625rem 1rem',
                          borderBottom: idx < attendees.length - 1 ? '1px solid #f1f5f9' : 'none',
                          gap: '0.5rem',
                        }}
                      >
                        <Link
                          href={`/personen/${a.personId}`}
                          style={{
                            color: '#1e293b',
                            textDecoration: 'none',
                            fontSize: '0.875rem',
                            fontWeight: 500,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {a.personName}
                        </Link>
                        <span style={{
                          padding: '0.125rem 0.5rem',
                          borderRadius: '9999px',
                          background: statusConf.bg,
                          color: statusConf.color,
                          fontSize: '0.6875rem',
                          fontWeight: 700,
                          flexShrink: 0,
                        }}>
                          {statusConf.label}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </section>
          )}

          {/* Leerer Attendees-State */}
          {attendees.length === 0 && (
            <section aria-labelledby="attendees-empty-heading">
              <h2 id="attendees-empty-heading" style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>
                Anwesenheit
              </h2>
              <div style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '0.75rem',
                padding: '1.5rem',
                textAlign: 'center',
                color: '#94a3b8',
                fontSize: '0.875rem',
              }}>
                Keine Anwesenheitsdaten vorhanden.
              </div>
            </section>
          )}
        </aside>
      </div>

      {/* Responsive: Mobile-Stil fuer schmale Viewports */}
      <style>{`
        @media (max-width: 768px) {
          div[style*="grid-template-columns"] {
            display: flex !important;
            flex-direction: column !important;
          }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}
