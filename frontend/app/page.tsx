import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'aitema|RIS — Ratsinformationssystem',
  description: 'Ihr offenes Ratsinformationssystem für transparente kommunale Demokratie. OParl 1.1 kompatibel.',
};

const quickLinks = [
  {
    href: '/sitzungen',
    title: 'Sitzungen',
    desc: 'Geplante und vergangene Sitzungen aller Gremien',
    bg: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
    iconBg: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
    iconColor: '#1e40af',
    icon: 'calendar',
  },
  {
    href: '/vorlagen',
    title: 'Vorlagen & Drucksachen',
    desc: 'Beschlussvorlagen, Anträge und Berichte',
    iconBg: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
    iconColor: '#92400e',
    icon: 'file',
  },
  {
    href: '/personen',
    title: 'Personen',
    desc: 'Ratsmitglieder, Bürgermeister und Verwaltung',
    iconBg: 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)',
    iconColor: '#065f46',
    icon: 'users',
  },
  {
    href: '/gremien',
    title: 'Gremien',
    desc: 'Ausschüsse, Fraktionen und Räte',
    iconBg: 'linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%)',
    iconColor: '#5b21b6',
    icon: 'building',
  },
  {
    href: '/kalender',
    title: 'Kalender',
    desc: 'Alle Termine im Monats- und Wochenblick',
    iconBg: 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)',
    iconColor: '#991b1b',
    icon: 'cal-check',
  },
  {
    href: '/suche',
    title: 'Volltextsuche',
    desc: 'Alle Inhalte durchsuchen und filtern',
    iconBg: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)',
    iconColor: '#0369a1',
    icon: 'search',
  },
];

function QuickLinkIcon({ type, color }: { type: string; color: string }) {
  const props = {
    width: 24, height: 24, viewBox: '0 0 24 24', fill: 'none',
    stroke: color, strokeWidth: 2, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const,
  };
  switch (type) {
    case 'calendar': return (
      <svg {...props}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
    );
    case 'file': return (
      <svg {...props}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
    );
    case 'users': return (
      <svg {...props}><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
    );
    case 'building': return (
      <svg {...props}><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
    );
    case 'cal-check': return (
      <svg {...props}><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><polyline points="9 16 11 18 15 14"/></svg>
    );
    case 'search': return (
      <svg {...props}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    );
    default: return null;
  }
}

export default function HomePage() {
  return (
    <div>
      {/* ── Hero Section ── */}
      <section
        className="aitema-hero"
        style={{ borderRadius: '1rem', marginBottom: '2.5rem' }}
        aria-labelledby="hero-heading"
      >
        <div style={{ position: 'relative', zIndex: 10, maxWidth: '640px' }}>
          {/* OParl Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.375rem 0.875rem',
            background: 'rgba(59,130,246,0.2)',
            border: '1px solid rgba(59,130,246,0.35)',
            borderRadius: '9999px',
            fontSize: '0.8125rem',
            fontWeight: 600,
            color: '#93c5fd',
            letterSpacing: '0.02em',
            marginBottom: '1.25rem',
          }}>
            <span style={{ width: '6px', height: '6px', background: '#60a5fa', borderRadius: '50%', display: 'inline-block' }} aria-hidden="true" />
            OParl 1.1 kompatibel
          </div>

          <h1 id="hero-heading" style={{
            fontSize: 'clamp(1.75rem, 4vw, 2.5rem)',
            fontWeight: 900,
            color: '#fff',
            letterSpacing: '-0.04em',
            lineHeight: 1.1,
            marginBottom: '1rem',
          }}>
            Transparente<br />
            <span style={{
              background: 'linear-gradient(135deg, #60a5fa, #a78bfa)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              Kommunal&shy;demokratie
            </span>
          </h1>

          <p style={{
            fontSize: '1.0625rem',
            color: 'rgba(255,255,255,0.75)',
            lineHeight: 1.65,
            marginBottom: '2rem',
            maxWidth: '480px',
          }}>
            Ihr offenes Ratsinformationssystem mit Zugang zu allen Sitzungen,
            Vorlagen und Beschlüssen Ihrer Gemeinde.
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <Link
              href="/suche"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                color: '#fff',
                textDecoration: 'none',
                borderRadius: '0.625rem',
                fontWeight: 700,
                fontSize: '0.9375rem',
                boxShadow: '0 4px 16px rgba(59,130,246,0.45)',
                letterSpacing: '-0.01em',
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              Jetzt suchen
            </Link>
            <Link
              href="/sitzungen"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                background: 'rgba(255,255,255,0.1)',
                color: '#fff',
                textDecoration: 'none',
                borderRadius: '0.625rem',
                fontWeight: 600,
                fontSize: '0.9375rem',
                border: '1px solid rgba(255,255,255,0.2)',
                letterSpacing: '-0.01em',
              }}
            >
              Kommende Sitzungen
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* ── Quick Access Grid ── */}
      <section aria-labelledby="quicklinks-heading">
        <h2
          id="quicklinks-heading"
          style={{
            fontSize: '1.375rem',
            fontWeight: 800,
            color: '#0f172a',
            letterSpacing: '-0.03em',
            marginBottom: '1.25rem',
          }}
        >
          Schnellzugriff
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1rem',
        }}>
          {quickLinks.map(({ href, title, desc, iconBg, iconColor, icon }) => (
            <Link
              key={href}
              href={href}
              className="aitema-card aitema-card-link"
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '1rem',
                textDecoration: 'none',
                color: 'inherit',
              }}
            >
              {/* Icon */}
              <div style={{
                width: '48px',
                height: '48px',
                background: iconBg,
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }} aria-hidden="true">
                <QuickLinkIcon type={icon} color={iconColor} />
              </div>

              {/* Text */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: '0.9375rem',
                  fontWeight: 700,
                  color: '#0f172a',
                  letterSpacing: '-0.02em',
                  marginBottom: '0.25rem',
                }}>
                  {title}
                </div>
                <div style={{
                  fontSize: '0.8125rem',
                  color: '#64748b',
                  lineHeight: 1.5,
                }}>
                  {desc}
                </div>
              </div>

              {/* Arrow */}
              <svg
                width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                aria-hidden="true"
                style={{ flexShrink: 0, marginTop: '0.375rem' }}
              >
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </Link>
          ))}
        </div>
      </section>

      {/* ── Info Banner ── */}
      <section
        aria-labelledby="oparl-info-heading"
        style={{
          marginTop: '3rem',
          padding: '2rem',
          background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
          border: '1px solid #bae6fd',
          borderRadius: '1rem',
        }}
      >
        <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div style={{
            width: '48px', height: '48px',
            background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
            borderRadius: '12px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
            boxShadow: '0 4px 12px rgba(59,130,246,0.3)',
          }} aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h2 id="oparl-info-heading" style={{ fontSize: '1.0625rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem', letterSpacing: '-0.02em' }}>
              OParl-konforme Open-Data-Plattform
            </h2>
            <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.65, marginBottom: '1rem' }}>
              Alle Daten stehen als maschinenlesbare OParl-API zur Verfügung. Entwickler können die Daten
              für eigene Anwendungen nutzen. Das System folgt dem OParl-Standard Version 1.1.
            </p>
            <Link
              href="/oparl"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.375rem',
                color: '#2563eb',
                textDecoration: 'none',
                fontWeight: 600,
                fontSize: '0.875rem',
              }}
            >
              Zur OParl API-Dokumentation
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
