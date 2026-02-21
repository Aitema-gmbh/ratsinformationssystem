import type { Metadata, Viewport } from 'next';
import Script from 'next/script';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'aitema|RIS — Ratsinformationssystem',
    template: '%s | aitema|RIS',
  },
  description: 'Offenes Ratsinformationssystem für deutsche Kommunen — OParl 1.1 kompatibel. Transparente kommunale Demokratie.',
  keywords: ['RIS', 'Ratsinformationssystem', 'OParl', 'Kommune', 'Gemeinderat', 'Open Data', 'Sitzungen', 'Vorlagen'],
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'aitema|RIS',
  },
  openGraph: {
    type: 'website',
    locale: 'de_DE',
    siteName: 'aitema|RIS',
  },
};

export const viewport: Viewport = {
  themeColor: '#0f172a',
  width: 'device-width',
  initialScale: 1,
};

const navLinks = [
  {
    href: '/sitzungen',
    label: 'Sitzungen',
    ariaLabel: 'Sitzungen anzeigen',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
    ),
  },
  {
    href: '/vorlagen',
    label: 'Vorlagen',
    ariaLabel: 'Vorlagen anzeigen',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
      </svg>
    ),
  },
  {
    href: '/personen',
    label: 'Personen',
    ariaLabel: 'Personen anzeigen',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
    ),
  },
  {
    href: '/gremien',
    label: 'Gremien',
    ariaLabel: 'Gremien anzeigen',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
      </svg>
    ),
  },
  {
    href: '/kalender',
    label: 'Kalender',
    ariaLabel: 'Kalenderansicht öffnen',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
        <rect x="8" y="14" width="3" height="3" rx="0.5"/>
      </svg>
    ),
  },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* Accessibility: Skip Navigation */}
        <a href="#main-content" className="skip-link">
          Zum Hauptinhalt springen
        </a>

        {/* ── Navigation Header ────────────────────── */}
        <header className="site-header" role="banner">
          <nav className="main-nav" id="main-navigation" aria-label="Hauptnavigation">

            {/* Brand / Logo */}
            <div className="nav-brand">
              <a href="/" aria-label="aitema|RIS — zur Startseite">
                <div className="nav-brand-logo" aria-hidden="true">
                  {/* Stylized "aR" monogram */}
                  <span style={{ fontSize: '0.875rem', fontWeight: 800, letterSpacing: '-0.08em', fontFamily: 'inherit' }}>aR</span>
                </div>
                <div className="nav-brand-text">
                  <span className="nav-brand-name">
                    aitema|<span className="accent">RIS</span>
                  </span>
                  <span className="nav-brand-tagline">
                    Ratsinformationssystem
                    <span className="nav-oparl-badge" aria-label="OParl Version 1.1">OParl 1.1</span>
                  </span>
                </div>
              </a>
            </div>

            {/* Main Navigation Links */}
            <ul className="nav-links" role="list">
              {navLinks.map(({ href, label, ariaLabel, icon }) => (
                <li key={href}>
                  <a href={href} aria-label={ariaLabel}>
                    {icon}
                    {label}
                  </a>
                </li>
              ))}
            </ul>

            {/* Search CTA Button */}
            <a
              href="/suche"
              className="nav-search-btn"
              aria-label="Volltextsuche öffnen"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <span>Suche</span>
              {/* Keyboard shortcut hint */}
              <kbd style={{
                fontSize: '0.6875rem',
                padding: '0.1rem 0.375rem',
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: '4px',
                fontFamily: 'inherit',
                letterSpacing: '0',
                lineHeight: '1.4',
                display: 'flex',
                alignItems: 'center',
                color: 'rgba(255,255,255,0.6)',
              }} aria-hidden="true">/</kbd>
            </a>
          </nav>
        </header>

        {/* ── Main Content ─────────────────────────── */}
        <main id="main-content" role="main" tabIndex={-1}>
          {children}
        </main>

        {/* ── Footer ───────────────────────────────── */}
        <footer className="site-footer" role="contentinfo">
          <div className="footer-content">
            <div className="footer-brand">
              <strong>aitema|RIS</strong>
              <span>OParl 1.1 kompatibel &bull; Open Data für Kommunen</span>
              <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.35)', marginTop: '2px' }}>
                Transparente kommunale Demokratie
              </span>
            </div>
            <nav className="footer-nav" aria-label="Footer-Navigation">
              <a href="/suche">Suche</a>
              <a href="/kalender">Kalender</a>
              <a href="/oparl">OParl API</a>
              <a href="/impressum">Impressum</a>
              <a href="/datenschutz">Datenschutz</a>
              <a href="/barrierefreiheit">Barrierefreiheit</a>
            </nav>
          </div>
        </footer>

        {/* ── PWA Service Worker ───────────────────── */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').catch(function() {});
                });
              }
              /* Keyboard shortcut: press "/" to focus search */
              document.addEventListener('keydown', function(e) {
                if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                  e.preventDefault();
                  window.location.href = '/suche';
                }
              });
            `,
          }}
        />
      {/* M1: Plausible Analytics - cookiefrei, DSGVO-konform */}
        <Script
          defer
          data-domain="ris.aitema.de"
          src="https://plausible.io/js/script.js"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
